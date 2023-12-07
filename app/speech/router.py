from io import BytesIO
from typing import Annotated, List
from uuid import UUID

from fastapi import APIRouter, Depends, HTTPException, status
from fastapi.responses import StreamingResponse
from app.speech.models import TTSTranscription
from app.speech.schemas import TTSTranscriptionCreate, TTSTranscriptionRead, VoicePreset
from app.user.auth import authenticate_user
from app.user.models import User

router = APIRouter(
    responses={404: {"description": "Not found"}},
    tags=["speech"],
)

TRANSCRIPTION_NOT_FOUND = HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Transcription not found")

ActiveVerifiedUser = Annotated[User, Depends(authenticate_user)]


@router.get(
    "/transcriptions",
    response_model=List[TTSTranscriptionRead],
    responses={status.HTTP_404_NOT_FOUND: {"description": "Transcription not found"}},
)
async def get_transcriptions(user: ActiveVerifiedUser) -> List[TTSTranscriptionRead]:
    transcriptions = await TTSTranscription.get_by_user_id(user_id=user.id)
    return [
        TTSTranscriptionRead(
            id=transcription.id,
            user_id=transcription.user_id,
            text=transcription.text,
            voice_preset=transcription.voice_preset,
        )
        for transcription in transcriptions
    ]


@router.get(
    "/transcription/{transcription_id}",
    response_model=TTSTranscriptionRead,
    responses={status.HTTP_404_NOT_FOUND: {"description": "Transcription not found"}},
)
async def get_transcription(transcription_id: UUID, user: ActiveVerifiedUser) -> TTSTranscriptionRead:
    """Get a transcription by ID."""

    transcription = await TTSTranscription.get(transcription_id)
    if transcription is None:
        raise TRANSCRIPTION_NOT_FOUND
    if transcription.user_id != user.id:
        raise TRANSCRIPTION_NOT_FOUND
    return TTSTranscriptionRead(
        id=transcription.id,
        user_id=transcription.user_id,
        text=transcription.text,
        voice_preset=transcription.voice_preset,
    )


@router.post("/transcription", response_model=TTSTranscriptionRead)
async def new_transcription(user: ActiveVerifiedUser, transcription: TTSTranscriptionCreate) -> TTSTranscriptionRead:
    """Create a new transcription."""
    tts_transcription = await TTSTranscription.transcribe(
        user_id=user.id, text=transcription.text, voice_preset=transcription.voice_preset
    )
    return TTSTranscriptionRead(
        id=tts_transcription.id,
        user_id=user.id,
        text=tts_transcription.text,
        voice_preset=tts_transcription.voice_preset,
    )


@router.get(
    "/transcription/{transcription_id}/download",
    responses={
        200: {
            "description": "Returns the audio content in WAV format.",
            "content": {
                "audio/wav": {
                    "schema": {
                        "type": "string",
                        "format": "binary",
                        "description": "A binary file containing the audio transcription in WAV format.",
                    }
                }
            },
        },
        404: {
            "description": "Transcription not found",
            "content": {"application/json": {"example": {"detail": "Transcription not found"}}},
        },
    },
    response_class=StreamingResponse,
    summary="Download Transcription",
    tags=["Transcription"],
)
async def download_transcription(user: ActiveVerifiedUser, transcription_id: UUID) -> StreamingResponse:
    transcription = await TTSTranscription.get(transcription_id=transcription_id)
    if not transcription:
        raise TRANSCRIPTION_NOT_FOUND
    if transcription.user_id != user.id:
        raise TRANSCRIPTION_NOT_FOUND
    audio_stream = BytesIO(transcription.audio)
    return StreamingResponse(audio_stream, media_type="audio/wav")


VOICE_PRESETS = [
    VoicePreset(name="snoop-dogg-hb-7s", display_name="Snoop Dogg"),
    VoicePreset(name="taylor-1", display_name="Taylor"),
    VoicePreset(name="taylor-2", display_name="Taylor"),
    VoicePreset(name="taylor-3", display_name="Taylor"),
    VoicePreset(name="obama-7s", display_name="Obama"),
]


@router.get("/voice_presets", response_model=List[VoicePreset])
async def get_voice_presets(user: ActiveVerifiedUser) -> List[VoicePreset]:
    return VOICE_PRESETS
