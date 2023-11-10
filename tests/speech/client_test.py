import pytest
import pytest_asyncio

from unittest.mock import MagicMock, AsyncMock, patch
from app.speech.client import get_tts
from typing import BinaryIO


@pytest.mark.asyncio
async def test_get_tts(patched_tts_client):
    text = "Hello, world!"
    voice_preset = "default"
    resp_data = b"audio data"

    # Call get_tts and assert the response is as expected
    result = await get_tts(text, voice_preset)
    assert result == resp_data

    # Assert the call method was called with the correct arguments
    patched_tts_client.assert_called_once_with("generate", {"text": text, "voice_preset": voice_preset})
