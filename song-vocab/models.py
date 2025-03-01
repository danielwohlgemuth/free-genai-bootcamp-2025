from typing import List, Optional
from pydantic import BaseModel

class SongRequest(BaseModel):
    query: str

class WordParts(BaseModel):
    type: Optional[str]
    formality: Optional[str]

class WordInfo(BaseModel):
    japanese: str
    romaji: str
    english: str
    parts: Optional[WordParts]

class VocabularyResponse(BaseModel):
    group_name: str
    words: List[WordInfo]
