import pytest
import pytest_asyncio
from unittest.mock import AsyncMock, patch
from app.speech.client import TranscriptionFailedError, get_tts
from httpx import Response


@pytest.mark.asyncio
async def test_get_tts(patched_tts_client):
    text = "Hello, world!"
    voice_preset_base64 = "default_base64"

    # Call get_tts and assert the response is as expected
    result = await get_tts(text, voice_preset_base64)
    assert result == "audio data"

    # Assert the post method was called with the correct arguments
    patched_tts_client.post.assert_called_once_with(
        "/run", json={"input": {"text_prompt": text, "voice_preset_base64": voice_preset_base64}}
    )


# Test for empty text input
@pytest.mark.asyncio
async def test_get_tts_empty_text():
    with pytest.raises(ValueError) as exc_info:
        await get_tts("", "voice_preset_base64")
    assert "Transcription text cannot be empty" in str(exc_info.value)


# Test for transcription failure
@pytest.mark.asyncio
async def test_get_tts_transcription_failure():
    mock_response = AsyncMock(spec=Response)
    mock_response.status_code = 400  # Simulating a failed response
    mock_response.text = "Error message"

    mock_client = AsyncMock()
    mock_client.post.return_value = mock_response

    with patch('app.speech.client.tts_client', return_value=mock_client):
        with pytest.raises(TranscriptionFailedError) as exc_info:
            await get_tts("Hello, world!", "voice_preset_base64")
    assert "Transcription failed: Error message" in str(exc_info.value)
