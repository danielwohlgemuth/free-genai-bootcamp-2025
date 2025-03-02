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

To analyze a song, you should:
1. First get the lyrics using get_lyrics_from_song_name
2. Then extract vocabulary using extract_vocabulary
3. Finally format the results as JSON

IMPORTANT: You must follow this EXACT format:

Question: the input question
Thought: your thoughts about what to do next
Action: the tool to use (either get_lyrics_from_song_name or extract_vocabulary)
Action Input: the input to the tool
Observation: the result
... (continue with Thought/Action/Action Input/Observation as needed)
Final Answer: the final answer

For example:

Question: Find vocabulary from the song およげ!たいやきくん
Thought: I need to get the lyrics first
Action: get_lyrics_from_song_name
Action Input: およげ!たいやきくん
Observation: <lyrics>
Thought: Now I can extract vocabulary from these lyrics
Action: extract_vocabulary
Action Input: <lyrics>
Observation: <vocabulary>
Final Answer: <vocabulary in JSON format>
"""

human_template = """
Question: Find vocabulary from the song {input}

{tools}

{tool_names}

{agent_scratchpad}
"""

prompt = ChatPromptTemplate.from_messages([
    SystemMessagePromptTemplate.from_template(system_template),
    HumanMessagePromptTemplate.from_template(human_template, input_variables=["input", "agent_scratchpad"])
])

# Create the agent
agent = create_react_agent(
    llm=llm,
    tools=tools,
    prompt=prompt
)

agent_executor = AgentExecutor.from_agent_and_tools(agent=agent, tools=tools, verbose=True, handle_parsing_errors=True)

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
