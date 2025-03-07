from database import retrieve_chat_history, retrieve_haikus, retrieve_haiku, delete_haiku_db, retrieve_last_chat, process_message
from fastapi import FastAPI, HTTPException
from pydantic import BaseModel

app = FastAPI()

class ChatMessage(BaseModel):
    message: str

class HaikuResponse(BaseModel):
    haiku_id: str
    status: str
    error_message: str
    haiku_line_en_1: str
    haiku_line_en_2: str
    haiku_line_en_3: str

@app.post('/chat/{haiku_id}')
async def interact_with_chatbot(haiku_id: str, chat_message: ChatMessage):
    await process_message(chat_message.message, haiku_id)
    chat = retrieve_last_chat(haiku_id)
    haiku = retrieve_haiku(haiku_id)
    return {'chat': chat, 'haiku': haiku}

@app.get('/chat/{haiku_id}/history')
async def get_chat_history(haiku_id: str):
    history = retrieve_chat_history(haiku_id)
    return {'messages': history}

@app.get('/haiku')
async def list_haikus():
    haikus = retrieve_haikus()
    return {'haikus': haikus}

@app.get('/haiku/{haiku_id}')
async def get_haiku(haiku_id: str):
    haiku = retrieve_haiku(haiku_id)
    return {'haiku': haiku}

@app.delete('/haiku/{haiku_id}')
async def delete_haiku(haiku_id: str):
    delete_haiku_db(haiku_id)
    return {'detail': 'Haiku and associated data deleted successfully'}
