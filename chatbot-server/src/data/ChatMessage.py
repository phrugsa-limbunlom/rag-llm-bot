from pydantic import BaseModel

class ChatMessage(BaseModel):
    user: str
    message: str