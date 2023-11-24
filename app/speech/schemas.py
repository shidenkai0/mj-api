from pydantic import ConfigDict, BaseModel
from uuid import UUID


class TTSTranscriptionBase(BaseModel):
    text: str
    voice_preset: str


class TTSTranscriptionCreate(TTSTranscriptionBase):
    pass


class TTSTranscriptionRead(TTSTranscriptionBase):
    id: UUID
    user_id: UUID
    model_config = ConfigDict(from_attributes=True)


class VoicePreset(BaseModel):
    preset_name: str
    display_name: str
