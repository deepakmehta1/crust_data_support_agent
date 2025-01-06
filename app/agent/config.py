import os
from dotenv import load_dotenv

# Load environment variables from .env file
load_dotenv()

# Retrieve OpenAI API key from environment variables
OPENAI_API_KEY = os.getenv("OPENAI_API_KEY")

if not OPENAI_API_KEY:
    raise ValueError(
        "OPENAI_API_KEY not found in environment variables. Please set it in the .env file."
    )

# Model configuration
MODEL_NAME = "gpt-4o-2024-08-06"  # Ensure you have access to this model


def generate_system_prompt(knowledge_base: dict) -> dict:
    """
    Generates the system prompt to guide the assistant's response to the customer,
    including knowledge base information for accurate Crustdata API guidance, and the agentic loop.

    :param knowledge_base: The knowledge base result to be used in the prompt.
    :return: The system prompt as a dictionary.
    """
    knowledge_base_description = f"""
    Here is the relevant information from the Crustdata API:
    - Name: {knowledge_base.get('name')}
    - Description: {knowledge_base.get('description')}
    - Data: {knowledge_base.get('data', 'No additional data available')}
    - Response: {knowledge_base.get('response')}
    
    Your task is to help the customer use the appropriate Crustdata API based on this information.
    Respond in a humble, clear, and concise manner, only providing relevant information about Crustdata APIs.
    """

    system_prompt_content = f"""
    You run in a loop of Thought, Action, PAUSE, Action_Response.

    At the end of the loop you output an Answer.

    Use Thought to understand the question you have been asked. 
    Use Action to identify the appropriate Crustdata API based on the question and knowledge base information.
    Break the question down into relevant steps, like selecting the correct API endpoint and preparing the request.
    Then, return PAUSE to signify the pause after gathering the necessary API information.

    Action_Response will be the structured response to the customer, in a format suitable for copy-pasting in the terminal (either in `curl` or Python `requests`).

    Knowledge Base Details:
    {knowledge_base_description}

    Your response should focus solely on Crustdata API guidance, providing detailed and structured responses based on the knowledge base.
    Stay humble and don't engage in anything beyond the subject of Crustdata APIs.
    Always provide the response in a way that the user can simply copy and paste it into their terminal.
    """

    return {"role": "system", "content": system_prompt_content}
