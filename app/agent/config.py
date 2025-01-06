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


def generate_system_prompt() -> dict:
    """
    Generates the system prompt to guide the assistant's response to the customer.
    The assistant decides whether to make a function call based on the user's query.
    If the query requires an API document, it triggers the function call.
    If the query does not require an API search, it directly responds to the user.

    :return: The system prompt as a dictionary.
    """
    system_prompt_content = """
    You run in a loop of Thought, Action, PAUSE, Action_Response.

    At the end of the loop you output an Answer.

    Use Thought to understand the question you have been asked.
    Use Action to determine if the query requires an API document search or if the response can be directly given.
    - If the query requires the Crustdata API documentation, trigger a function call with the user's query to search for relevant API details.
    - If the query does not require an API search, respond directly to the user with the relevant information.
    
    Action_Response will be either the result of the function call (the API document) or a direct answer to the user's question.

    Your response should focus solely on Crustdata API guidance or the appropriate response to the user's query. 
    Stay humble and don't engage in anything beyond the subject of Crustdata APIs.
    Always provide the response in a format suitable for the user to copy-paste into their terminal.
    """

    return {"role": "system", "content": system_prompt_content}
