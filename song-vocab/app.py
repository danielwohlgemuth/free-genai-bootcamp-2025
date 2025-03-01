from fastapi import FastAPI, HTTPException
from typing import List, Dict
from langchain.agents import AgentExecutor, create_react_agent
from langchain_community.llms import Ollama
from langchain.prompts import PromptTemplate
from langchain.tools import Tool
from tools import get_tools
import os
from dotenv import load_dotenv
from models import SongRequest, VocabularyResponse, WordInfo

# Load environment variables
load_dotenv()
OLLAMA_BASE_URL = os.getenv("OLLAMA_BASE_URL", "http://localhost:11434")
MODEL_NAME = os.getenv("MODEL_NAME", "qwen2.5:3b")

app = FastAPI(title="Japanese Song Vocabulary Extractor")

# Initialize Ollama LLM
llm = Ollama(
    base_url=OLLAMA_BASE_URL,
    model=MODEL_NAME
)

# Get tools for the agent
tools = get_tools()

# Define the agent's prompt template
prompt = PromptTemplate.from_template("""
You are a Japanese language expert tasked with extracting vocabulary from song lyrics.
Your goal is to identify and explain key vocabulary that would be useful for Japanese learners.

Follow these steps:
1. Use search_lyrics_links to find webpages with the song lyrics
2. Use get_lyrics_from_url on the most relevant URL to get the raw text
3. Use extract_clean_lyrics to get clean Japanese lyrics
4. Use extract_vocabulary to identify vocabulary items
5. Use filter_vocabulary to select the most useful words
6. Use enhance_vocabulary to add romaji and translations

Question: {input}

{agent_scratchpad}
""")

# Create the agent
agent = create_react_agent(llm=llm, tools=tools, prompt=prompt, response_format=VocabularyResponse, verbose=True)

@app.post("/extract_vocabulary", response_model=VocabularyResponse)
async def extract_vocabulary(request: SongRequest):
    try:
        # Use the agent to process the request
        result = agent.invoke({
            "input": f"Find vocabulary from the song: {request.query}"
        })
        
        # The agent's response should contain the processed vocabulary
        # Convert it to our response format
        if isinstance(result['output'], str):
            # If the output is a string, try to parse it
            try:
                vocab_data = eval(result['output'])
            except:
                vocab_data = []
        else:
            vocab_data = result['output']
            
        return VocabularyResponse(
            group_name=request.query,
            words=[WordInfo(**item) for item in vocab_data]
        )
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)
