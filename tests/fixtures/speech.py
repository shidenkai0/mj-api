from typing import AsyncGenerator, BinaryIO
from httpx import Response
import pytest_asyncio
from app.speech.models import TTSTranscription, VoicePreset
from app.user.models import User
from unittest.mock import AsyncMock, MagicMock, patch


@pytest_asyncio.fixture
async def patched_tts_client() -> AsyncGenerator[AsyncMock, None]:
    mock_response = AsyncMock(spec=Response)
    mock_response.status_code = 200
    mock_response.json.return_value = {"output": {"audio_url": "audio data"}}

    mock_client = AsyncMock()
    mock_client.post.return_value = mock_response

    with patch('app.speech.client.tts_client', return_value=mock_client):
        yield mock_client


@pytest_asyncio.fixture
async def test_voice_preset() -> AsyncGenerator[VoicePreset, None]:
    voice_preset = await VoicePreset.create(
        name="default",
        display_name="Default",
        base64="base64",
    )
    yield voice_preset


@pytest_asyncio.fixture
async def test_tts_transcription(
    test_user: User, test_voice_preset: VoicePreset, patched_tts_client
) -> AsyncGenerator[TTSTranscription, None]:
    """Create a new TTSTranscription object for testing."""
    tts_transcription = await TTSTranscription.create(
        user_id=test_user.id,
        text="Hello, world!",
        voice_preset_id=test_voice_preset.id,
        audio=b"audio data",
    )
    yield tts_transcription


@pytest_asyncio.fixture
def mock_get_audio():
    with patch('app.speech.models.get_audio') as mock_audio:
        mock_audio.return_value = b'audio data'
        yield mock_audio
