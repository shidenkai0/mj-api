from pydantic import BaseModel
from uuid import UUID


class TTSTranscriptionBase(BaseModel):
    text: str
    voice_preset: str


class TTSTranscriptionCreate(TTSTranscriptionBase):
    pass


class TTSTranscriptionRead(TTSTranscriptionBase):
    id: UUID
    user_id: UUID

    class Config:
        orm_mode = True
