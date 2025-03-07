import os
import sqlite3
from typing import List


DATABASE_URL = os.getenv("DATABASE_URL", "sqlite:///haiku_generator.db")


# Function to get a database connection

def get_db_connection():
    conn = sqlite3.connect(DATABASE_URL)
    return conn

# Function to update haiku in the database

def update_haiku(haiku: List[str], haiku_id: str):
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute('UPDATE haiku SET haiku_line_en_1 = ?, haiku_line_en_2 = ?, haiku_line_en_3 = ? WHERE haiku_id = ?', (haiku[0], haiku[1], haiku[2], haiku_id))
    conn.commit()
    conn.close()

# Function to update haiku lines in the database

def update_haiku_lines(haiku: List[str], haiku_id: str):
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute('UPDATE haiku SET haiku_line_en_1 = ?, haiku_line_en_2 = ?, haiku_line_en_3 = ? WHERE haiku_id = ?', (haiku[0], haiku[1], haiku[2], haiku_id))
    conn.commit()
    conn.close()

# Function to update image description in the database

def update_image_description_in_db(haiku_id: str, description: str, line_number: int):
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute(f'UPDATE haiku SET image_description_{line_number} = ? WHERE haiku_id = ?', (description, haiku_id))
    conn.commit()
    conn.close()

# Function to update translation in the database

def update_translation_in_db(haiku_id: str, translated_haiku: str, line_number: int):
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute(f'UPDATE haiku SET translation_{line_number} = ? WHERE haiku_id = ?', (translated_haiku, haiku_id))
    conn.commit()
    conn.close()

# Function to store chat interaction in the database

def store_chat_interaction(haiku_id: str, message: str, role: str):
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute('''
        INSERT INTO chat_history (haiku_id, message, role)
        VALUES (?, ?, ?)
    ''', (haiku_id, message, role))
    conn.commit()
    conn.close()

# Function to retrieve chat history

def retrieve_chat_history(haiku_id: str):
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute('SELECT * FROM chat_history WHERE haiku_id = ?', (haiku_id,))
    history = cursor.fetchall()
    conn.close()
    return [dict(row) for row in history]

# Function to retrieve the last chat entry for a specific haiku ID

def retrieve_last_chat(haiku_id: str):
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute('SELECT * FROM chat_history WHERE haiku_id = ? ORDER BY chat_id DESC LIMIT 1', (haiku_id,))
    last_chat = cursor.fetchone()
    conn.close()
    return dict(last_chat) if last_chat else {}

# Function to update haiku links

def update_haiku_links(haiku_id: str, image_link: str, audio_link: str, image_number: int = None, audio_number: int = None):
    conn = get_db_connection()
    cursor = conn.cursor()
    if image_number is not None:
        cursor.execute(f'''UPDATE haiku SET image_link_{image_number} = ? WHERE haiku_id = ?''', (image_link, haiku_id))
    if audio_number is not None:
        cursor.execute(f'''UPDATE haiku SET audio_link_{audio_number} = ? WHERE haiku_id = ?''', (audio_link, haiku_id))
    conn.commit()
    conn.close()

# Function to retrieve all haikus

def retrieve_haikus():
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute('SELECT * FROM haiku')
    haikus = cursor.fetchall()
    conn.close()
    return [dict(row) for row in haikus]

# Function to retrieve a specific haiku by ID

def retrieve_haiku(haiku_id: str):
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute('SELECT * FROM haiku WHERE haiku_id = ?', (haiku_id,))
    haiku = cursor.fetchone()
    conn.close()
    return dict(haiku) if haiku else {}

# Function to delete a haiku by ID

def delete_haiku_db(haiku_id: str):
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute('DELETE FROM haiku WHERE haiku_id = ?', (haiku_id,))
    cursor.execute('DELETE FROM chat_history WHERE haiku_id = ?', (haiku_id,))
    conn.commit()
    conn.close()

# Function to retrieve a specific haiku line by ID

def retrieve_haiku_line(haiku_id: str, line_number: int):
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute(f'SELECT haiku_line_en_{line_number} FROM haiku WHERE haiku_id = ?', (haiku_id,))
    line = cursor.fetchone()
    conn.close()
    return line[0] if line else None

# Function to update translation in the database

def update_translation(haiku_id: str, translated_haiku: str, line_number: int):
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute(f'UPDATE haiku SET haiku_line_ja_{line_number} = ? WHERE haiku_id = ?', (translated_haiku, haiku_id))
    conn.commit()
    conn.close()

# Function to update image description in the database

def update_image_description(haiku_id: str, description: str, line_number: int):
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute(f'UPDATE haiku SET image_description_{line_number} = ? WHERE haiku_id = ?', (description, haiku_id))
    conn.commit()
    conn.close()

# Function to update haiku links

def update_haiku_links(haiku_id: str, image_link: str = None, audio_link: str = None, image_number: int = None, audio_number: int = None):
    conn = get_db_connection()
    cursor = conn.cursor()
    if image_number is not None:
        cursor.execute(f'UPDATE haiku SET image_link_{image_number} = ? WHERE haiku_id = ?', (image_link, haiku_id))
    if audio_number is not None:
        cursor.execute(f'UPDATE haiku SET audio_link_{audio_number} = ? WHERE haiku_id = ?', (audio_link, haiku_id))
    conn.commit()
    conn.close()
