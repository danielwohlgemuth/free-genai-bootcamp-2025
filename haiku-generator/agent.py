import langchain
import os
from database import store_chat_interaction, retrieve_chat_history, update_haiku_lines, retrieve_haiku_line
from dotenv import load_dotenv
from langchain_core.runnables import RunnableConfig
from langchain_core.tools import InjectedToolArg, tool
from langchain_ollama import ChatOllama
from langgraph.prebuilt.chat_agent_executor import create_react_agent
from typing import Annotated
from typing import List
from workflow import start_workflow


langchain.debug = True


load_dotenv()
MODEL_BASE_URL = os.getenv("MODEL_BASE_URL", "http://localhost:11434")
MODEL_NAME = os.getenv("MODEL_NAME", "qwen2.5:7b")
model = ChatOllama(
    base_url=MODEL_BASE_URL,
    model=MODEL_NAME
)

system_template="""You are an assistant that helps generate haikus.

A haiku is a traditional Japanese poem with the following format:
- Three lines
- Syllable pattern:
    - 5 syllables in the first line
    - 7 syllables in the second line
    - 5 syllables in the third line

If the user provides a haiku or you generate one, save it in the database.
Once the user confirms that the haiku is correct, start the media generation process.
"""

@tool
async def start_media_generation(config: RunnableConfig) -> str:
    """Start haiku media generation from haiku."""
    haiku_id = config.get("configurable", {}).get("haiku_id")
    start_workflow(haiku_id)
    return f"Haiku media generation started"

@tool
def update_haiku(haiku: List[str], config: RunnableConfig) -> str:
    """Update haiku in database."""
    haiku_id = config.get("configurable", {}).get("haiku_id")
    update_haiku_lines(haiku_id, haiku)
    return f"Haiku updated in database"

def get_tools():
    return [update_haiku, start_media_generation]

def get_tool_names():
    return [tool.name for tool in get_tools()]

def create_agent():
    agent_model = create_react_agent(model, tools=get_tools())
    return agent_model


agent_model = create_agent()


def process_message(haiku_id: str, user_message: str):
    store_chat_interaction(haiku_id, user_message, 'human')

    chat_history = retrieve_chat_history(haiku_id)
    messages = [('system', system_template)]
    for chat in chat_history:
        messages.append((chat["role"], chat["message"]))

    inputs = {
        "messages": messages,
        "configurable": {
            "haiku_id": haiku_id
        }
    }

    agent_message = agent_model.invoke(inputs)
    print('agent_message', agent_message)

    store_chat_interaction(haiku_id, agent_message["messages"][-1].content, 'ai')
