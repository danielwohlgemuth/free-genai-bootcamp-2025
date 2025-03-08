import os
from database import store_chat_interaction, retrieve_chat_history, update_haiku_lines, retrieve_haiku_line
from workflow import start_workflow
from langchain_core.tools import InjectedToolArg, tool
from langchain_ollama import OllamaLLM
from typing import Annotated
from typing import List


MODEL_NAME = os.getenv("OLLAMA_MODEL", "qwen2.5:7b")
model = OllamaLLM(model=MODEL_NAME)


@tool
async def start_media_generation(haiku_id: Annotated[str, InjectedToolArg]):
    """Start haiku media generation from haiku.

    Args:
        haiku_id: Haiku ID.
    """
    start_workflow(haiku_id)
    return f"Haiku media generation started"

@tool(parse_docstring=True)
def update_haiku(haiku: List[str], haiku_id: Annotated[str, InjectedToolArg]) -> str:
    """Update haiku in database.

    Args:
        haiku: Haiku with each line as a separate string.
        haiku_id: Haiku ID.
    """
    update_haiku_lines(haiku_id, haiku)
    return f"Haiku updated in database"

def process_message(haiku_id: str, user_message: str):
    store_chat_interaction(haiku_id, user_message, 'user')
    prompt = create_prompt(haiku_id, user_message)
    agent_message = model.invoke(prompt)
    store_chat_interaction(haiku_id, agent_message, 'agent')

def create_prompt(haiku_id: str, user_message: str):
    chat_history = retrieve_chat_history(haiku_id)
    prompt = ''
    for chat in chat_history:
        prompt += f'{chat["role"]}: {chat["message"]}\n'
    prompt += f'user: {user_message}\n'
    prompt += 'Generate a single haiku with three lines based on the above conversation.'
    return prompt
