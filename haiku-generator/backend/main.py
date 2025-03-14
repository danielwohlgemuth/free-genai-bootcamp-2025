from agent import process_message
from database import retrieve_chats, retrieve_haikus, retrieve_haiku, delete_haiku_db, retrieve_last_chat, insert_haiku
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from model import InteractWithChatbotRequest, InteractWithChatbotResponse, ListHaikusResponse, GetHaikuResponse, DeleteHaikuResponse


app = FastAPI()

# Add CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

@app.post('/chat/{haiku_id}')
async def interact_with_chatbot(haiku_id: str, chat_message: InteractWithChatbotRequest) -> InteractWithChatbotResponse:
    if not retrieve_haiku(haiku_id):
        insert_haiku(haiku_id)
    process_message(haiku_id, chat_message.message)
    chat = retrieve_last_chat(haiku_id)
    haiku = retrieve_haiku(haiku_id)
    return InteractWithChatbotResponse(chat=chat, haiku=haiku)

@app.get('/haiku')
async def list_haikus() -> ListHaikusResponse:
    haikus = retrieve_haikus()
    return ListHaikusResponse(haikus=haikus)

@app.get('/haiku/{haiku_id}')
async def get_haiku(haiku_id: str) -> GetHaikuResponse:
    haiku = retrieve_haiku(haiku_id)
    chats = retrieve_chats(haiku_id)
    return GetHaikuResponse(haiku=haiku, chats=chats)

@app.delete('/haiku/{haiku_id}')
async def delete_haiku(haiku_id: str) -> DeleteHaikuResponse:
    delete_haiku_db(haiku_id)
    return DeleteHaikuResponse(message='Haiku and associated data deleted successfully')

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)
