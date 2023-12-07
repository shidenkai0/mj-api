import uuid
import sqlalchemy as sa
from typing import Optional, Sequence

from sqlalchemy import UUID, LargeBinary, String, ForeignKey
from app.database import (
    Base,
    DeleteMixin,
    TimestampMixin,
    async_session,
)
from app.speech.client import get_tts
from app.user.models import User
from sqlalchemy.orm import Mapped, mapped_column, relationship
from enum import StrEnum


# # Define the Status Enum
# class TranscriptionStatus(StrEnum):
#     PENDING = "pending"
#     IN_PROGRESS = "in_progress"
#     FAILED = "failed"
#     COMPLETED = "completed"


class VoicePreset(Base, TimestampMixin):
    """
    Represents a voice preset.

    Attributes:
        id (uuid.UUID): The unique identifier for the voice preset.
        name (str): The name of the voice preset.
        display_name (str): The display name of the voice preset.
    """

    __tablename__ = "voice_preset"

    id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)  # type: ignore
    name: Mapped[str] = mapped_column(String, nullable=False, unique=True)
    display_name: Mapped[str] = mapped_column(String, nullable=False)

    def __repr__(self) -> str:
        """
        Return a string representation of the VoicePreset object.

        Returns:
            str: A string representation of the VoicePreset object.
        """
        return f"<VoicePreset(id={self.id}, name={self.name}, display_name={self.display_name})>"

    @classmethod
    async def create(cls, name: str, display_name: str, commit: bool = True) -> "VoicePreset":
        """
        Create a new voice preset.

        Args:
            name (str): The name of the voice preset.
            display_name (str): The display name of the voice preset.
            commit (bool): Whether to commit the new voice preset to the database.

        Returns:
            VoicePreset: The newly created voice preset.
        """
        voice_preset = cls(name=name, display_name=display_name)
        async with async_session() as session:
            if commit:
                session.add(voice_preset)
                await session.commit()
                await session.refresh(voice_preset)
            return voice_preset

    @classmethod
    async def get(cls, voice_preset_id: uuid.UUID) -> Optional["VoicePreset"]:
        """
        Get a voice preset by ID.

        Args:
            voice_preset_id (uuid.UUID): The unique identifier for the voice preset.

        Returns:
            Optional[VoicePreset]: The voice preset, if it exists.
        """
        query = sa.select(cls).where(cls.id == voice_preset_id)
        async with async_session() as session:
            result = await session.execute(query)
            return result.scalars().first()

    @classmethod
    async def get_all(cls) -> Sequence["VoicePreset"]:
        """
        Get all voice presets.

        Returns:
            Sequence[VoicePreset]: The voice presets.
        """
        query = sa.select(cls)
        async with async_session() as session:
            result = await session.execute(query)
            return result.scalars().unique().all()


class TTSTranscription(Base, TimestampMixin, DeleteMixin):
    """
    Represents a text to speech transcription.

    Attributes:
        id (uuid.UUID): The unique identifier for the transcription.
        text (str): The text of the transcription.
        audio (bytes): The audio of the transcription.
    """

    __tablename__ = "tts_transcription"

    id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)  # type: ignore
    user_id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), ForeignKey(User.id), nullable=False)  # type: ignore
    user: Mapped[User] = relationship("User", lazy="joined")
    voice_preset_id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), ForeignKey(VoicePreset.id), nullable=False)  # type: ignore
    voice_preset: Mapped[VoicePreset] = relationship("VoicePreset", lazy="joined")
    text: Mapped[str] = mapped_column(String, nullable=False)
    # status: Mapped[TranscriptionStatus] = mapped_column(String, nullable=False, default=TranscriptionStatus.PENDING)
    audio: Mapped[bytes] = mapped_column(LargeBinary, nullable=False)

    def __repr__(self) -> str:
        """
        Return a string representation of the TTSTranscription object.

        Returns:
            str: A string representation of the TTSTranscription object.
        """
        return f"<TTSTranscription(id={self.id}, status={self.status} text={self.text})>"

    @classmethod
    async def create(
        cls,
        user_id: uuid.UUID,
        text: str,
        voice_preset_id: uuid.UUID,
        audio: bytes,
        # status: TranscriptionStatus = TranscriptionStatus.PENDING,
        commit: bool = True,
    ) -> "TTSTranscription":
        """
        Create a new transcription.

        Args:
            user_id (uuid.UUID): The unique identifier for the user associated with the transcription.
            text (str): The text of the transcription.
            voice_preset (str): The voice preset to use for the transcription.
            audio (bytes): The audio of the transcription.
            commit (bool): Whether to commit the new transcription to the database.

        Returns:
            TTSTranscription: The newly created transcription.
        """
        transcription = cls(user_id=user_id, text=text, voice_preset_id=voice_preset_id, audio=audio)
        async with async_session() as session:
            if commit:
                session.add(transcription)
                await session.commit()
                await session.refresh(transcription)
            return transcription

    @classmethod
    async def get(cls, transcription_id: uuid.UUID) -> Optional["TTSTranscription"]:
        """
        Get a transcription by ID.

        Args:
            transcription_id (uuid.UUID): The unique identifier for the transcription.

        Returns:
            Optional[TTSTranscription]: The transcription, if it exists.
        """
        query = cls.default_query().where(cls.id == transcription_id)
        async with async_session() as session:
            result = await session.execute(query)
            return result.scalars().first()

    @classmethod
    async def get_by_user_id(cls, user_id: uuid.UUID) -> Sequence["TTSTranscription"]:
        """
        Get all transcriptions for a user.

        Args:
            user_id (uuid.UUID): The unique identifier for the user.

        Returns:
            Sequence[TTSTranscription]: The transcriptions for the user.
        """
        query = cls.default_query().where(cls.user_id == user_id)
        async with async_session() as session:
            result = await session.execute(query)
            return result.scalars().unique().all()  # TODO: check how this performs over time

    @classmethod
    async def transcribe(cls, user_id: uuid.UUID, text: str, voice_preset_id: uuid.UUID) -> "TTSTranscription":
        """
        Transcribe text to speech.

        Args:
            user_id (uuid.UUID): The unique identifier for the user.
            text (str): The text to transcribe.
            voice_preset (str): The voice preset to use for the transcription.

        Returns:
            TTSTranscription: The transcription.
        """
        voice_preset = await VoicePreset.get(voice_preset_id)
        if voice_preset is None:
            raise ValueError(f"Voice preset {voice_preset_id} does not exist.")
        audio = await get_tts(text=text, voice_preset=voice_preset.name)
        return await cls.create(user_id=user_id, text=text, voice_preset_id=voice_preset_id, audio=audio, commit=True)
