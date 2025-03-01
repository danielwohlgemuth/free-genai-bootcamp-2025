from langchain.tools import Tool, tool
from typing import Dict, List, Optional, Annotated
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
import traceback
import json

# Load environment variables
load_dotenv()
OLLAMA_BASE_URL = os.getenv("OLLAMA_BASE_URL", "http://localhost:11434")
MODEL_NAME = os.getenv("MODEL_NAME", "qwen2.5:3b")

# Initialize LLM
llm = ChatOllama(
    base_url=OLLAMA_BASE_URL,
    model=MODEL_NAME
)

cache_lyrics = {
    "およげ!たいやきくん": """
    およげ!たいやきくん

    まいにち　まいにち　ぼくらはてっぱんの
    うえで　やかれて　いやになっちゃうよ
    あるあさ　ぼくは　みせのおじさんと
    けんかして　うみに　にげこんだのさ
    はじめて　およいだ　うみのそこ
    とっても　きもちが　いいもんだ
    おなかの　あんこが　おもいけど
    うみは　ひろいぜ　こころがはずむ
    ももいろ　サンゴが　てをふって
    ぼくの　およぎを　ながめていたよ

    まいにち　まいにち　たのしいことばかり
    なんぱせんが　ぼくのすみかさ
    ときどき　サメに　いじめられるけど
    そんなときゃ　そうさ　にげるのさ
    いちにち　およげば　はらぺこさ
    めだまも　くるくる　まわっちゃう
    たまには　エビでも　くわなけりゃ
    しおみず　ばかりじゃ　ふやけてしまう
    いわばの　かげから　くいつけば
    それは　ちいさな　つりばりだった

    どんなに　どんなに　もがいても
    ハリが　のどから　とれないよ
    はまべで　みしらぬ　おじさんが
    ぼくを　つりあげ　びっくりしてた
    やっぱり　ぼくは　たいやきさ
    すこし　こげある　たいやきさ
    おじさん　つばを　のみこんで
    ぼくを　うまそうに　たべたのさ
    """
}

@tool("get_lyrics_from_song_name", return_direct=True)
def get_lyrics_from_song_name(song_name: Annotated[str, "Japanese song name"]) -> str:
    """Search for Japanese song lyrics by song name."""
    try:
        print('song_name', song_name)
        if song_name in cache_lyrics:
            return cache_lyrics[song_name]

        query = f"{song_name} japanese lyrics"
        results = DDGS().text(query, max_results=1)
        url = results[0]['href']
        print('url', url)
        
        # Create a SoupStrainer instance
        only_text_tags = SoupStrainer(['p', 'div', 'pre'])
        
        loader = WebBaseLoader(
            web_paths=[url],
            bs_kwargs=dict(
                parse_only=only_text_tags
            )
        )
        docs = loader.load()
        # print('docs', docs)
        raw_text = docs[0].page_content if docs else ""
        # print('raw_text', raw_text)
        prompt = f"""
        Extract only the Japanese lyrics from the following text.
        Remove any English translations, advertisements, or other content.
        Text: {raw_text}
        
        Return only the lyrics, nothing else.
        Japanese Lyrics:
        """
        result = llm.invoke(prompt)
        cache_lyrics[song_name] = result.content
        return result.content
    except Exception as e:
        print(f"Error in get_lyrics_from_song_name: {str(e)}")
        print('Stack trace:', ''.join(traceback.format_tb(e.__traceback__)))
        raise HTTPException(status_code=500, detail=str(e))

@tool("extract_vocabulary", return_direct=True)
def extract_vocabulary(lyrics: Annotated[str, "The lyrics to extract vocabulary from"]) -> WordInfoList:
    """Extract vocabulary items from lyrics. Takes lyrics text as input and returns a list of vocabulary items."""
    try:
        # Early validation of input
        if not lyrics or not lyrics.strip():
            print('Warning: Empty lyrics provided')
            return WordInfoList(root=[])
            
        print('Processing lyrics:', lyrics[:100] + '...' if len(lyrics) > 100 else lyrics)
        
        # Stage 1: Extract unique Japanese words
        parser = PydanticOutputParser(pydantic_object=WordList)
        template = """You are a Japanese language expert. Extract unique Japanese words from these lyrics and return them as a simple list.
        Only include meaningful vocabulary words that would be useful for a Japanese learner.
        Focus on nouns, verbs, and adjectives.
        Do not include particles or grammatical markers.
        If no Japanese words are found, return a

        print('parser.get_format_instructions()', parser.get_format_instructions())ings like this:
        ["word1", "word2", "word3"]
        
        Or if no Japanese words are found:
        []

        Extract the words now:
        """
        prompt = PromptTemplate.from_template(
            template,
            input_variables=["lyrics"],
            partial_variables={"format_instructions": parser.get_format_instructions()}
        )

        print('parser.get_format_instructions()', parser.get_format_instructions())
        
        formatted_prompt = prompt.format(lyrics=lyrics)
        result = llm.invoke(formatted_prompt)
        print('Initial word extraction result:', result.content[:100] + '...' if len(result.content) > 100 else result.content)
        
        try:
            parsed_result = parser.parse(result.content)
            words = parsed_result.root
            if not words:
                print('Warning: No words extracted from lyrics')
                return WordInfoList(root=[])
        except Exception as e:
            print(f'Error parsing initial word list: {str(e)}')
            print('Stack trace:', ''.join(traceback.format_tb(e.__traceback__)))
            print('Raw content:', result.content)
            return WordInfoList(root=[])
            
        # Stage 2: Select least common words
        min_words: int = 3
        max_words: int = 10
        print(f'Filtering {len(words)} words to {min_words}-{max_words} items')
        
        template = """
        From these Japanese words, select the {min_words}-{max_words} least common ones that would be most useful for a Japanese learner.
        Return ONLY a list of strings like this:
        ["word1", "word2", "word3"]

        Words: {words}

        Select the words now:
        """
        prompt = PromptTemplate.from_template(
            template,
            input_variables=["words", "min_words", "max_words"],
            partial_variables={"format_instructions": parser.get_format_instructions()}
        )

        formatted_prompt = prompt.format(words=words, min_words=min_words, max_words=max_words)
        result = llm.invoke(formatted_prompt)
        print('Word filtering result:', result.content[:100] + '...' if len(result.content) > 100 else result.content)

        try:
            parsed_result = parser.parse(result.content)
            words = parsed_result.root
            if not words:
                print('Warning: No words remained after filtering')
                return WordInfoList(root=[])
        except Exception as e:
            print(f'Error parsing filtered word list: {str(e)}')
            print('Stack trace:', ''.join(traceback.format_tb(e.__traceback__)))
            print('Raw content:', result.content)
            return WordInfoList(root=[])

        # Stage 3: Add word details
        print(f'Adding details for {len(words)} words')
            
        template = """
        For these Japanese words: {words}

        Create a list of word details. For each word include:
        - japanese: The word in Japanese
        - romaji: Romaji (in Hepburn style)
        - english: English translation
        - parts: Part of speech and formality level

        Return ONLY a JSON array like this:
        [
            {{
                "japanese": "てっぱん",
                "romaji": "teppan",
                "english": "iron plate",
                "parts": {{"type": "noun", "formality": "neutral"}}
            }}
        ]

        Create the word details now:
        """
        prompt = PromptTemplate.from_template(template)
        
        formatted_prompt = prompt.format(words=words)
        result = llm.invoke(formatted_prompt)
        print('Word details result:', result.content[:100] + '...' if len(result.content) > 100 else result.content)

        try:
            # Parse the JSON response directly
            word_details = json.loads(result.content)
            
            # Validate each word detail against WordInfo model
            validated_words = []
            for detail in word_details:
                try:
                    word_info = WordInfo(
                        japanese=detail["japanese"],
                        romaji=detail["romaji"],
                        english=detail["english"],
                        parts=WordParts(**detail.get("parts", {})) if detail.get("parts") else None
                    )
                    validated_words.append(word_info)
                except Exception as e:
                    print(f"Error validating word detail: {detail}")
                    print(f"Error: {str(e)}")
                    continue
            
            if not validated_words:
                print('Warning: No valid word details were generated')
                return WordInfoList(root=[])
                
            print(f'Successfully processed {len(validated_words)} words')
            return WordInfoList(root=validated_words)
            
        except Exception as e:
            print(f'Error in extract_vocabulary: {str(e)}')
            print('Stack trace:', ''.join(traceback.format_tb(e.__traceback__)))
            return WordInfoList(root=[])
            
    except Exception as e:
        print(f'Unexpected error in extract_vocabulary: {str(e)}')
        print('Stack trace:', ''.join(traceback.format_tb(e.__traceback__)))
        return WordInfoList(root=[])

def get_tools() -> List[Tool]:
    return [
        get_lyrics_from_song_name,  
        extract_vocabulary,
    ]
