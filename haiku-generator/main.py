from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
from database import get_db_connection, execute_query, fetch_all, fetch_one

app = FastAPI()

# Models for request and response bodies
class ChatMessage(BaseModel):
    message: str

class HaikuResponse(BaseModel):
    haiku_id: str
    status: str
    error_message: str
    haiku_line_en_1: str
    haiku_line_en_2: str
    haiku_line_en_3: str

# API Endpoints
@app.post('/chat/{haiku_id}')
async def interact_with_chatbot(haiku_id: str, chat_message: ChatMessage):
    conn = get_db_connection()
    execute_query(conn, 'insert into chat_history (haiku_id, role, message) values (?, ?, ?)', (haiku_id, 'user', chat_message.message))
    # Logic for chatbot interaction goes here
    # For now, we will just return a placeholder response
    execute_query(conn, 'insert into chat_history (haiku_id, role, message) values (?, ?, ?)', (haiku_id, 'assistant', 'some_response'))
    return {"chat_id": "some_chat_id", "message": chat_message.message, "haiku": {"haiku_id": haiku_id, "status": "new", "error_message": "", "haiku_line_en_1": "", "haiku_line_en_2": "", "haiku_line_en_3": ""}}

@app.get('/chat/{haiku_id}/history')
async def get_chat_history(haiku_id: str):
    conn = get_db_connection()
    history = fetch_all(conn, 'SELECT * FROM chat_history WHERE haiku_id = ?', (haiku_id,))
    return {'messages': [{'chat_id': row['chat_id'], 'role': row['role'], 'message': row['message']} for row in history]}

@app.get('/haiku')
async def list_haikus():
    conn = get_db_connection()
    haikus = fetch_all(conn, 'SELECT haiku_id, status, error_message FROM haiku')
    return {'haikus': [{'haiku_id': row['haiku_id'], 'status': row['status'], 'error_message': row['error_message']} for row in haikus]}

@app.get('/haiku/{haiku_id}')
async def get_haiku(haiku_id: str):
    conn = get_db_connection()
    haiku = fetch_one(conn, 'SELECT * FROM haiku WHERE haiku_id = ?', (haiku_id,))
    if haiku is None:
        raise HTTPException(status_code=404, detail='Haiku not found')
    return {'haiku': dict(haiku)}

@app.delete('/haiku/{haiku_id}')
async def delete_haiku(haiku_id: str):
    conn = get_db_connection()
    execute_query(conn, 'DELETE FROM haiku WHERE haiku_id = ?', (haiku_id,))
    execute_query(conn, 'DELETE FROM chat_history WHERE haiku_id = ?', (haiku_id,))
    conn.commit()
    return {'detail': 'Haiku and associated data deleted successfully'}
