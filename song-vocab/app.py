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

{{tools}}

Tool names: {{tool_names}}

Use these tools to process the song lyrics and extract vocabulary.

General Instructions:
1. Search for lyrics using the "get_lyrics_from_song_name" tool. This provides a list of urls.
2. Extract vocabulary using the "extract_vocabulary" tool. Use the clean lyrics from step 1.
3. Filter vocabulary using the "filter_vocabulary" tool. Use the vocabulary from step 2.
4. Enhance vocabulary using the "enhance_vocabulary" tool. Use the filtered vocabulary from step 3.

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
    SystemMessagePromptTemplate.from_template(system_template),
    HumanMessagePromptTemplate.from_template(human_template)
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
            group_name=request.query,
            words=word_list
        )
    except Exception as e:
        print(f"Error processing request: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)
