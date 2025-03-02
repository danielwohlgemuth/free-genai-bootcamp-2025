import langchain
import os
import requests
import traceback
from dotenv import load_dotenv
from fastapi import FastAPI, HTTPException
from langchain_ollama import ChatOllama
from langchain.agents import AgentExecutor, create_react_agent
from langchain.output_parsers import PydanticOutputParser
from langchain.prompts import ChatPromptTemplate, SystemMessagePromptTemplate, HumanMessagePromptTemplate
from langgraph.graph import StateGraph, START, END
from models import State, WordInfo, VocabularyResponse, SongRequest
from pydantic import BaseModel
from tools import search_lyrics, get_lyrics, extract_lyrics, extract_vocabulary, filter_vocabulary, enhance_vocabulary
from typing import List, Optional


langchain.debug = True

# Load environment variables
load_dotenv()
OLLAMA_BASE_URL = os.getenv("OLLAMA_BASE_URL", "http://localhost:11434")
MODEL_NAME = os.getenv("MODEL_NAME", "qwen2.5:7b")

def define_workflow():
    # Build workflow
    workflow = StateGraph(State)

    # Add nodes
    workflow.add_node("search_lyrics", search_lyrics)
    workflow.add_node("get_lyrics", get_lyrics)
    workflow.add_node("extract_lyrics", extract_lyrics)
    workflow.add_node("extract_vocabulary", extract_vocabulary)
    workflow.add_node("filter_vocabulary", filter_vocabulary)
    workflow.add_node("enhance_vocabulary", enhance_vocabulary)

    # Add edges to connect nodes
    workflow.add_edge(START, "search_lyrics")
    workflow.add_edge("search_lyrics", "get_lyrics")
    workflow.add_edge("get_lyrics", "extract_lyrics")
    workflow.add_edge("extract_lyrics", "extract_vocabulary")
    workflow.add_edge("extract_vocabulary", "filter_vocabulary")
    workflow.add_edge("filter_vocabulary", "enhance_vocabulary")
    workflow.add_edge("enhance_vocabulary", END)

    # Compile
    chain = workflow.compile()

    # Save mermaid graph
    try:
        with open("song-vocab.mermaid", "w") as f:
            f.write(chain.get_graph().draw_mermaid())
        with open("song-vocab-mermaid.png", "wb") as f:
            f.write(chain.get_graph().draw_mermaid_png())
    except Exception as e:
        print(f"Error saving graph: {str(e)}")

    return chain

app = FastAPI(title="Japanese Song Vocabulary Extractor")
chain = define_workflow()

@app.post("/extract_vocabulary", response_model=VocabularyResponse)
async def extract_vocabulary(request: SongRequest):
    try:
        state = chain.invoke({ "song_name": request.topic })
        result = state['enhanced_vocabulary']
        result.group_name = request.topic
        return result

    except Exception as e:
        print(f"Error in extract_vocabulary: {str(e)}")
        print('Stack trace:', ''.join(traceback.format_tb(e.__traceback__)))
        raise HTTPException(status_code=500, detail=str(e))

if __name__ == "__main__":
    # Make sure the model is loaded
    requests.post(f"{OLLAMA_BASE_URL}/api/pull", data=f'{{"model": "{MODEL_NAME}"}}')

    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)
