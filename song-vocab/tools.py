from langchain.tools import tool
from typing import Dict, List, Optional
import requests
from pydantic import BaseModel
import os
from bs4 import BeautifulSoup, SoupStrainer
from duckduckgo_search import DDGS
from dotenv import load_dotenv
from langchain_community.document_loaders import WebBaseLoader
from langchain_ollama import ChatOllama
from langchain.output_parsers import PydanticOutputParser
from langchain.prompts import PromptTemplate
from models import WordInfo, WordList, WordInfoList

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
def search_lyrics(self, song_name: str) -> str:
    """Search for Japanese song lyrics by song name."""
    try:
        query = f"{song_name} japanese lyrics"
        results = DDGS().text(query, max_results=1)
        url = results[0]['href']
        return url
    except Exception as e:
        print(f"Error in search_lyrics: {str(e)}")
        print('Stack trace:', ''.join(traceback.format_tb(e.__traceback__)))
        raise HTTPException(status_code=500, detail=str(e))

@tool
def get_lyrics(self, url: str) -> str:
    """Extract lyrics from a webpage"""
    try:
        # Create a SoupStrainer instance
        only_text_tags = SoupStrainer(['p', 'div', 'pre'])
        loader = WebBaseLoader(
            web_paths=[url],
            bs_kwargs=dict(
                parse_only=only_text_tags
            )
        )
        docs = loader.load()
        return docs[0].page_content if docs else ""
    except Exception as e:
        print(f"Error in get_lyrics: {str(e)}")
        print('Stack trace:', ''.join(traceback.format_tb(e.__traceback__)))
        raise HTTPException(status_code=500, detail=str(e))

@tool
def extract_lyrics(self, raw_text: str) -> str:
    """Use LLM to extract clean lyrics from raw text"""
    try:
        prompt = f"""
        Extract only the Japanese lyrics from the following text. 
        Remove any English translations, advertisements, or other content.
        Text: {raw_text}
        
        Japanese Lyrics:
        """
        return llm.invoke(prompt)
    except Exception as e:
        print(f"Error in extract_lyrics: {str(e)}")
        print('Stack trace:', ''.join(traceback.format_tb(e.__traceback__)))
        raise HTTPException(status_code=500, detail=str(e))

@tool
def extract_vocabulary(self, lyrics: str) -> WordList:
    """Extract vocabulary items from lyrics"""
    try:
        prompt = f"""
        Extract unique Japanese words from these lyrics:
        {lyrics}
        
        For each word, provide:
        - The word in Japanese
        - Its part of speech
        - Its formality level
        
        Format as JSON list of strings.
        """
        result = llm.invoke(prompt)
        return WordList(root=eval(result))
    
    except Exception as e:
        print(f"Error in extract_vocabulary: {str(e)}")
        print('Stack trace:', ''.join(traceback.format_tb(e.__traceback__)))
        raise HTTPException(status_code=500, detail=str(e))

@tool
def filter_vocabulary(self, words: WordList, min_words: int = 3, max_words: int = 10) -> WordList:
    """Filter to least common words using LLM"""
    try:
        prompt = f"""
        From these Japanese words, select the {min_words}-{max_words} least common ones that would be most useful for a Japanese learner:
        {words}
        
        Return only the selected words in the same format.
        """
    result = llm.invoke(prompt)
    return WordList(root=eval(result))

    except Exception as e:
        print(f"Error in filter_vocabulary: {str(e)}")
        print('Stack trace:', ''.join(traceback.format_tb(e.__traceback__)))
        raise HTTPException(status_code=500, detail=str(e))

@tool
def enhance_vocabulary(self, words: WordList) -> WordInfoList:
    """Add romaji and English translations"""
    try:
        prompt = f"""
        For each Japanese word, add:
        - Romaji (in Hepburn style)
        - English translation
        
        Words: {words}
        
        Return as JSON list with all original fields plus romaji and english.
        """
        result = llm.invoke(prompt)
        return WordInfoList(root=eval(result))
    
    except Exception as e:
        print(f"Error in enhance_vocabulary: {str(e)}")
        print('Stack trace:', ''.join(traceback.format_tb(e.__traceback__)))
        raise HTTPException(status_code=500, detail=str(e))