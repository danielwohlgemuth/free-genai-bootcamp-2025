import sqlite3

# Connect to SQLite database (or create it if it doesn't exist)
conn = sqlite3.connect('haiku_generator.db')
cursor = conn.cursor()

# Create Haiku Table
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

# Create Chat History Table
cursor.execute('''
CREATE TABLE IF NOT EXISTS chat_history (
    chat_id INTEGER PRIMARY KEY AUTOINCREMENT,
    haiku_id TEXT,
    role TEXT,
    message TEXT,
    FOREIGN KEY (haiku_id) REFERENCES haiku (haiku_id)
)''')

# Commit changes and close the connection
conn.commit()
conn.close()
