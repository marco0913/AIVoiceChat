from pydantic import BaseModel


class LLMRequest(BaseModel):
    text: str
    conversation_id: str | None = None


class LLMResponse(BaseModel):
    text: str
    conversation_id: str | None = None


class TTSRequest(BaseModel):
    text: str


class AudioResponse(BaseModel):
    audio: bytes
    format: str = "mp3"
