import os
import sqlite3
from haiku_generation import generate_multimedia
from langchain_core.tools import InjectedToolArg, tool
from langchain_ollama import OllamaLLM
from langchain.tools import Tool
from typing import Annotated
from typing import List
from database import get_db_connection, close_db_connection


MODEL_NAME = os.getenv("OLLAMA_MODEL", "qwen2.5:7b")
ollama_model = OllamaLLM(model=MODEL_NAME)


@tool(parse_docstring=True)
def generate_haiku_media(haiku_id: Annotated[str, InjectedToolArg]) -> str:
    """Start haiku media generation from haiku.

    Args:
        haiku_id: Haiku ID.
    """
    generate_multimedia(haiku_id)
    return f"Haiku media generation started"

@tool
def update_haiku_in_db(haiku: List[str], haiku_id: Annotated[str, InjectedToolArg]) -> str:
    """Update haiku in database.

    Args:
        haiku: Haiku with each line as a separate string.
        haiku_id: Haiku ID.
    """
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute('UPDATE haiku SET haiku_line_en_1 = ?, haiku_line_en_2 = ?, haiku_line_en_3 = ? WHERE haiku_id = ?', (haiku.split('\n')[0], haiku.split('\n')[1], haiku.split('\n')[2], haiku_id))
    conn.commit()
    close_db_connection(conn)
    return f"Haiku updated in database"

def get_tools() -> List[Tool]:    
    return [
        generate_haiku_media,
        update_haiku_in_db
    ]
    
def retrieve_chat_history(haiku_id: str):
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute('SELECT * FROM chat_history WHERE haiku_id = ?', (haiku_id,))
    history = cursor.fetchall()
    close_db_connection(conn)
    return history

def store_chat_interaction(haiku_id: str, user_message: str, response: str):
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute('''
        INSERT INTO chat_history (haiku_id, user_message, response)
        VALUES (?, ?, ?)
    ''', (haiku_id, user_message, response))
    conn.commit()
    close_db_connection(conn)

async def generate_haiku(user_message: str, haiku_id: str):
    chat_history = retrieve_chat_history(haiku_id)
    prompt = create_prompt(user_message, chat_history)
    haiku = await ollama_model.generate(prompt)
    await update_haiku_in_db(haiku_id, haiku)
    store_chat_interaction(haiku_id, user_message, haiku)
    generate_multimedia(haiku_id)
    return f"Haiku generation started"

async def update_haiku_in_db(haiku_id: str, haiku: str):
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute('UPDATE haiku SET haiku_line_en_1 = ?, haiku_line_en_2 = ?, haiku_line_en_3 = ? WHERE haiku_id = ?', (haiku.split('\n')[0], haiku.split('\n')[1], haiku.split('\n')[2], haiku_id))
    conn.commit()
    close_db_connection(conn)

def create_prompt(user_message: str, chat_history: list):
    prompt = f'User: {user_message}\n'
    for entry in chat_history:
        user_msg, response = entry
        prompt += f'User: {user_msg}\nBot: {response}\n'
    prompt += 'Generate a single haiku with three lines based on the above conversation.'
    return prompt
