import os
import random
import requests
import traceback
from bs4 import BeautifulSoup, SoupStrainer
from dotenv import load_dotenv
from duckduckgo_search import DDGS
from fastapi import HTTPException
from langchain_community.document_loaders import WebBaseLoader
from langchain_ollama import OllamaLLM
from langchain.output_parsers import PydanticOutputParser
from langchain.prompts import PromptTemplate
from langchain.tools import tool
from models import State, StringList, VocabularyResponse


# Load environment variables
load_dotenv()
OLLAMA_BASE_URL = os.getenv("OLLAMA_BASE_URL", "http://localhost:11434")
MODEL_NAME = os.getenv("MODEL_NAME", "qwen2.5:7b")

# Initialize LLM
llm = OllamaLLM(
    base_url=OLLAMA_BASE_URL,
    model=MODEL_NAME
)


def search_lyrics(state: State):
    """Search for Japanese song lyrics by song name."""
    try:
        query = f"{state['song_name']} japanese lyrics"
        results = DDGS().text(query, max_results=1)
        urls = [result['href'] for result in results]
        return { "lyrics_urls": urls }

    except Exception as e:
        print(f"Error in search_lyrics: {str(e)}")
        print('Stack trace:', ''.join(traceback.format_tb(e.__traceback__)))
        raise HTTPException(status_code=500, detail=str(e))

def get_lyrics(state: State):
    """Extract lyrics from a webpage"""
    try:
        lyrics_url = random.choice(state['lyrics_urls'])

        # Create a SoupStrainer instance
        only_text_tags = SoupStrainer(['p', 'div', 'pre'])
        loader = WebBaseLoader(
            web_paths=[lyrics_url],
            bs_kwargs=dict(
                parse_only=only_text_tags
            )
        )
        docs = loader.load()
        lyrics = docs[0].page_content if docs else ""
        return { "lyrics": lyrics }

    except Exception as e:
        print(f"Error in get_lyrics: {str(e)}")
        print('Stack trace:', ''.join(traceback.format_tb(e.__traceback__)))
        raise HTTPException(status_code=500, detail=str(e))

def extract_lyrics(state: State):
    """Use LLM to extract clean lyrics from raw text"""
    try:
        prompt = PromptTemplate.from_template(
            """
            Extract only the Japanese lyrics from the following text.
            Remove any English translations, advertisements, or other content.
            Text: {raw_text}
            
            Return only the lyrics, nothing else.
            """
        )

        formatted_prompt = prompt.format(raw_text=state['lyrics'])
        result = llm.invoke(formatted_prompt)

        return { "lyrics": result }

    except Exception as e:
        print(f"Error in extract_lyrics: {str(e)}")
        print('Stack trace:', ''.join(traceback.format_tb(e.__traceback__)))
        raise HTTPException(status_code=500, detail=str(e))

def extract_vocabulary(state: State):
    """Extract vocabulary items from lyrics"""
    try:
        # Create a parser for our expected output format
        parser = PydanticOutputParser(pydantic_object=StringList)
        
        prompt = PromptTemplate.from_template(
            """
            Extract unique Japanese words from these lyrics:
            {lyrics}
            
            {format_instructions}
            Return only the JSON object, nothing else.
            """,
            partial_variables={"format_instructions": parser.get_format_instructions()}
        )
        
        formatted_prompt = prompt.format(lyrics=state['lyrics'])
        result = llm.invoke(formatted_prompt)
        print("result", result)
        result = result.replace('}', '')
        print("result", result)
        
        parsed_result = parser.parse(result)
        print("parsed_result", parsed_result)
        return { "vocabulary": parsed_result }
    
    except Exception as e:
        print(f"Error in extract_vocabulary: {str(e)}")
        print('Stack trace:', ''.join(traceback.format_tb(e.__traceback__)))
        raise HTTPException(status_code=500, detail=str(e))

def filter_vocabulary(state: State):
    """Filter to least common words using LLM"""
    try:
        min_words: int = 3
        max_words: int = 10

        # Create a parser for our expected output format
        parser = PydanticOutputParser(pydantic_object=StringList)

        prompt = PromptTemplate.from_template(
            """
            From these Japanese words, select the {min_words}-{max_words} least common ones that would be most useful for a Japanese learner:
            {words}
            
            {format_instructions}
            Return only the JSON object, nothing else.
            """,
            partial_variables={"format_instructions": parser.get_format_instructions()}
        )

        formatted_prompt = prompt.format(words=state['vocabulary'], min_words=min_words, max_words=max_words)
        result = llm.invoke(formatted_prompt)
        print("result", result)

        parsed_result = parser.parse(result)
        print("parsed_result", parsed_result)
        return { "limited_vocabulary": parsed_result }

    except Exception as e:
        print(f"Error in filter_vocabulary: {str(e)}")
        print('Stack trace:', ''.join(traceback.format_tb(e.__traceback__)))
        raise HTTPException(status_code=500, detail=str(e))

def enhance_vocabulary(state: State):
    """Add romaji and English translations"""
    try:
        parser = PydanticOutputParser(pydantic_object=VocabularyResponse)
        
        prompt = PromptTemplate.from_template(
            """
            For each Japanese word, provide:
            - The word in Japanese
            - Romaji (in Hepburn style)
            - English translation
            - Part of speech and formality level
            
            Words: {words}
            
            {format_instructions}
            Return only the JSON object, nothing else.
            """,
            partial_variables={"format_instructions": parser.get_format_instructions()}
        )
        
        formatted_prompt = prompt.format(words=state['limited_vocabulary'])
        result = llm.invoke(formatted_prompt)
        print("result", result)
        
        parsed_result = parser.parse(result)
        print("parsed_result", parsed_result)
        return { "enhanced_vocabulary": parsed_result }
    
    except Exception as e:
        print(f"Error in enhance_vocabulary: {str(e)}")
        print('Stack trace:', ''.join(traceback.format_tb(e.__traceback__)))
        raise HTTPException(status_code=500, detail=str(e))