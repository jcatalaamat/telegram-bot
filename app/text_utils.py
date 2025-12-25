"""Text utilities: option parsing and message chunking."""

import re
from dataclasses import dataclass

# Max chars per Telegram message chunk
MAX_CHUNK_SIZE = 3500


@dataclass
class TranscribeOptions:
    """Options parsed from user message."""

    language: str | None = None  # e.g., 'en', 'es', 'ca', 'fr' (source language hint)
    timestamps: bool = False
    translate: str | None = None  # Target language for translation, e.g., 'en', 'es'
    summary: bool = False  # Summarize the transcription
    voice: bool = False  # Reply with voice audio


def parse_options(text: str | None) -> TranscribeOptions:
    """Parse transcription options from caption or message text.

    Supported options:
        lang=XX (source language hint)
        timestamps=1 (include timestamps)
        translate=XX (translate to language)
        summary=1 (summarize the content)
        voice=1 (reply with audio)

    Args:
        text: Caption or message text (may be None)

    Returns:
        TranscribeOptions with parsed values
    """
    options = TranscribeOptions()

    if not text:
        return options

    # Parse language: lang=XX
    lang_match = re.search(r"\blang=(\w{2,3})\b", text, re.IGNORECASE)
    if lang_match:
        options.language = lang_match.group(1).lower()

    # Parse timestamps: timestamps=1
    ts_match = re.search(r"\btimestamps=([01])\b", text, re.IGNORECASE)
    if ts_match:
        options.timestamps = ts_match.group(1) == "1"

    # Parse translate: translate=XX
    translate_match = re.search(r"\btranslate=(\w{2,3})\b", text, re.IGNORECASE)
    if translate_match:
        options.translate = translate_match.group(1).lower()

    # Parse summary: summary=1
    summary_match = re.search(r"\bsummary=([01])\b", text, re.IGNORECASE)
    if summary_match:
        options.summary = summary_match.group(1) == "1"

    # Parse voice: voice=1
    voice_match = re.search(r"\bvoice=([01])\b", text, re.IGNORECASE)
    if voice_match:
        options.voice = voice_match.group(1) == "1"

    return options


def chunk_text(text: str, max_size: int = MAX_CHUNK_SIZE) -> list[str]:
    """Split text into chunks that fit within Telegram message limits.

    Tries to break at paragraph boundaries, then sentence boundaries,
    then word boundaries.

    Args:
        text: Text to split
        max_size: Maximum chars per chunk

    Returns:
        List of text chunks
    """
    if len(text) <= max_size:
        return [text]

    chunks: list[str] = []
    remaining = text

    while remaining:
        if len(remaining) <= max_size:
            chunks.append(remaining)
            break

        # Find a good break point
        chunk = remaining[:max_size]

        # Try to break at paragraph
        break_pos = chunk.rfind("\n\n")
        if break_pos < max_size // 2:
            # Try to break at newline
            break_pos = chunk.rfind("\n")
        if break_pos < max_size // 2:
            # Try to break at sentence
            for punct in [". ", "! ", "? ", "。"]:
                pos = chunk.rfind(punct)
                if pos > max_size // 2:
                    break_pos = pos + 1
                    break
        if break_pos < max_size // 2:
            # Try to break at word
            break_pos = chunk.rfind(" ")
        if break_pos < max_size // 2:
            # Force break at max_size
            break_pos = max_size

        chunks.append(remaining[: break_pos + 1].rstrip())
        remaining = remaining[break_pos + 1 :].lstrip()

    return chunks


def format_duration(seconds: float) -> str:
    """Format duration as human-readable string."""
    if seconds < 60:
        return f"{seconds:.0f}s"
    minutes = int(seconds // 60)
    secs = int(seconds % 60)
    return f"{minutes}m {secs}s"
