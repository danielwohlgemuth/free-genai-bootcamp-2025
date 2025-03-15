import langchain
import os
from database import store_chat_interaction, retrieve_chats, update_haiku_lines, retrieve_haiku
from dotenv import load_dotenv
from langchain_core.prompts import ChatPromptTemplate
from langchain_core.tools import tool
from langchain_ollama import ChatOllama
from langchain.agents import create_tool_calling_agent, AgentExecutor
from model import UpdateHaiku
from pydantic import BaseModel, Field
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

The haiku should be in English.

If the user provides a haiku or you generate one, save it to the database.
Once the user confirms that the haiku is good, generate the media.
Once media is generated, the interaction is complete. Don't ask for more input.

Pass this haiku id to the tools: {haiku_id}. The haiku id is a string and is for internal use only. Don't expose it to the user.
Pass the haiku as a list of three strings to the tool.
"""


@tool
def generate_media(haiku_id: str | int) -> str:
    """Generate haiku media."""
    haiku = retrieve_haiku(str(haiku_id))
    if not haiku.haiku_line_en_1 or not haiku.haiku_line_en_2 or not haiku.haiku_line_en_3:
        return f"Haiku not available for media generation. Please save a haiku first."    
    start_workflow(str(haiku_id))
    return f"Media generated"

@tool("update_haiku", args_schema=UpdateHaiku)
def update_haiku(haiku: List[str], haiku_id: str | int, topic: str) -> str:
    """Update haiku in database."""
    if len(haiku) != 3:
        return "Invalid haiku format. Please provide 3 lines."
    if not topic:
        return "Invalid haiku format. Please provide a topic."
    update_haiku_lines(str(haiku_id), haiku, topic)
    return "Haiku updated in database"

def get_tools():
    return [update_haiku, generate_media]

def get_tool_names():
    return [tool.name for tool in get_tools()]

def create_agent():
    prompt = ChatPromptTemplate.from_messages([
        ("system", system_template),
        ("placeholder", "{messages}"),
        ("placeholder", "{agent_scratchpad}"),
    ])
    agent_model = create_tool_calling_agent(model, tools=get_tools(), prompt=prompt)
    agent_executor = AgentExecutor(agent=agent_model, tools=get_tools(), verbose=True, max_iterations=5)
    return agent_executor


agent_model = create_agent()


def process_message(haiku_id: str, user_message: str):
    store_chat_interaction(haiku_id, user_message, 'human')

    chats = retrieve_chats(haiku_id)
    messages = []
    for chat in chats:
        messages.append((chat.role, chat.message))

    inputs = {
        "messages": messages,
        "haiku_id": haiku_id
    }

    config = {"configurable": {"haiku_id": haiku_id}}

    agent_message = agent_model.invoke(inputs, config=config)
    print('agent_message', agent_message)
    print('agent_message_content', agent_message["output"])

    store_chat_interaction(haiku_id, agent_message["output"], 'ai')
