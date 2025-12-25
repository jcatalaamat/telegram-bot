"""Transcription using faster-whisper."""

import logging
from dataclasses import dataclass
from pathlib import Path

from faster_whisper import WhisperModel

from app.config import WHISPER_COMPUTE_TYPE, WHISPER_DEVICE, WHISPER_MODEL

logger = logging.getLogger(__name__)

# Global model instance (loaded once)
_model: WhisperModel | None = None


def get_model() -> WhisperModel:
    """Get or initialize the Whisper model."""
    global _model

    if _model is None:
        logger.info(
            f"Loading Whisper model: {WHISPER_MODEL} "
            f"(device={WHISPER_DEVICE}, compute_type={WHISPER_COMPUTE_TYPE})"
        )
        _model = WhisperModel(
            WHISPER_MODEL,
            device=WHISPER_DEVICE,
            compute_type=WHISPER_COMPUTE_TYPE,
        )
        logger.info("Whisper model loaded successfully")

    return _model


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
    """Transcribe audio file using faster-whisper.

    Args:
        audio_path: Path to WAV audio file
        language: Optional language code (e.g., 'en', 'es'). None for auto-detect.
        with_timestamps: Include timestamps in output

    Returns:
        TranscriptionResult with text and metadata
    """
    model = get_model()

    logger.debug(f"Transcribing: {audio_path} (lang={language or 'auto'})")

    segments_iter, info = model.transcribe(
        str(audio_path),
        language=language,
        beam_size=5,
        vad_filter=True,
    )

    detected_lang = info.language
    logger.debug(f"Detected language: {detected_lang}")

    segments: list[tuple[float, float, str]] = []
    text_parts: list[str] = []

    for segment in segments_iter:
        seg_text = segment.text.strip()
        if not seg_text:
            continue

        segments.append((segment.start, segment.end, seg_text))

        if with_timestamps:
            text_parts.append(f"{format_timestamp(segment.start)} {seg_text}")
        else:
            text_parts.append(seg_text)

    if with_timestamps:
        full_text = "\n".join(text_parts)
    else:
        full_text = " ".join(text_parts)

    logger.info(f"Transcription complete: {len(full_text)} chars, lang={detected_lang}")

    return TranscriptionResult(
        text=full_text,
        language=detected_lang,
        segments=segments,
    )
