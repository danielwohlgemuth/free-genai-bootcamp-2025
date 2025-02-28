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

Question: {input}

{agent_scratchpad}
""")

# Create the agent
agent = create_react_agent(llm=llm, tools=tools, prompt=prompt)
agent_executor = AgentExecutor(agent=agent, tools=tools, verbose=True)

@app.post("/extract_vocabulary", response_model=VocabularyResponse)
async def extract_vocabulary(request: SongRequest):
    try:
        # TODO: Implement the agent-based vocabulary extraction logic
        # For now, return a mock response
        return VocabularyResponse(
            group_name=request.query,
            words=[
                WordInfo(
                    japanese="例",
                    romaji="rei",
                    english="example",
                    parts={
                        "type": "noun",
                        "formality": "neutral"
                    }
                )
            ]
        )
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)
