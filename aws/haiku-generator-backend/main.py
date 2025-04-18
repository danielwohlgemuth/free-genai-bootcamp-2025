from agent import process_message
from auth import get_user_id
from database import retrieve_chats, retrieve_haikus, retrieve_haiku, delete_haiku_db, retrieve_last_chat, insert_haiku
from fastapi import FastAPI, Depends
from fastapi.middleware.cors import CORSMiddleware
from model import SendChatRequest, SendChatResponse, ListHaikusResponse, GetHaikuResponse, DeleteHaikuResponse, GenerateMediaResponse
from storage import get_signed_haiku_media
from workflow import start_workflow


app = FastAPI()

# Add CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

@app.post('/api/chat/{haiku_id}')
async def send_chat(haiku_id: str, chat_message: SendChatRequest, user_id: str = Depends(get_user_id)) -> SendChatResponse:
    if retrieve_haiku(user_id, haiku_id).error_message == "Haiku not found":
        insert_haiku(user_id, haiku_id)
    process_message(user_id, haiku_id, chat_message.message)
    chat = retrieve_last_chat(user_id, haiku_id)
    haiku = retrieve_haiku(user_id, haiku_id)
    get_signed_haiku_media(haiku)
    return SendChatResponse(chat=chat, haiku=haiku)

@app.get('/api/haiku')
async def list_haikus(user_id: str = Depends(get_user_id)) -> ListHaikusResponse:
    haikus = retrieve_haikus(user_id)
    for haiku in haikus:
        get_signed_haiku_media(haiku)
    return ListHaikusResponse(haikus=haikus)

@app.get('/api/haiku/{haiku_id}')
async def get_haiku(haiku_id: str, user_id: str = Depends(get_user_id)) -> GetHaikuResponse:
    haiku = retrieve_haiku(user_id, haiku_id)
    get_signed_haiku_media(haiku)
    if haiku.error_message == "Haiku not found":
        haiku.error_message = ""
    chats = retrieve_chats(user_id, haiku_id)
    return GetHaikuResponse(haiku=haiku, chats=chats)

@app.post('/api/haiku/{haiku_id}')
async def generate_media(haiku_id: str, user_id: str = Depends(get_user_id)) -> GenerateMediaResponse:
    haiku = retrieve_haiku(user_id, haiku_id)
    if haiku.error_message == "Haiku not found" or haiku.status != "failed":
        haiku.error_message = ""
    else:
        start_workflow(user_id, haiku_id)
        haiku = retrieve_haiku(user_id, haiku_id)
    get_signed_haiku_media(haiku)
    return GenerateMediaResponse(haiku=haiku)

@app.delete('/api/haiku/{haiku_id}')
async def delete_haiku(haiku_id: str, user_id: str = Depends(get_user_id)) -> DeleteHaikuResponse:
    delete_haiku_db(user_id, haiku_id)
    return DeleteHaikuResponse(message='Haiku and associated data deleted successfully')

@app.get("/api/health")
async def health_check():
    return {"status": "healthy"}

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)
