from pydantic import BaseModel, Field
from typing import List, Optional

class ChatMessage(BaseModel):
    role: str # 'user' or 'ai'
    content: str

class ChatRequest(BaseModel):

    client_id: str
    user_id: str
    lat: float
    long: float
    query: str
    history: Optional[List[ChatMessage]] = []




class NearbyItem(BaseModel):
    name: str
    number: Optional[str] = Field(None, alias="phone_number")
    distance: str
    phone_number: Optional[str] = None

    class Config:
        populate_by_name = True

class ChatResponse(BaseModel):
    ai_response: str
    results: List[NearbyItem] = []
