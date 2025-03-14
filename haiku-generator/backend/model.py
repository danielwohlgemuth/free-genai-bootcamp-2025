from pydantic import BaseModel
from typing import Optional, List
from pydantic import Field, ConfigDict

class Empty(BaseModel):
    model_config = ConfigDict(extra="forbid")

class Haiku(BaseModel):
    haiku_id: str
    status: str
    error_message: Optional[str]
    haiku_line_en_1: Optional[str]
    haiku_line_en_2: Optional[str]
    haiku_line_en_3: Optional[str]
    image_description_1: Optional[str]
    image_description_2: Optional[str]
    image_description_3: Optional[str]
    image_link_1: Optional[str]
    image_link_2: Optional[str]
    image_link_3: Optional[str]
    haiku_line_ja_1: Optional[str]
    haiku_line_ja_2: Optional[str]
    haiku_line_ja_3: Optional[str]
    audio_link_1: Optional[str]
    audio_link_2: Optional[str]
    audio_link_3: Optional[str]

class Chat(BaseModel):
    chat_id: int
    haiku_id: str
    role: str
    message: str

class InteractWithChatbotRequest(BaseModel):
    message: str

class InteractWithChatbotResponse(BaseModel):
    chat: Chat
    haiku: Haiku

class ListHaikusResponse(BaseModel):
    haikus: List[Haiku]

class GetHaikuResponse(BaseModel):
    haiku: Haiku | Empty
    chats: List[Chat]

class DeleteHaikuResponse(BaseModel):
    message: str

class UpdateHaiku(BaseModel):
    haiku: List[str] = Field(description="Haiku lines as list of strings")
    haiku_id: str | int = Field(description="Haiku ID as string")
