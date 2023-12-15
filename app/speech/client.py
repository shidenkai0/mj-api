from app.config import settings
from httpx import AsyncClient, Response


_tts_client = None


async def tts_client() -> AsyncClient:
    global _tts_client
    if not _tts_client and settings.RUNPOD_ENDPOINT_URL:
        _tts_client = await AsyncClient(
            base_url=settings.RUNPOD_ENDPOINT_URL, headers={"Authorization": f"Bearer {settings.RUNPOD_API_KEY}"}
        )
    return _tts_client


class TranscriptionFailedError(Exception):
    pass


async def get_tts(text: str, voice_preset_base64: str) -> str:
    """
    Get a text to speech transcription from the Runpod endpoint.

    Args:
        text (str): Text to transcribe.
        voice_preset_base64 (str): Base64 encoded voice preset.
    Returns:
        str: Signed URL to the transcription audio.
    """
    if not text:
        raise ValueError("Transcription text cannot be empty")

    client = await tts_client()
    if not client:
        raise ValueError("Transcription client not configured")

    response = await client.post(
        "/run", json={"input": {"text_prompt": text, "voice_preset_base64": voice_preset_base64}}
    )

    if response.status_code != 200:
        raise TranscriptionFailedError(f"Transcription failed: {response.text}")

    return response.json()["output"]["audio_url"]
