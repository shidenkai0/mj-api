from typing import BinaryIO
from bentoml.client import AsyncClient
from app.config import settings


_tts_client = None


async def tts_client():
    global _tts_client
    if not _tts_client and settings.TTS_ENGINE_URL:
        _tts_client = await AsyncClient.from_url(settings.TTS_ENGINE_URL)
    return _tts_client


async def get_tts(text: str, voice_preset: str) -> bytes:
    """Get a text to speech transcription."""
    if not text:
        raise ValueError("Transcription text cannot be empty")

    client = await tts_client()
    response: BinaryIO = await client.call("generate", {"text": text, "voice_preset": f"voice_presets/{voice_preset}"})

    return response.read()
