import os
import sqlite3
from typing import List
from dotenv import load_dotenv


load_dotenv()
DATABASE_URL = os.getenv("DATABASE_URL", "haiku_generator.db")


def get_db_connection():
    conn = sqlite3.connect(DATABASE_URL)
    conn.row_factory = sqlite3.Row
    return conn

def create_tables():
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute('''
    CREATE TABLE IF NOT EXISTS haiku (
        haiku_id TEXT PRIMARY KEY,
        status TEXT DEFAULT "new",
        error_message TEXT,
        haiku_line_en_1 TEXT,
        haiku_line_en_2 TEXT,
        haiku_line_en_3 TEXT,
        haiku_line_ja_1 TEXT,
        haiku_line_ja_2 TEXT,
        haiku_line_ja_3 TEXT,
        image_description_1 TEXT,
        image_description_2 TEXT,
        image_description_3 TEXT,
        image_link_1 TEXT,
        image_link_2 TEXT,
        image_link_3 TEXT,
        audio_link_1 TEXT,
        audio_link_2 TEXT,
        audio_link_3 TEXT
    )''')
    cursor.execute('''
    CREATE TABLE IF NOT EXISTS chat_history (
        chat_id INTEGER PRIMARY KEY AUTOINCREMENT,
        haiku_id TEXT,
        role TEXT,
        message TEXT,
        FOREIGN KEY (haiku_id) REFERENCES haiku (haiku_id)
    )''')
    conn.commit()
    conn.close()

create_tables()

def update_haiku_lines(haiku_id: str, haiku: List[str]):
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute('''
    INSERT OR REPLACE INTO haiku (haiku_id, haiku_line_en_1, haiku_line_en_2, haiku_line_en_3)
    VALUES (?, ?, ?, ?);
    ''', (haiku_id, haiku[0], haiku[1], haiku[2]))
    conn.commit()
    conn.close()

def update_image_description(haiku_id: str, description: str, line_number: int):
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute('''
    INSERT OR REPLACE INTO haiku (haiku_id, image_description_{})
    VALUES (?, ?);
    '''.format(line_number), (haiku_id, description))
    conn.commit()
    conn.close()

def update_translation(haiku_id: str, translated_haiku: str, line_number: int):
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute('''
    INSERT OR REPLACE INTO haiku (haiku_id, haiku_line_ja_{})
    VALUES (?, ?);
    '''.format(line_number), (haiku_id, translated_haiku))
    conn.commit()
    conn.close()

def store_chat_interaction(haiku_id: str, message: str, role: str):
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute('''
        INSERT INTO chat_history (haiku_id, message, role)
        VALUES (?, ?, ?)
    ''', (haiku_id, message, role))
    conn.commit()
    conn.close()

def retrieve_chat_history(haiku_id: str):
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute('SELECT * FROM chat_history WHERE haiku_id = ?', (haiku_id,))
    history = cursor.fetchall()
    conn.close()
    return [dict(row) for row in history]

def retrieve_last_chat(haiku_id: str):
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute('SELECT * FROM chat_history WHERE haiku_id = ? ORDER BY chat_id DESC LIMIT 1', (haiku_id,))
    last_chat = cursor.fetchone()
    conn.close()
    return dict(last_chat) if last_chat else {}

def retrieve_haikus():
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute('SELECT * FROM haiku')
    haikus = cursor.fetchall()
    conn.close()
    return [dict(row) for row in haikus]

def retrieve_haiku(haiku_id: str):
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute('SELECT * FROM haiku WHERE haiku_id = ?', (haiku_id,))
    haiku = cursor.fetchone()
    conn.close()
    return dict(haiku) if haiku else {}

def delete_haiku_db(haiku_id: str):
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute('DELETE FROM haiku WHERE haiku_id = ?', (haiku_id,))
    cursor.execute('DELETE FROM chat_history WHERE haiku_id = ?', (haiku_id,))
    conn.commit()
    conn.close()

def retrieve_haiku_line(haiku_id: str, line_number: int):
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute(f'SELECT haiku_line_en_{line_number} FROM haiku WHERE haiku_id = ?', (haiku_id,))
    line = cursor.fetchone()
    conn.close()
    return line[0] if line else None

def update_haiku_link(haiku_id: str, image_link: str = None, audio_link: str = None, number: int = None):
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute('''
    INSERT OR REPLACE INTO haiku (haiku_id, image_link_{}, audio_link_{})
    VALUES (?, ?, ?);
    '''.format(number, number), (haiku_id, image_link, audio_link))
    conn.commit()
    conn.close()

def set_status(haiku_id: str, status: str, error_message: str):
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute('''
    INSERT OR REPLACE INTO haiku (haiku_id, status, error_message)
    VALUES (?, ?, ?);
    ''', (haiku_id, status, error_message))
    conn.commit()
    conn.close()
