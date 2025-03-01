from langchain.tools import Tool, tool
from typing import Dict, List, Optional
import requests
from pydantic import BaseModel
import os
from bs4 import BeautifulSoup
from duckduckgo_search import DDGS
from dotenv import load_dotenv
from langchain_community.document_loaders import WebBaseLoader
from langchain_ollama import ChatOllama
from langchain.output_parsers import PydanticOutputParser
from langchain.prompts import PromptTemplate
from models import WordInfo

# Load environment variables
load_dotenv()
OLLAMA_BASE_URL = os.getenv("OLLAMA_BASE_URL", "http://localhost:11434")
MODEL_NAME = os.getenv("MODEL_NAME", "qwen2.5:3b")

# Initialize LLM
llm = ChatOllama(
    base_url=OLLAMA_BASE_URL,
    model=MODEL_NAME
)

@tool
def get_lyrics(song_name: str) -> str:
    """Search and extract Japanese lyrics from a song name"""
    print('song_name', song_name)
    query = f"{song_name} japanese lyrics"
    results = DDGS().text(query, max_results=1)
    url = results[0]['href']
    print('url', url)
    loader = WebBaseLoader(
        web_paths=[url],
        bs_kwargs=dict(
            parse_only=BeautifulSoup.SoupStrainer(['p', 'div', 'pre'])
        )
    )
    docs = loader.load()
    print('docs', docs)
    raw_text = docs[0].page_content if docs else ""
    print('raw_text', raw_text)
    prompt = f"""
    Extract only the Japanese lyrics from the following text. 
    Remove any English translations, advertisements, or other content.
    Text: {raw_text}
    
    Japanese Lyrics:
    """
    result = llm.invoke(prompt)
    print('result', result)
    return result

@tool
def extract_vocabulary(lyrics: str) -> List[str]:
    """Extract vocabulary items from lyrics"""
    print('lyrics', lyrics)
    # Create a parser for our expected output format
    parser = PydanticOutputParser(pydantic_object=List[str])
    
    prompt = PromptTemplate.from_template(
        """
        Extract unique Japanese words from these lyrics:
        {lyrics}
        
        {format_instructions}
        """,
        input_variables=["lyrics"],
        partial_variables={"format_instructions": parser.get_format_instructions()}
    )
    
    formatted_prompt = prompt.format(lyrics=lyrics)
    result = llm.invoke(formatted_prompt)
    print('result', result)
    
    try:
        parsed_result = parser.parse(result)
        print('parsed_result', parsed_result)
        return parsed_result
    except:
        return []

@tool
def filter_vocabulary(words: List[str]) -> List[str]:
    """Filter to least common words using LLM"""
    min_words: int = 3
    max_words: int = 10
    print('words', words)
    # Create a parser for our expected output format
    parser = PydanticOutputParser(pydantic_object=List[str])

    prompt = PromptTemplate.from_template(
        """
        From these Japanese words, select the {min_words}-{max_words} least common ones that would be most useful for a Japanese learner:
        {words}
        
        {format_instructions}
        """,
        input_variables=["words", "min_words", "max_words"],
        partial_variables={"format_instructions": parser.get_format_instructions()}
    )

    formatted_prompt = prompt.format(words=words, min_words=min_words, max_words=max_words)
    result = llm.invoke(formatted_prompt)
    print('result', result)

    try:
        parsed_result = parser.parse(result)
        print('parsed_result', parsed_result)
        return parsed_result
    except:
        return words[:max_words]  # Fallback to simple truncation

@tool
def enhance_vocabulary(words: List[str]) -> List[WordInfo]:
    """Add romaji and English translations"""
    print('words', words)
    # Create a parser for our expected output format
    parser = PydanticOutputParser(pydantic_object=List[WordInfo])
        
    prompt = PromptTemplate.from_template(
        """
        For each Japanese word, provide:
        - The word in Japanese
        - Romaji (in Hepburn style)
        - English translation
        - Part of speech and formality level
        
        Words: {words}
        
        {format_instructions}
        """,
        input_variables=["words"],
        partial_variables={"format_instructions": parser.get_format_instructions()}
    )
    
    formatted_prompt = prompt.format(words=words)
    result = llm.invoke(formatted_prompt)
    print('result', result)

    try:
        parsed_result = parser.parse(result)
        print('parsed_result', parsed_result)
        return parsed_result
    except:
        return []

def get_tools() -> List[Tool]:    
    return [
        Tool(
            name="get_lyrics_from_song_name",
            func=get_lyrics,
            description="Get lyrics text from a song name"
        ),
        Tool(
            name="extract_vocabulary",
            func=extract_vocabulary,
            description="Extract vocabulary items from lyrics"
        ),
        Tool(
            name="filter_vocabulary",
            func=filter_vocabulary,
            description="Filter to least common and most useful words"
        ),
        Tool(
            name="enhance_vocabulary",
            func=enhance_vocabulary,
            description="Add romaji and English translations to vocabulary"
        )
    ]
