from typing import List, Optional
from pydantic import BaseModel, RootModel

class SongRequest(BaseModel):
    query: str

class WordParts(BaseModel):
    type: Optional[str] = None
    formality: Optional[str] = None

class WordInfo(BaseModel):
    japanese: str
    romaji: str
    english: str
    parts: Optional[WordParts] = None

class WordList(RootModel):
    root: List[str]

class WordInfoList(RootModel):
    root: List[WordInfo]

class VocabularyResponse(BaseModel):
    group_name: str
    words: List[WordInfo]
