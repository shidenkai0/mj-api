from pydantic import ConfigDict, BaseModel
from uuid import UUID


class VoicePresetRead(BaseModel):
    id: UUID
    name: str
    display_name: str


class TTSTranscriptionBase(BaseModel):
    text: str


class TTSTranscriptionCreate(TTSTranscriptionBase):
    voice_preset_id: UUID


class TTSTranscriptionRead(TTSTranscriptionBase):
    id: UUID
    user_id: UUID
    voice_preset: VoicePresetRead
    model_config = ConfigDict(from_attributes=True)
