from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
from typing import List, Optional
from langchain_ollama import ChatOllama
from langchain.prompts import ChatPromptTemplate, SystemMessagePromptTemplate, HumanMessagePromptTemplate
from langchain.output_parsers import PydanticOutputParser
from langchain.agents import AgentExecutor, create_react_agent
from tools import get_tools
import os
from dotenv import load_dotenv
import traceback
from models import WordInfo, VocabularyResponse, SongRequest

import langchain
langchain.debug = True

# Load environment variables
load_dotenv()
OLLAMA_BASE_URL = os.getenv("OLLAMA_BASE_URL", "http://localhost:11434")
MODEL_NAME = os.getenv("MODEL_NAME", "qwen2.5:3b")

app = FastAPI(title="Japanese Song Vocabulary Extractor")

# Initialize the language model
llm = ChatOllama(
    base_url=OLLAMA_BASE_URL,
    model=MODEL_NAME
)



@app.post("/extract_vocabulary", response_model=VocabularyResponse)
async def extract_vocabulary(request: SongRequest):
    try:

    except Exception as e:
        print(f"Error in extract_vocabulary: {str(e)}")
        print('Stack trace:', ''.join(traceback.format_tb(e.__traceback__)))
        raise HTTPException(status_code=500, detail=str(e))

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)
