import os
import psycopg
import uuid
from dotenv import load_dotenv
from model import Empty, Haiku, Chat
from psycopg.rows import dict_row
from typing import List


load_dotenv()


DB_HOST = os.getenv('DB_HOST', 'localhost')
DB_PORT = os.getenv('DB_PORT', '5432')
DB_USER = os.getenv('DB_USER', 'user')
DB_PASSWORD = os.getenv('DB_PASSWORD', 'password')
DB_NAME = os.getenv('DB_NAME', 'haiku')
DATABASE_URL = f"postgresql://{DB_USER}:{DB_PASSWORD}@{DB_HOST}:{DB_PORT}/{DB_NAME}"


def get_db_connection():
    conn = psycopg.connect(DATABASE_URL)
    conn.row_factory = dict_row
    return conn

def create_database():
    # First connect to the default postgres database
    conn = psycopg.connect(
        host=DB_HOST,
        port=DB_PORT,
        user=DB_USER,
        password=DB_PASSWORD,
        dbname='postgres'
    )
    conn.autocommit = True
    cursor = conn.cursor()
    
    # Create the database
    cursor.execute(f"DROP DATABASE IF EXISTS {DB_NAME}")
    cursor.execute(f"CREATE DATABASE {DB_NAME}")
    
    # Connect to the newly created database
    conn.close()
    conn = psycopg.connect(
        host=DB_HOST,
        port=DB_PORT,
        user=DB_USER,
        password=DB_PASSWORD,
        dbname=DB_NAME
    )
    conn.autocommit = True
    cursor = conn.cursor()
    
    # Create the schema and grant permissions
    cursor.execute(f"""
        CREATE SCHEMA IF NOT EXISTS public;
        GRANT ALL ON SCHEMA public TO "{DB_USER}";
    """)
    
    conn.commit()
    conn.close()

def create_tables():
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute('''
    CREATE TABLE IF NOT EXISTS haiku (
        haiku_id TEXT PRIMARY KEY,
        status TEXT DEFAULT 'new',
        error_message TEXT,
        topic TEXT,
        haiku_line_en_1 TEXT,
        haiku_line_en_2 TEXT,
        haiku_line_en_3 TEXT,
        image_description_1 TEXT,
        image_description_2 TEXT,
        image_description_3 TEXT,
        image_link_1 TEXT,
        image_link_2 TEXT,
        image_link_3 TEXT,
        haiku_line_ja_1 TEXT,
        haiku_line_ja_2 TEXT,
        haiku_line_ja_3 TEXT,
        audio_link_1 TEXT,
        audio_link_2 TEXT,
        audio_link_3 TEXT
    )''')
    cursor.execute('''
    CREATE TABLE IF NOT EXISTS chat (
        chat_id TEXT PRIMARY KEY,
        haiku_id TEXT,
        role TEXT,
        message TEXT,
        created_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP,
        FOREIGN KEY (haiku_id) REFERENCES haiku (haiku_id)
    )''')
    conn.commit()
    conn.close()

def retrieve_haikus()-> List[Haiku]:
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute('SELECT * FROM haiku')
    haikus = cursor.fetchall()
    conn.close()
    return [Haiku(**dict(row)) for row in haikus]

def retrieve_haiku(haiku_id: str) -> Haiku:
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute('SELECT * FROM haiku WHERE haiku_id = ?', (haiku_id,))
    haiku = cursor.fetchone()
    conn.close()
    return Haiku(**dict(haiku)) if haiku else Haiku(haiku_id=haiku_id, status="new", error_message="Haiku not found")

def retrieve_haiku_line(haiku_id: str, line_number: int) -> str:
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute(f'SELECT haiku_line_en_{line_number} FROM haiku WHERE haiku_id = ?', (haiku_id,))
    line = cursor.fetchone()
    conn.close()
    return line[0] if line else ''

def retrieve_chats(haiku_id: str) -> List[Chat]:
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute('SELECT * FROM chat WHERE haiku_id = ? ORDER BY created_at ASC', (haiku_id,))
    history = cursor.fetchall()
    conn.close()
    return [Chat(**dict(row)) for row in history]

def retrieve_last_chat(haiku_id: str) -> Chat | Empty:
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute('SELECT * FROM chat WHERE haiku_id = ? ORDER BY created_at DESC LIMIT 1', (haiku_id,))
    last_chat = cursor.fetchone()
    conn.close()
    return Chat(**dict(last_chat)) if last_chat else Empty()

def insert_haiku(haiku_id: str):
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute('''
    INSERT INTO haiku (haiku_id) VALUES (?)
    ''', (haiku_id,))
    conn.commit()
    conn.close()

def update_haiku_lines(haiku_id: str, haiku: List[str], topic: str):
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute('UPDATE haiku SET haiku_line_en_1 = ?, haiku_line_en_2 = ?, haiku_line_en_3 = ?, topic = ? WHERE haiku_id = ?', (haiku[0], haiku[1], haiku[2], topic, haiku_id))
    conn.commit()
    conn.close()

def update_image_description(haiku_id: str, description: str, line_number: int):
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute(f'UPDATE haiku SET image_description_{line_number} = ? WHERE haiku_id = ?', (description, haiku_id))
    conn.commit()
    conn.close()

def update_translation(haiku_id: str, translated_haiku: str, line_number: int):
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute(f'UPDATE haiku SET haiku_line_ja_{line_number} = ? WHERE haiku_id = ?', (translated_haiku, haiku_id))
    conn.commit()
    conn.close()

def update_haiku_link(haiku_id: str, number: int, image_link: str = None, audio_link: str = None):
    conn = get_db_connection()
    cursor = conn.cursor()
    if image_link is not None:
        cursor.execute(f'UPDATE haiku SET image_link_{number} = ? WHERE haiku_id = ?', (image_link, haiku_id))
    if audio_link is not None:
        cursor.execute(f'UPDATE haiku SET audio_link_{number} = ? WHERE haiku_id = ?', (audio_link, haiku_id))
    conn.commit()
    conn.close()

def set_status(haiku_id: str, status: str, error_message: str):
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute('UPDATE haiku SET status = ?, error_message = ? WHERE haiku_id = ?', (status, error_message, haiku_id))
    conn.commit()
    conn.close()

def store_chat_interaction(haiku_id: str, message: str, role: str):
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute('''
        INSERT INTO chat (chat_id, haiku_id, message, role)
        VALUES (?, ?, ?, ?)
    ''', (str(uuid.uuid4()), haiku_id, message, role))
    conn.commit()
    conn.close()

def delete_haiku_db(haiku_id: str):
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute('DELETE FROM haiku WHERE haiku_id = ?', (haiku_id,))
    cursor.execute('DELETE FROM chat WHERE haiku_id = ?', (haiku_id,))
    conn.commit()
    conn.close()
