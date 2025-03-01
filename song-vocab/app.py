from fastapi import FastAPI, HTTPException
from typing import List, Dict
from langchain.agents import AgentExecutor, create_tool_calling_agent
from langchain_ollama import ChatOllama
from langchain.prompts import ChatPromptTemplate, SystemMessagePromptTemplate, HumanMessagePromptTemplate
from langchain.output_parsers import PydanticOutputParser
from tools import get_tools
import os
from dotenv import load_dotenv
from models import SongRequest, VocabularyResponse, WordInfo
import traceback

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
You are a Japanese language expert tasked with extracting vocabulary from song lyrics.
Your goal is to identify and explain key vocabulary that would be useful for Japanese learners.

You have access to the following tools:

{tools}

Tool names: {tool_names}

Use these tools to process the song lyrics and extract vocabulary.

General Instructions:
1. First, use the "get_lyrics_from_song_name" tool with the song name as input.
2. Take the lyrics returned from step 1 and pass them to the "extract_vocabulary" tool using the parameter name "lyrics".

Example tool usage:
1. lyrics = get_lyrics_from_song_name(song_name="Song Title")
2. vocabulary = extract_vocabulary(lyrics=lyrics)

After using the tools, your final response should be a list of WordInfo objects, each containing:
- japanese: The Japanese word or phrase
- romaji: The romanized version
- english: The English translation
- parts: The grammatical parts (e.g. noun, verb, etc.)
"""

human_template = """
Find vocabulary from the song: {input}

{agent_scratchpad}
"""

prompt = ChatPromptTemplate.from_messages([
    SystemMessagePromptTemplate.from_template(system_template, partial_variables={"tools": tools, "tool_names": ", ".join([tool.name for tool in tools])}),
    HumanMessagePromptTemplate.from_template(human_template, input_variables=["input"])
])

# structured_llm = llm.with_structured_output(VocabularyResponse)

# Create the agent
agent = create_tool_calling_agent(
    llm=llm,
    tools=tools,
    prompt=prompt
)
agent_executor = AgentExecutor(agent=agent, tools=tools, verbose=True)

@app.post("/extract_vocabulary", response_model=VocabularyResponse)
async def extract_vocabulary(request: SongRequest):
    try:
        result = agent_executor.invoke({
            "input": request.query
        })

        print('result', result)
        
        # The agent should return a List[WordInfo]
        if isinstance(result, dict) and 'output' in result:
            result = result['output']
            
        # Convert the result to a list of WordInfo objects if it's not already
        if isinstance(result, str):
            # Try to evaluate the string as a Python literal
            import ast
            try:
                result = ast.literal_eval(result)
            except:
                result = []
                
        if not isinstance(result, list):
            result = []
            
        # Ensure each item in the list is a WordInfo object
        word_list = []
        for item in result:
            if isinstance(item, dict):
                try:
                    word_list.append(WordInfo(**item))
                except:
                    continue
            elif isinstance(item, WordInfo):
                word_list.append(item)
                
        return VocabularyResponse(
            group_name=song_request.query,
            words=result.root if isinstance(result, WordInfoList) else []
        )

    except Exception as e:
        print(f"Error in extract_vocabulary: {str(e)}")
        print('Stack trace:', ''.join(traceback.format_tb(e.__traceback__)))
        raise HTTPException(status_code=500, detail=str(e))

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)
