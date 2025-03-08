import os
from database import store_chat_interaction, retrieve_chat_history, update_haiku_lines, retrieve_haiku_line
from workflow import define_workflow
from langchain_core.tools import InjectedToolArg, tool
from langchain_ollama import OllamaLLM
from typing import Annotated
from typing import List


MODEL_NAME = os.getenv("OLLAMA_MODEL", "qwen2.5:7b")
model = OllamaLLM(model=MODEL_NAME)
workflow = define_workflow()


@tool
async def start_media_generation(haiku_id: Annotated[str, InjectedToolArg]):
    """Start haiku media generation from haiku.

    Args:
        haiku_id: Haiku ID.
    """
    workflow.invoke({"haiku_id": haiku_id})
    return f"Haiku media generation started"

@tool(parse_docstring=True)
def update_haiku(haiku: List[str], haiku_id: Annotated[str, InjectedToolArg]) -> str:
    """Update haiku in database.

    Args:
        haiku: Haiku with each line as a separate string.
        haiku_id: Haiku ID.
    """
    update_haiku_lines(haiku, haiku_id)
    return f"Haiku updated in database"

def process_message(user_message: str, haiku_id: str):
    store_chat_interaction(haiku_id, user_message, 'user')
    chat_history = retrieve_chat_history(haiku_id)
    prompt = create_prompt(user_message, chat_history)
    agent_message = model.invoke(prompt)
    store_chat_interaction(haiku_id, agent_message, 'agent')

def create_prompt(user_message: str, chat_history: list):
    prompt = f'User: {user_message}\n'
    for entry in chat_history:
        user_msg, response = entry
        prompt += f'User: {user_msg}\nBot: {response}\n'
    prompt += 'Generate a single haiku with three lines based on the above conversation.'
    return prompt
