from pydantic import BaseModel
from typing import Optional, List
from pydantic import Field, ConfigDict

class Empty(BaseModel):
    model_config = ConfigDict(extra="forbid")

class Haiku(BaseModel):
    haiku_id: str
    status: str
    error_message: Optional[str] = None
    haiku_line_en_1: Optional[str] = None
    haiku_line_en_2: Optional[str] = None
    haiku_line_en_3: Optional[str] = None
    image_description_1: Optional[str] = None
    image_description_2: Optional[str] = None
    image_description_3: Optional[str] = None
    image_link_1: Optional[str] = None
    image_link_2: Optional[str] = None
    image_link_3: Optional[str] = None
    haiku_line_ja_1: Optional[str] = None
    haiku_line_ja_2: Optional[str] = None
    haiku_line_ja_3: Optional[str] = None
    audio_link_1: Optional[str] = None
    audio_link_2: Optional[str] = None
    audio_link_3: Optional[str] = None

class Chat(BaseModel):
    chat_id: int
    haiku_id: str
    role: str
    message: str

class SendChatRequest(BaseModel):
    message: str

class SendChatResponse(BaseModel):
    chat: Chat
    haiku: Haiku

class ListHaikusResponse(BaseModel):
    haikus: List[Haiku]

class GetHaikuResponse(BaseModel):
    haiku: Haiku
    chats: List[Chat]

class DeleteHaikuResponse(BaseModel):
    message: str

class UpdateHaiku(BaseModel):
    haiku: List[str] = Field(description="Haiku lines as list of strings")
    haiku_id: str | int = Field(description="Haiku ID as string")
