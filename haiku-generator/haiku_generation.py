from langchain import LLMChain, PromptTemplate
from langchain.llms import Ollama
import sqlite3
import logging
import os

logging.basicConfig(level=logging.INFO, filename='haiku_generator.log', filemode='a',
                    format='%(asctime)s - %(levelname)s - %(message)s')

MODEL_NAME = os.getenv("OLLAMA_MODEL", "qwen2.5:7b")
ollama_model = Ollama(model=MODEL_NAME)

def retrieve_chat_history(haiku_id: str):
    conn = sqlite3.connect('haiku_generator.db')
    cursor = conn.cursor()
    cursor.execute('SELECT * FROM chat_history WHERE haiku_id = ?', (haiku_id,))
    history = cursor.fetchall()
    conn.close()
    return history

def store_chat_interaction(haiku_id: str, user_message: str, response: str):
    conn = sqlite3.connect('haiku_generator.db')
    cursor = conn.cursor()
    cursor.execute('''
        INSERT INTO chat_history (haiku_id, user_message, response)
        VALUES (?, ?, ?)
    ''', (haiku_id, user_message, response))
    conn.commit()
    conn.close()

async def generate_haiku(user_message: str, haiku_id: str):
    try:
        chat_history = retrieve_chat_history(haiku_id)
        prompt = create_prompt(user_message, chat_history)
        haiku = await ollama_model.generate(prompt)
        logging.info(f"Haiku generated: {haiku}")
        await update_haiku_in_db(haiku_id, haiku)
        store_chat_interaction(haiku_id, user_message, haiku)
        multimedia = await generate_multimedia(haiku_id)
        return multimedia
    except Exception as e:
        logging.error(f"Error generating haiku: {e}")
        raise

async def update_haiku_in_db(haiku_id: str, haiku: str):
    conn = sqlite3.connect('haiku_generator.db')
    cursor = conn.cursor()
    cursor.execute('UPDATE haiku SET haiku_line_en_1 = ?, haiku_line_en_2 = ?, haiku_line_en_3 = ? WHERE haiku_id = ?', (haiku.split('\n')[0], haiku.split('\n')[1], haiku.split('\n')[2], haiku_id))
    conn.commit()
    conn.close()

async def generate_multimedia(haiku_id: str):
    for i in range(1, 4):
        haiku_line = await retrieve_haiku_line(haiku_id, i)
        await generate_image(haiku_id, haiku_line, i)
        await generate_audio(haiku_id, haiku_line, i)

async def retrieve_haiku_line(haiku_id: str, line_number: int):
    conn = sqlite3.connect('haiku_generator.db')
    cursor = conn.cursor()
    cursor.execute(f'SELECT haiku_line_en_{line_number} FROM haiku WHERE haiku_id = ?', (haiku_id,))
    line = cursor.fetchone()[0]
    conn.close()
    return line

async def create_image_description(haiku: str):
    return f'An artistic representation of the haiku: {haiku}'

async def generate_image(haiku_id: str, haiku_line: str, line_number: int):
    description = await create_image_description(haiku_line)
    await update_image_description_in_db(haiku_id, description, line_number)
    await generate_image_from_description(description)

async def generate_audio(haiku_id: str, haiku_line: str, line_number: int):
    haiku = await retrieve_haiku(haiku_id)
    translated_haiku = await translate_haiku(haiku_line)
    await update_translation_in_db(haiku_id, translated_haiku, line_number)
    await generate_audio_from_text(translated_haiku)

async def translate_haiku(haiku: str):
    try:
        prompt = f'Translate the following haiku into Japanese: {haiku}'
        translation = await ollama_model.generate(prompt)
        logging.info(f"Haiku translated: {translation}")
        return translation
    except Exception as e:
        logging.error(f"Error translating haiku: {e}")
        raise

def create_prompt(user_message: str, chat_history: list):
    prompt = f'User: {user_message}\n'
    for entry in chat_history:
        user_msg, response = entry
        prompt += f'User: {user_msg}\nBot: {response}\n'
    prompt += 'Generate a single haiku with three lines based on the above conversation.'
    return prompt

async def update_translation_in_db(haiku_id: str, translated_haiku: str, line_number: int):
    conn = sqlite3.connect('haiku_generator.db')
    cursor = conn.cursor()
    cursor.execute(f'UPDATE haiku SET haiku_line_ja_{line_number} = ? WHERE haiku_id = ?', (translated_haiku, haiku_id))
    conn.commit()
    conn.close()

async def update_image_description_in_db(haiku_id: str, description: str, line_number: int):
    conn = sqlite3.connect('haiku_generator.db')
    cursor = conn.cursor()
    cursor.execute(f'UPDATE haiku SET image_description_{line_number} = ? WHERE haiku_id = ?', (description, haiku_id))
    conn.commit()
    conn.close()

async def retrieve_haiku(haiku_id: str):
    conn = sqlite3.connect('haiku_generator.db')
    cursor = conn.cursor()
    cursor.execute('SELECT haiku_line_en_1, haiku_line_en_2, haiku_line_en_3 FROM haiku WHERE haiku_id = ?', (haiku_id,))
    lines = cursor.fetchone()
    haiku = '\n'.join(lines)
    conn.close()
    return haiku
