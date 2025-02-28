from langchain.tools import Tool
from typing import Dict, List, Optional
import requests
from pydantic import BaseModel
import re
import json

class LyricSearchTool(BaseModel):
    def search_lyrics(self, song_name: str) -> str:
        """
        Search for Japanese song lyrics using the Genius API.
        Returns the lyrics if found, otherwise returns an error message.
        """
        # Note: In a production environment, this would use the Genius API
        # For demo purposes, we'll return a sample Japanese song lyrics
        sample_lyrics = """
        空が青くて
        雲ひとつない
        そんな日には
        君を思い出す
        """
        return sample_lyrics

class TranslationTool(BaseModel):
    def translate(self, text: str, source_lang: str = "ja", target_lang: str = "en") -> str:
        """
        Translate text between languages using a translation API.
        """
        # Note: In a production environment, this would use a translation API
        # For demo purposes, we'll use a simple dictionary
        translations = {
            "空": "sky",
            "青い": "blue",
            "雲": "cloud",
            "日": "day",
            "君": "you",
            "思い出す": "remember"
        }
        
        # Simple word-by-word translation
        translated = text
        for jp, en in translations.items():
            translated = translated.replace(jp, en)
        return translated

class VocabularyAnalyzer(BaseModel):
    def __init__(self):
        # Sample vocabulary database
        self.vocab_db = {
            "空": {
                "romaji": "sora",
                "english": "sky",
                "parts": {"type": "noun", "formality": "neutral"}
            },
            "青い": {
                "romaji": "aoi",
                "english": "blue",
                "parts": {"type": "i-adjective", "formality": "neutral"}
            },
            "雲": {
                "romaji": "kumo",
                "english": "cloud",
                "parts": {"type": "noun", "formality": "neutral"}
            },
            "思い出す": {
                "romaji": "omoidasu",
                "english": "remember",
                "parts": {"type": "verb", "formality": "casual"}
            }
        }

    def analyze_word(self, word: str) -> Optional[Dict]:
        """
        Analyze a Japanese word and return its components.
        """
        if word in self.vocab_db:
            result = self.vocab_db[word].copy()
            result["japanese"] = word
            return result
        return None

    def extract_vocabulary(self, text: str) -> List[Dict]:
        """
        Extract vocabulary from a text and analyze each word.
        """
        # Simple word extraction using our vocab database
        words = []
        for word in self.vocab_db.keys():
            if word in text:
                analysis = self.analyze_word(word)
                if analysis:
                    words.append(analysis)
        return words

def get_tools() -> List[Tool]:
    lyric_tool = LyricSearchTool()
    translation_tool = TranslationTool()
    vocab_analyzer = VocabularyAnalyzer()
    
    return [
        Tool(
            name="search_lyrics",
            func=lyric_tool.search_lyrics,
            description="Search for Japanese song lyrics by song name"
        ),
        Tool(
            name="translate_text",
            func=translation_tool.translate,
            description="Translate text between Japanese and English"
        ),
        Tool(
            name="analyze_vocabulary",
            func=vocab_analyzer.extract_vocabulary,
            description="Extract and analyze vocabulary from Japanese text"
        )
    ]
