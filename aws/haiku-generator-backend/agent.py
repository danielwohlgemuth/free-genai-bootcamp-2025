import langchain
import os
from database import store_chat_interaction, retrieve_chats, update_haiku_lines, retrieve_haiku
from dotenv import load_dotenv
from langchain_aws import ChatBedrock
from langchain_core.prompts import ChatPromptTemplate
from langchain_core.tools import StructuredTool
from langchain_core.tools import tool
from langchain.agents import create_tool_calling_agent, AgentExecutor
from model import UpdateHaiku
from typing import List
from workflow import start_workflow


langchain.debug = True
load_dotenv()


MODEL_REGION = os.getenv('MODEL_REGION', 'us-east-1')
AWS_ACCESS_KEY_ID = os.getenv('AWS_ACCESS_KEY_ID')
AWS_SECRET_ACCESS_KEY = os.getenv('AWS_SECRET_ACCESS_KEY')
CHAT_MODEL_PROVIDER = os.getenv('CHAT_MODEL_PROVIDER', 'anthropic')
CHAT_MODEL_ID = os.getenv('CHAT_MODEL_ID')


model = ChatBedrock(
    region=MODEL_REGION,
    aws_access_key_id=AWS_ACCESS_KEY_ID,
    aws_secret_access_key=AWS_SECRET_ACCESS_KEY,
    provider=CHAT_MODEL_PROVIDER,
    model_id=CHAT_MODEL_ID
)

system_template="""You are an assistant that helps generate haikus.

A haiku is a traditional Japanese poem with the following format:
- Three lines
- Syllable pattern:
    - 5 syllables in the first line
    - 7 syllables in the second line
    - 5 syllables in the third line

The haiku should be in English.

Wait until the user confirms that the haiku is good, then generate the media.
Once media is generated, the interaction is complete. Don't ask for more input.
Have a conversation with the user to generate and improve the haiku. Once you start generating the media, the interaction is complete, so make sure the user is satisfied with the haiku.
As soon as you have a haiku, either provided by the user or generated by you, save it to the database before doing anything else.

Pass the haiku as a list of three strings to the tool.
"""


def generate_media_base(user_id: str, haiku_id: str) -> str:
    haiku = retrieve_haiku(user_id, haiku_id)
    if not haiku.haiku_line_en_1 or not haiku.haiku_line_en_2 or not haiku.haiku_line_en_3:
        return f"Haiku not available for media generation. Please save a haiku first."    
    start_workflow(user_id, haiku_id)
    return f"Media generated"

def configure_generate_media(user_id: str, haiku_id: str) -> tool:
    def generate_media():
        return generate_media_base(user_id, haiku_id)

    return StructuredTool.from_function(
        func=generate_media,
        name="generate_media",
        description="Generate haiku media.",
        args_schema=None
    )

def update_haiku_base(user_id: str, haiku_id: str, haiku: List[str], topic: str) -> str:
    if len(haiku) != 3:
        return "Invalid haiku format. Please provide 3 lines."
    if not topic:
        return "Invalid haiku format. Please provide a topic."
    update_haiku_lines(user_id, haiku_id, haiku, topic)
    return "Haiku updated in database"

def configure_update_haiku(user_id: str, haiku_id: str) -> tool:
    def update_haiku(haiku: List[str], topic: str):
        return update_haiku_base(user_id, haiku_id, haiku, topic)

    return StructuredTool.from_function(
        func=update_haiku,
        name="update_haiku",
        description="Update haiku in database.",
        args_schema=UpdateHaiku
    )

def create_agent(user_id: str, haiku_id: str):
    generate_media = configure_generate_media(user_id, haiku_id)
    update_haiku = configure_update_haiku(user_id, haiku_id)
    tools = [generate_media, update_haiku]
    prompt = ChatPromptTemplate.from_messages([
        ("system", system_template),
        ("placeholder", "{messages}"),
        ("placeholder", "{agent_scratchpad}"),
    ])
    agent_model = create_tool_calling_agent(model, tools=tools, prompt=prompt)
    agent_executor = AgentExecutor(agent=agent_model, tools=tools, verbose=True, max_iterations=5)
    return agent_executor

def process_message(user_id: str, haiku_id: str, user_message: str):
    store_chat_interaction(user_id, haiku_id, user_message, 'human')

    chats = retrieve_chats(user_id, haiku_id)
    messages = []
    for chat in chats:
        messages.append((chat.role, chat.message))
    inputs = { "messages": messages }

    agent_model = create_agent(user_id, haiku_id)
    agent_message = agent_model.invoke(inputs)
    print('agent_message', agent_message)
    print('agent_message_content', agent_message["output"])
    if agent_message["output"] and agent_message["output"][0]["text"]:
        print('agent_message_content_text', agent_message["output"][0]["text"])
        store_chat_interaction(user_id, haiku_id, agent_message["output"][0]["text"], 'ai')
