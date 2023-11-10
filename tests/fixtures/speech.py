from typing import AsyncGenerator, BinaryIO
import pytest_asyncio
from app.speech.models import TTSTranscription
from app.user.models import User
from unittest.mock import AsyncMock, MagicMock, patch


@pytest_asyncio.fixture
async def patched_tts_client():
    mock_response = MagicMock(spec=BinaryIO)
    mock_response.read.return_value = b"audio data"

    async_call_mock = AsyncMock(return_value=mock_response)

    with patch('app.speech.client.tts_client') as mock_tts_client:
        mock_tts_client.return_value.call = async_call_mock
        yield async_call_mock


@pytest_asyncio.fixture
async def test_tts_transcription(test_user: User, patched_tts_client) -> AsyncGenerator[TTSTranscription, None]:
    """Create a new TTSTranscription object for testing."""
    tts_transcription = await TTSTranscription.create(
        user_id=test_user.id,
        text="Hello, world!",
        voice_preset="default",
        audio=b"audio data",
    )
    yield tts_transcription
