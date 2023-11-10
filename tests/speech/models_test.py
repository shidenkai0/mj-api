import pytest
from uuid import UUID
from app.speech.models import TTSTranscription
from app.user.models import User
from sqlalchemy.ext.asyncio import AsyncSession
from unittest.mock import patch


@pytest.mark.asyncio
async def test_tts_transcription_create(test_user: User):
    """Test creating a new TTSTranscription object."""
    tts_transcription = await TTSTranscription.create(
        user_id=test_user.id,
        text="Hello, world!",
        voice_preset="default",
        audio=b"audio data",
    )
    assert tts_transcription.id is not None


@pytest.mark.asyncio
async def test_tts_transcription_get(test_tts_transcription: TTSTranscription):
    """Test getting a TTSTranscription object."""
    tts_transcription = await TTSTranscription.get(test_tts_transcription.id)
    assert tts_transcription is not None


@pytest.mark.asyncio
async def test_tts_transcription_get_excludes_soft_deleted(test_tts_transcription: TTSTranscription):
    await TTSTranscription.delete(test_tts_transcription.id, soft=True)
    tts_transcription = await TTSTranscription.get(test_tts_transcription.id)
    assert tts_transcription is None


@pytest.mark.asyncio
async def test_tts_transcription_get_not_found():
    """Test getting a TTSTranscription object that does not exist."""
    tts_transcription = await TTSTranscription.get(UUID(int=0))
    assert tts_transcription is None


@pytest.mark.asyncio
async def test_tts_transcription_delete(async_session: AsyncSession, test_tts_transcription: TTSTranscription):
    """Test deleting a TTSTranscription object."""
    await TTSTranscription.delete(test_tts_transcription.id, soft=False)
    tts_transcription = await async_session.get(TTSTranscription, test_tts_transcription.id)
    assert tts_transcription is None


@pytest.mark.asyncio
async def test_tts_transcription_transcribe(test_user: User):
    """Test transcribing text to speech."""
    # Mock the get_tts function to return a dummy audio data
    with patch("app.speech.models.get_tts", return_value=b"audio data"):
        text = "Hello, world!"
        voice_preset = "default"
        tts_transcription = await TTSTranscription.transcribe(
            user_id=test_user.id, text=text, voice_preset=voice_preset
        )

        assert tts_transcription is not None
        assert tts_transcription.user_id == test_user.id
        assert tts_transcription.voice_preset == voice_preset
        assert tts_transcription.text == text
        assert tts_transcription.audio == b"audio data"
