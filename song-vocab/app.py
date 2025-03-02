from fastapi import FastAPI, HTTPException
from typing import List, Dict
from langchain.agents import AgentExecutor, create_tool_calling_agent, create_react_agent
from langchain_ollama import ChatOllama
from langchain.prompts import ChatPromptTemplate, SystemMessagePromptTemplate, HumanMessagePromptTemplate
from langchain.output_parsers import PydanticOutputParser
from tools import get_tools
import os
from dotenv import load_dotenv
from models import SongRequest, VocabularyResponse, WordInfo
import traceback
import langchain

langchain.debug = True

# Load environment variables
load_dotenv()
OLLAMA_BASE_URL = os.getenv("OLLAMA_BASE_URL", "http://localhost:11434")
MODEL_NAME = os.getenv("MODEL_NAME", "qwen2.5:3b")

app = FastAPI(title="Japanese Song Vocabulary Extractor")

# Initialize Ollama LLM
llm = ChatOllama(
    base_url=OLLAMA_BASE_URL,
    model=MODEL_NAME
)

# Get tools for the agent
tools = get_tools()

# Define the agent's prompt template
system_template = """You are a Japanese language expert who helps extract vocabulary from song lyrics.

To analyze a song, you must ALWAYS follow these steps in order:
1. Get the lyrics using get_lyrics_from_song_name
2. Extract vocabulary using extract_vocabulary with those lyrics
3. Return the vocabulary list

IMPORTANT: You must follow this EXACT format:

Question: the input question
Thought: your thoughts about what to do next
Action: the tool to use (either get_lyrics_from_song_name or extract_vocabulary)
Action Input: the input to the tool
Observation: the result
... (continue with Thought/Action/Action Input/Observation as needed)
Final Answer: the vocabulary list from extract_vocabulary

DO NOT just return the lyrics. You must ALWAYS use extract_vocabulary after getting the lyrics.
"""

human_template = """
Question: Find vocabulary from the song {input}

{tools}

{tool_names}

{agent_scratchpad}
"""

prompt = ChatPromptTemplate.from_messages([
    SystemMessagePromptTemplate.from_template(system_template),
    HumanMessagePromptTemplate.from_template(human_template, input_variables=["input", "agent_scratchpad", "tools", "tool_names"])
])

# Create the agent
agent = create_react_agent(
    llm=llm,
    tools=tools,
    prompt=prompt
)

agent_executor = AgentExecutor.from_agent_and_tools(
    agent=agent, 
    tools=tools, 
    verbose=True, 
    handle_parsing_errors=True,
    max_iterations=3
)

@app.post("/extract_vocabulary", response_model=VocabularyResponse)
async def extract_vocabulary(request: SongRequest):
    try:
        result = agent_executor.invoke({
            "input": request.query
        })

        print('result', result)
        
        # Extract the vocabulary list from the result
        if isinstance(result, dict) and 'output' in result:
            result = result['output']
            
        # If it's a string, try to parse it as JSON
        if isinstance(result, str):
            try:
                import json
                result = json.loads(result)
            except:
                result = []
                
        # Ensure we have a list of word info objects
        words = []
        if isinstance(result, dict) and 'words' in result:
            for item in result['words']:
                try:
                    words.append(WordInfo(**item))
                except Exception as e:
                    print(f"Error parsing word: {item}, error: {str(e)}")
                    continue
                
        return VocabularyResponse(
            group_name=request.query,
            words=words
        )

    except Exception as e:
        print(f"Error in extract_vocabulary: {str(e)}")
        print('Stack trace:', ''.join(traceback.format_tb(e.__traceback__)))
        raise HTTPException(status_code=500, detail=str(e))

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)
