from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
from typing import List, Dict
from langchain.agents import AgentExecutor, create_react_agent
from langchain_community.llms import Ollama
from langchain.prompts import PromptTemplate
from langchain.tools import Tool
from tools import get_tools

app = FastAPI(title="Japanese Song Vocabulary Extractor")

class SongRequest(BaseModel):
    query: str

class WordInfo(BaseModel):
    japanese: str
    romaji: str
    english: str
    parts: Dict[str, str]

class VocabularyResponse(BaseModel):
    group_name: str
    words: List[WordInfo]

# Initialize Ollama LLM
llm = Ollama(model="mistral")

# Get tools for the agent
tools = get_tools()

# Define the agent's prompt template
prompt = PromptTemplate.from_template("""
You are a Japanese language expert tasked with extracting vocabulary from song lyrics.
Your goal is to identify and explain key vocabulary that would be useful for Japanese learners.

Follow these steps:
1. Search for the song lyrics using the search_lyrics tool
2. Extract vocabulary using the analyze_vocabulary tool
3. Format the results according to the required schema

Question: {input}

{agent_scratchpad}
""")

# Create the agent
agent = create_react_agent(llm=llm, tools=tools, prompt=prompt)
agent_executor = AgentExecutor(agent=agent, tools=tools, verbose=True)

@app.post("/extract_vocabulary", response_model=VocabularyResponse)
async def extract_vocabulary(request: SongRequest):
    try:
        # Use the agent to process the request
        result = agent_executor.invoke({
            "input": f"Find vocabulary from the song: {request.query}"
        })
        
        # Extract the vocabulary items from the agent's response
        lyrics = tools[0].func(request.query)  # Get lyrics
        vocab_items = tools[2].func(lyrics)    # Analyze vocabulary
        
        return VocabularyResponse(
            group_name=request.query,
            words=[
                WordInfo(**item)
                for item in vocab_items
            ]
        )
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)
