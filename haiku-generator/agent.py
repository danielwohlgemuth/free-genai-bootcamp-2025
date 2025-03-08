import langchain
import os
from database import store_chat_interaction, retrieve_chat_history, update_haiku_lines, retrieve_haiku_line
from dotenv import load_dotenv
from langchain_core.prompts import PromptTemplate
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

def get_tools():
    return [update_haiku, start_media_generation]

def get_tool_names():
    return [tool.name for tool in get_tools()]

def create_agent():
    template="""You are an assistant that helps generate haikus.

    A haiku is a traditional Japanese poem with the following format:
    - Three lines
    - Syllable pattern:
        - 5 syllables in the first line
        - 7 syllables in the second line
        - 5 syllables in the third line

    If the user provides a haiku or you generate one, save it in the database.
    Once the user confirms that the haiku is correct, start the media generation process.

    Tools:
    {tools}

    Tool names:
    {tool_names}

    {agent_scratchpad}

    {input}
    """

    prompt = PromptTemplate.from_template(template, partial_variables={"tools": get_tools(), "tool_names": get_tool_names()})

    agent = create_react_agent(model, tools=get_tools(), prompt=prompt)


agent = create_agent()


def process_message(haiku_id: str, user_message: str):
    store_chat_interaction(haiku_id, user_message, 'user')

    chat_history = retrieve_chat_history(haiku_id)
    messages = 'Chat history:\n'
    for chat in chat_history:
        messages += f'{chat["role"]}: {chat["message"]}\n'
    messages += f'user: {user_message}\n'

    inputs = {
        "haiku_id": haiku_id,
        "input": messages
    }

    agent_message = agent.invoke(inputs)

    store_chat_interaction(haiku_id, agent_message, 'agent')
