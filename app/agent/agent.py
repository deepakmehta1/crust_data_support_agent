# app/agent/agent.py
import inspect
from datetime import datetime, timezone
from openai import OpenAI
import json
from app.models.conversation import Message
from .config import OPENAI_API_KEY, MODEL_NAME
from app.services.conversation import ConversationService
from tools.tools import (
    get_tools,
    get_tool_schemas,
)
from typing import List, Tuple, Optional, Dict

from pydantic import BaseModel


class OpenAIResponse(BaseModel):
    content: (
        str  # The content of the response, which can be a message from the assistant.
    )
    show_to_user: (
        bool  # A boolean that decides whether the content should be shown to the user.
    )


class Agent:
    def __init__(
        self,
        system_prompt: dict,
        conversation_id: str,
        conversation_service: ConversationService,
        tools: Dict[str, callable] = get_tools(),
    ) -> None:
        self.client = OpenAI(api_key=OPENAI_API_KEY)
        self.system_prompt = system_prompt
        self.conversation_service = conversation_service
        self.tools = tools
        self.conversation = conversation_service.get_conversation(conversation_id)

    def __get_messages(self) -> List[dict]:
        """
        Retrieves the list of messages from the system prompt and memory.

        Returns:
            List of messages to send to the LLM (Large Language Model).
        """
        # Retrieve the conversation from the conversation service
        conversation_data = self.conversation_service.get_conversation()

        # Parse the conversation into a list of messages with role and content
        messages = [
            {"role": message.role, "content": message.content}
            for message in conversation_data["messages"]
        ]

        # Include the system prompt as the starting message
        return [{"role": "system", "content": self.system_prompt["content"]}] + messages

    def __build_message(self, role: str, content: str, name: str = None) -> Message:
        """
        Builds a message object from the role and content provided.

        Args:
            role (str): The role of the sender (user or assistant).
            content (str): The message content.
            name (str, optional): The name of the function if it's a function call. Defaults to None.

        Returns:
            Message: A Pydantic Message object containing the formatted message details.
        """
        return Message(
            role=role,
            content=content,
            status="message_sent",
            timestamp=datetime.now(timezone.utc),
        )

    def call_llm(self) -> Tuple[Optional[str], str]:
        """
        Calls the LLM (Large Language Model) API and processes the response.

        Returns:
            - assistant_message: The assistant's message content or None.
            - message_type: The type of message ('tools' or 'assistant').
        """
        try:
            # Send request to LLM with messages and tools
            response = self.client.beta.chat.completions.parse(
                model=MODEL_NAME,
                messages=self.__get_messages(),
                temperature=0,
                max_tokens=1000,
                n=1,
                stop=None,
                tools=get_tool_schemas(),
                response_format=OpenAIResponse,
            )

            assistant_message = response.choices[0].message.parsed
            message_type = "assistant"  # Default to assistant response

            # Access tool_calls correctly if any exist
            tool_calls = response.choices[0].message.tool_calls
            if tool_calls:
                message_type = "tools"  # If there are tool calls, it's a tool message
                for tool_call in tool_calls:
                    # Print tool call details for debugging
                    print(f"Tool ID: {tool_call.id}")
                    print(f"Tool Name: {tool_call.function.name}")
                    print(f"Arguments: {tool_call.function.arguments}")

                    # Process tool call arguments
                    tool_name = tool_call.function.name
                    args_str = (
                        tool_call.function.arguments
                    )  # String representing tool arguments
                    try:
                        args = json.loads(
                            args_str
                        )  # Parse the arguments string into a dictionary
                    except json.JSONDecodeError:
                        args = {}  # Default to empty dictionary if parsing fails
                        print(
                            f"Error parsing arguments for tool {tool_name}: {args_str}"
                        )

                    # Dynamically map arguments to the function's signature
                    if isinstance(args, dict):
                        func = self.tools.get(tool_name)
                        if func:
                            signature = inspect.signature(
                                func
                            )  # Get the function signature
                            bound_args = signature.bind(
                                self.db_connector, **args
                            )  # Bind arguments to the function signature
                            bound_args.apply_defaults()  # Apply default values for missing arguments
                            args = list(
                                bound_args.arguments.values()
                            )  # Convert to a list for function call

                    # Execute the tool based on the mapped arguments
                    result = self.execute_tool(tool_name, args)
                    print(f"Tool result: {result}")
                    result_string = f"Tool result for {args_str}: {result}"

                    # Send the tool result back to the model if it is a tool call
                    self.conversation_service.store_message(
                        self.conversation,
                        self.__build_message(
                            "function", result_string, tool_call.function.name
                        ),
                    )

            return (
                assistant_message,
                message_type,
            )

        except Exception as e:
            print(f"Error calling OpenAI API: {e}")
            return None, None  # Return None if an error occurs

    def execute_tool(self, tool: str, args: List) -> str:
        """
        Executes the tool based on the provided name and arguments.

        Args:
            tool: The tool's name to execute (e.g., 'add', 'multiply').
            args: The arguments for the tool.

        Returns:
            - result: The result of executing the tool as a string.
        """
        func = self.tools.get(tool)
        if func:
            try:
                result = func(*args)
                return result
            except Exception as e:
                return f"Error executing tool '{tool}': {e}"
        return f"Tool '{tool}' not found."

    def interact(self, user_input: str) -> str:
        """
        Processes the user's input, interacts with the assistant, and manages tool calls.

        Args:
            user_input: The input message from the user.

        Returns:
            - The final assistant message or tool result.
        """
        self.conversation_service.store_message(
            self.conversation, self.__build_message("user", user_input)
        )

        while True:
            assistant_response, message_type = self.call_llm()  # Call the LLM

            if message_type == "tools":
                # If it's a tool call, process it and send the result back to the model
                print(f"Processing tool call: {assistant_response}")
                # Store the tool result in memory (this is optional)
            else:
                # If it's the assistant's final response, return it to the user
                print(f"Internal processing: {assistant_response}")
                self.conversation_service.store_message(
                    self.conversation,
                    self.__build_message("assistant", assistant_response.content),
                )
                if (
                    assistant_response.show_to_user
                ):  # Only return the result if show_to_user is True
                    return assistant_response.content
