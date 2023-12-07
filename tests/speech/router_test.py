import pytest
from httpx import AsyncClient
from app.speech.models import TTSTranscription, VoicePreset
from app.user.models import User

# Assuming you have similar fixtures for test_user and authenticated_client_user
# which provide a User instance and an authenticated AsyncClient instance respectively.
# The test_tts_transcription fixture is assumed to yield a TTSTranscription instance.


@pytest.mark.asyncio
async def test_get_transcriptions(authenticated_client_user: AsyncClient, test_tts_transcription: TTSTranscription):
    # Test getting a list of TTSTranscription objects by user ID
    response = await authenticated_client_user.get("/transcriptions")
    assert response.status_code == 200
    transcriptions = response.json()
    assert len(transcriptions) > 0  # Assuming there are transcriptions to be returned
    # Verify that the test_tts_transcription is in the returned list
    assert any(t["id"] == str(test_tts_transcription.id) for t in transcriptions)


@pytest.mark.asyncio
async def test_get_transcription(authenticated_client_user: AsyncClient, test_tts_transcription: TTSTranscription):
    # Test getting a TTSTranscription object by ID
    response = await authenticated_client_user.get(f"/transcription/{test_tts_transcription.id}")
    assert response.status_code == 200
    assert response.json()["id"] == str(test_tts_transcription.id)


@pytest.mark.asyncio
async def test_new_transcription(
    authenticated_client_user: AsyncClient, test_user: User, test_voice_preset: VoicePreset, patched_tts_client
):
    # Test creating a new TTSTranscription
    transcription_data = {
        "text": "Sample text",
        "voice_preset_id": str(test_voice_preset.id),
    }
    response = await authenticated_client_user.post("/transcription", json=transcription_data)
    assert response.status_code == 200
    assert response.json()["text"] == transcription_data["text"]


@pytest.mark.asyncio
async def test_download_transcription(authenticated_client_user: AsyncClient, test_tts_transcription: TTSTranscription):
    # Test downloading a TTSTranscription by ID
    response = await authenticated_client_user.get(f"/transcription/{test_tts_transcription.id}/download")
    assert response.status_code == 200
    assert response.headers["content-type"] == "audio/wav"


@pytest.mark.asyncio
async def test_get_voice_presets(authenticated_client_user: AsyncClient, test_voice_preset: VoicePreset):
    # Test getting the list of voice presets
    response = await authenticated_client_user.get("/voice_presets")
    assert response.status_code == 200
    assert response.json() == [
        {
            "id": str(test_voice_preset.id),
            "name": test_voice_preset.name,
            "display_name": test_voice_preset.display_name,
        }
    ]
