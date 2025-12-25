"""AI utilities: translation, summarization, text-to-speech."""

import logging
from pathlib import Path

from openai import OpenAI

from app.config import OPENAI_API_KEY

logger = logging.getLogger(__name__)

# Language names for better prompts
LANGUAGE_NAMES = {
    "en": "English",
    "es": "Spanish",
    "ca": "Catalan",
    "fr": "French",
    "de": "German",
    "it": "Italian",
    "pt": "Portuguese",
    "nl": "Dutch",
    "ru": "Russian",
    "zh": "Chinese",
    "ja": "Japanese",
    "ko": "Korean",
    "ar": "Arabic",
}


def get_client() -> OpenAI:
    """Get OpenAI client."""
    return OpenAI(api_key=OPENAI_API_KEY)


def translate_text(text: str, target_lang: str) -> str:
    """Translate text to target language using GPT.

    Args:
        text: Text to translate
        target_lang: Target language code (e.g., 'en', 'es')

    Returns:
        Translated text
    """
    client = get_client()
    lang_name = LANGUAGE_NAMES.get(target_lang, target_lang)

    logger.info(f"Translating to {lang_name}")

    response = client.chat.completions.create(
        model="gpt-4o-mini",
        messages=[
            {
                "role": "system",
                "content": f"You are a translator. Translate the following text to {lang_name}. "
                "Only output the translation, nothing else. Preserve the original formatting.",
            },
            {"role": "user", "content": text},
        ],
        temperature=0.3,
    )

    translated = response.choices[0].message.content.strip()
    logger.info(f"Translation complete: {len(translated)} chars")
    return translated


def summarize_text(text: str) -> str:
    """Summarize text using GPT.

    Args:
        text: Text to summarize

    Returns:
        Summary as bullet points
    """
    client = get_client()

    logger.info("Summarizing text")

    response = client.chat.completions.create(
        model="gpt-4o-mini",
        messages=[
            {
                "role": "system",
                "content": "Summarize the following transcription in bullet points. "
                "Focus on key points, action items, and important information. "
                "Be concise but don't miss anything important. "
                "Use the same language as the input text.",
            },
            {"role": "user", "content": text},
        ],
        temperature=0.5,
    )

    summary = response.choices[0].message.content.strip()
    logger.info(f"Summary complete: {len(summary)} chars")
    return summary


def text_to_speech(text: str, output_path: Path) -> None:
    """Convert text to speech using OpenAI TTS.

    Args:
        text: Text to convert
        output_path: Path to save the audio file
    """
    client = get_client()

    # Truncate if too long (OpenAI TTS has a 4096 char limit)
    if len(text) > 4000:
        text = text[:4000] + "..."
        logger.warning("Text truncated for TTS (max 4096 chars)")

    logger.info(f"Generating speech for {len(text)} chars")

    response = client.audio.speech.create(
        model="tts-1",
        voice="nova",  # Options: alloy, echo, fable, onyx, nova, shimmer
        input=text,
    )

    response.stream_to_file(output_path)
    logger.info(f"Speech saved to {output_path}")
