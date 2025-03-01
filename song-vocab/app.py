from fastapi import FastAPI, HTTPException
from typing import List, Dict
from langchain.agents import AgentExecutor, create_react_agent
from langchain_ollama import OllamaLLM
from langchain.prompts import ChatPromptTemplate, SystemMessagePromptTemplate, HumanMessagePromptTemplate
from langchain.output_parsers import PydanticOutputParser
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
llm = OllamaLLM(
    base_url=OLLAMA_BASE_URL,
    model=MODEL_NAME
)

# Get tools for the agent
tools = get_tools()

# Define the agent's prompt template
system_template = """
You are a Japanese language expert tasked with extracting vocabulary from song lyrics.
Your goal is to identify and explain key vocabulary that would be useful for Japanese learners.

You have access to the following tools:

{tools}

Tool names: {tool_names}

Use these tools to process the song lyrics and extract vocabulary.
"""

human_template = """
Find vocabulary from the song: {input}

{agent_scratchpad}
"""

prompt = ChatPromptTemplate.from_messages([
    SystemMessagePromptTemplate.from_template(system_template),
    HumanMessagePromptTemplate.from_template(human_template)
])

# Create the agent
agent = create_react_agent(
    llm=llm,
    tools=tools,
    prompt=prompt,
    output_parser=PydanticOutputParser(pydantic_object=VocabularyResponse)
)
agent_executor = AgentExecutor(agent=agent, tools=tools)

@app.post("/extract_vocabulary", response_model=VocabularyResponse)
async def extract_vocabulary(request: SongRequest):
    try:
        result = agent_executor.invoke({
            "input": request.query
        })
        
        # The agent should return a List[WordInfo]
        if isinstance(result, dict) and 'output' in result:
            result = result['output']
            
        # Ensure we have a List[WordInfo]
        if not isinstance(result, List[WordInfo]):
            # Create a default response if something went wrong
            return VocabularyResponse(
                group_name=request.query,
                words=[]
            )
            
        return VocabularyResponse(
            group_name=request.query,
            words=result
        )
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)
