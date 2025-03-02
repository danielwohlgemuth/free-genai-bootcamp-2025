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
system_template = """
You are a Japanese language expert tasked with helping Japanese learners to understand song lyrics.



You must follow this workflow:
1. Use 'get_lyrics_from_song_name' first to retrieve the lyrics.
2. Use 'extract_vocabulary' on the lyrics to extract word details.
3. Return the response as a JSON object: {{"group_name": "...", "words": ["japanese": "...", "romaji": "...", "english": "...", "parts": [{{"type": "...", "formality": "..."}}]]}}
Never skip steps. Only call tools when needed.

Example output format:
{{
    "group_name": "およげ!たいやきくん",
    "words": [
        {{
            "japanese": "およぐ",
            "romaji": "oyogu",
            "english": "to swim",
            "parts": {{
                "type": "verb",
                "formality": "dictionary"
            }}
        }},
        {{
            "japanese": "たいやき",
            "romaji": "taiyaki",
            "english": "fish-shaped cake filled with red bean paste",
            "parts": {{
                "type": "noun",
                "formality": "neutral"
            }}
        }}
    ]
}}
"""

human_template = """
The name of the song is: {input}

{tools}

{tool_names}

{agent_scratchpad}
"""

prompt = ChatPromptTemplate.from_messages([
    SystemMessagePromptTemplate.from_template(system_template),
    HumanMessagePromptTemplate.from_template(human_template, input_variables=["input"])
])

# Create the agent
agent = create_react_agent(
    llm=llm,
    tools=tools,
    prompt=prompt
)

agent_executor = AgentExecutor.from_agent_and_tools(agent=agent, tools=tools, verbose=True)

@app.post("/extract_vocabulary", response_model=VocabularyResponse)
async def extract_vocabulary(request: SongRequest):
    try:
        result = agent_executor.invoke({
            "input": request.query
        })
        # for chunk in agent_executor.stream({
        #     "input": request.query
        # }):
        #     print('chunc', chunk)


        print('result', result)
        
        # # The agent should return a List[WordInfo]
        # if isinstance(result, dict) and 'output' in result:
        #     result = result['output']
            
        # # Convert the result to a list of WordInfo objects if it's not already
        # if isinstance(result, str):
        #     # Try to evaluate the string as a Python literal
        #     import ast
        #     try:
        #         result = ast.literal_eval(result)
        #     except:
        #         result = []
                
        # if not isinstance(result, list):
        #     result = []
            
        # Ensure each item in the list is a WordInfo object
        words = []
        # for item in result:
        #     if isinstance(item, dict):
        #         try:
        #             words.append(WordInfo(**item))
        #         except:
        #             continue
        #     elif isinstance(item, WordInfo):
        #         words.append(item)
                
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
