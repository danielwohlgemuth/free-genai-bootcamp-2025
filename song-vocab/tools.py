from langchain.tools import Tool
from typing import Dict, List, Optional
import requests
from pydantic import BaseModel
from bs4 import BeautifulSoup
import os
from dotenv import load_dotenv
from langchain_community.document_loaders import BraveSearchLoader, WebBaseLoader
from langchain_ollama import OllamaLLM
from langchain.output_parsers import PydanticOutputParser
from langchain.prompts import PromptTemplate
from models import WordInfo

# Load environment variables
load_dotenv()
OLLAMA_BASE_URL = os.getenv("OLLAMA_BASE_URL", "http://localhost:11434")
MODEL_NAME = os.getenv("MODEL_NAME", "qwen2.5:3b")

# Initialize LLM
llm = OllamaLLM(
    base_url=OLLAMA_BASE_URL,
    model=MODEL_NAME
)

class LinkRetrieverTool(BaseModel):
    """Tool for retrieving links using Brave Search"""
    def search_lyrics(self, song_name: str) -> List[str]:
        """Search for Japanese lyrics using Brave Search"""
        query = f"{song_name} japanese lyrics"
        loader = BraveSearchLoader(
            query=query,
            max_results=5
        )
        docs = loader.load()
        return [doc.metadata['link'] for doc in docs]

class LyricsRetrieverTool(BaseModel):
    """Tool for retrieving lyrics from web pages"""
    def get_lyrics(self, url: str) -> str:
        """Extract lyrics from a webpage using BeautifulSoup4"""
        loader = WebBaseLoader(
            web_paths=[url],
            bs_kwargs=dict(
                parse_only=BeautifulSoup.SoupStrainer(['p', 'div', 'pre'])
            )
        )
        docs = loader.load()
        return docs[0].page_content if docs else ""

class LyricsExtractorTool(BaseModel):
    """Tool for extracting clean lyrics using LLM"""
    def extract_lyrics(self, raw_text: str) -> str:
        """Use LLM to extract clean lyrics from raw text"""
        prompt = f"""
        Extract only the Japanese lyrics from the following text. 
        Remove any English translations, advertisements, or other content.
        Text: {raw_text}
        
        Japanese Lyrics:
        """
        return llm.invoke(prompt)

class VocabularyExtractorTool(BaseModel):
    """Tool for extracting vocabulary using LLM"""
    def extract_vocabulary(self, lyrics: str) -> List[str]:
        """Extract vocabulary items from lyrics"""
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
        
        try:
            parsed_result = parser.parse(result)
            return parsed_result
        except:
            return []

class VocabularyFilterTool(BaseModel):
    """Tool for filtering to least common words"""
    def filter_vocabulary(self, words: List[str], min_words: int = 3, max_words: int = 10) -> List[str]:
        """Filter to least common words using LLM"""
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

        try:
            parsed_result = parser.parse(result)
            return parsed_result
        except:
            return words[:max_words]  # Fallback to simple truncation

class VocabularyEnhancerTool(BaseModel):
    """Tool for enhancing vocabulary with romaji and English"""
    def enhance_vocabulary(self, words: List[str]) -> List[WordInfo]:
        """Add romaji and English translations"""
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
        
        try:
            parsed_result = parser.parse(result)
            return parsed_result
        except:
            return []

def get_tools() -> List[Tool]:
    link_retriever = LinkRetrieverTool()
    lyrics_retriever = LyricsRetrieverTool()
    lyrics_extractor = LyricsExtractorTool()
    vocab_extractor = VocabularyExtractorTool()
    vocab_filter = VocabularyFilterTool()
    vocab_enhancer = VocabularyEnhancerTool()
    
    return [
        Tool(
            name="search_lyrics_links",
            func=link_retriever.search_lyrics,
            description="Search for Japanese lyrics webpages using Brave Search"
        ),
        Tool(
            name="get_lyrics_from_url",
            func=lyrics_retriever.get_lyrics,
            description="Extract raw text from a lyrics webpage"
        ),
        Tool(
            name="extract_clean_lyrics",
            func=lyrics_extractor.extract_lyrics,
            description="Extract clean Japanese lyrics from raw text"
        ),
        Tool(
            name="extract_vocabulary",
            func=vocab_extractor.extract_vocabulary,
            description="Extract vocabulary items from lyrics"
        ),
        Tool(
            name="filter_vocabulary",
            func=vocab_filter.filter_vocabulary,
            description="Filter to least common and most useful words"
        ),
        Tool(
            name="enhance_vocabulary",
            func=vocab_enhancer.enhance_vocabulary,
            description="Add romaji and English translations to vocabulary"
        )
    ]
