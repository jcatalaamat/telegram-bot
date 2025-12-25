"""Transcription using OpenAI Whisper API."""

import logging
from dataclasses import dataclass
from pathlib import Path

from openai import OpenAI

from app.config import OPENAI_API_KEY

logger = logging.getLogger(__name__)

# OpenAI client
_client: OpenAI | None = None


def get_client() -> OpenAI:
    """Get or initialize the OpenAI client."""
    global _client

    if _client is None:
        logger.info("Initializing OpenAI client")
        _client = OpenAI(api_key=OPENAI_API_KEY)

    return _client


@dataclass
class TranscriptionResult:
    """Result of transcription."""

    text: str
    language: str
    segments: list[tuple[float, float, str]]  # (start, end, text)


def format_timestamp(seconds: float) -> str:
    """Format seconds as [MM:SS]."""
    minutes = int(seconds // 60)
    secs = int(seconds % 60)
    return f"[{minutes:02d}:{secs:02d}]"


def transcribe_audio(
    audio_path: Path,
    language: str | None = None,
    with_timestamps: bool = False,
) -> TranscriptionResult:
    """Transcribe audio file using OpenAI Whisper API.

    Args:
        audio_path: Path to audio file
        language: Optional language code (e.g., 'en', 'es'). None for auto-detect.
        with_timestamps: Include timestamps in output

    Returns:
        TranscriptionResult with text and metadata
    """
    client = get_client()

    logger.debug(f"Transcribing: {audio_path} (lang={language or 'auto'})")

    with open(audio_path, "rb") as audio_file:
        if with_timestamps:
            # Use verbose_json to get segments with timestamps
            response = client.audio.transcriptions.create(
                model="whisper-1",
                file=audio_file,
                language=language,
                response_format="verbose_json",
            )

            detected_lang = response.language or "unknown"
            segments: list[tuple[float, float, str]] = []
            text_parts: list[str] = []

            for segment in response.segments or []:
                seg_text = segment.get("text", "").strip()
                if not seg_text:
                    continue

                start = segment.get("start", 0)
                end = segment.get("end", 0)
                segments.append((start, end, seg_text))
                text_parts.append(f"{format_timestamp(start)} {seg_text}")

            full_text = "\n".join(text_parts)

        else:
            # Simple transcription without timestamps
            response = client.audio.transcriptions.create(
                model="whisper-1",
                file=audio_file,
                language=language,
                response_format="json",
            )

            full_text = response.text
            detected_lang = "auto"
            segments = []

    logger.info(f"Transcription complete: {len(full_text)} chars, lang={detected_lang}")

    return TranscriptionResult(
        text=full_text,
        language=detected_lang,
        segments=segments,
    )
