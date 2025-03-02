from pydantic import BaseModel, RootModel
from typing import List, Optional
from typing import TypedDict


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

class WordInfoList(RootModel):
    root: List[WordInfo]

class VocabularyResponse(BaseModel):
    group_name: str
    words: WordInfoList

class StringList(RootModel):
    root: List[str]

# Graph state
class State(TypedDict):
    song_name: str
    lyrics_urls: StringList
    lyrics: str
    vocabulary: StringList
    limited_vocabulary: StringList
    enhanced_vocabulary: VocabularyResponse