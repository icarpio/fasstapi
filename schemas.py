from pydantic import BaseModel

class ChatResponse(BaseModel):
    text: str
    audio_base64: str
