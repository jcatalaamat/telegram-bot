"""Telegram bot handlers."""

import logging
from pathlib import Path

from telegram import Update
from telegram.ext import (
    Application,
    CommandHandler,
    ContextTypes,
    MessageHandler,
    filters,
)

from app.audio_utils import (
    cleanup_job_dir,
    convert_to_wav,
    create_job_dir,
    get_audio_duration,
    get_input_path,
    get_wav_path,
)
from app.config import (
    AUDIO_EXTENSIONS,
    AUDIO_MIME_PREFIXES,
    MAX_AUDIO_SECONDS,
    MAX_FILE_MB,
    TELEGRAM_BOT_TOKEN,
)
from app.text_utils import chunk_text, format_duration, parse_options
from app.transcribe import transcribe_audio

logger = logging.getLogger(__name__)

HELP_TEXT = """
I can transcribe voice notes and audio files for you.

*What to send:*
- Voice notes (just record and send)
- Audio files (drag & drop)
- WhatsApp voice exports (.opus, .ogg, .m4a)

*Supported formats:*
.ogg, .opus, .m4a, .mp3, .wav, .mp4, .webm, .mkv

*Options (add to caption):*
- `lang=XX` - Force language (en, es, ca, fr, etc.)
- `timestamps=1` - Include timestamps

*Examples:*
- Send a voice note (auto-detect language)
- Send audio with caption: `lang=es`
- Send file with caption: `timestamps=1 lang=en`

*Limits:*
- Max duration: 10 minutes
- Max file size: 25MB

*Tip:* To export WhatsApp voice messages, long-press the message in WhatsApp and choose "Forward" or "Share", then send it here.
""".strip()


async def start_command(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """Handle /start command."""
    await update.message.reply_text(
        "Hi! I'm a transcription bot.\n\n" + HELP_TEXT,
        parse_mode="Markdown",
    )


async def help_command(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """Handle /help command."""
    await update.message.reply_text(HELP_TEXT, parse_mode="Markdown")


def is_supported_document(doc) -> bool:
    """Check if a document is a supported audio/video file."""
    if doc is None:
        return False

    # Check MIME type
    if doc.mime_type:
        if any(doc.mime_type.startswith(prefix) for prefix in AUDIO_MIME_PREFIXES):
            return True

    # Check file extension
    if doc.file_name:
        ext = Path(doc.file_name).suffix.lower()
        if ext in AUDIO_EXTENSIONS:
            return True

    return False


async def handle_audio(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """Handle voice notes, audio files, and documents."""
    message = update.message
    user = message.from_user
    logger.info(f"Received audio from user {user.id} ({user.username})")

    # Determine the audio source
    if message.voice:
        file_obj = message.voice
        original_filename = None
        caption = None
    elif message.audio:
        file_obj = message.audio
        original_filename = message.audio.file_name
        caption = message.caption
    elif message.document and is_supported_document(message.document):
        file_obj = message.document
        original_filename = message.document.file_name
        caption = message.caption
    else:
        # Unsupported document type
        await message.reply_text(
            "Sorry, I can't process this file type.\n\n" + HELP_TEXT,
            parse_mode="Markdown",
        )
        return

    # Check file size
    if file_obj.file_size and file_obj.file_size > MAX_FILE_MB * 1024 * 1024:
        await message.reply_text(
            f"File is too large. Maximum size is {MAX_FILE_MB}MB."
        )
        return

    # Parse options from caption
    options = parse_options(caption)

    # Create job directory
    job_id, job_dir = create_job_dir()
    logger.info(f"Job {job_id}: Processing audio from user {user.id}")

    try:
        # Send processing message
        status_msg = await message.reply_text("Downloading audio...")

        # Download file
        input_path = get_input_path(job_dir, original_filename)
        tg_file = await file_obj.get_file()
        await tg_file.download_to_drive(input_path)
        logger.debug(f"Job {job_id}: Downloaded to {input_path}")

        # Check duration
        await status_msg.edit_text("Checking audio duration...")
        duration = get_audio_duration(input_path)
        if duration > MAX_AUDIO_SECONDS:
            await status_msg.edit_text(
                f"Audio is too long ({format_duration(duration)}). "
                f"Maximum duration is {format_duration(MAX_AUDIO_SECONDS)}."
            )
            return

        # Convert to WAV
        await status_msg.edit_text("Converting audio...")
        wav_path = get_wav_path(job_dir)
        convert_to_wav(input_path, wav_path)

        # Transcribe
        lang_info = f" (language: {options.language})" if options.language else ""
        await status_msg.edit_text(f"Transcribing{lang_info}...")

        result = transcribe_audio(
            wav_path,
            language=options.language,
            with_timestamps=options.timestamps,
        )

        if not result.text.strip():
            await status_msg.edit_text(
                "No speech detected in the audio. "
                "Please make sure the audio contains clear speech."
            )
            return

        # Send transcription
        await status_msg.delete()

        # Header with metadata
        header = f"Transcription (detected: {result.language})"
        if options.timestamps:
            header += " with timestamps"
        header += ":"

        # Split into chunks if needed
        chunks = chunk_text(result.text)

        for i, chunk in enumerate(chunks):
            if i == 0:
                text = f"{header}\n\n{chunk}"
            else:
                text = chunk

            await message.reply_text(text)

        logger.info(f"Job {job_id}: Sent {len(chunks)} message(s)")

    except Exception as e:
        logger.exception(f"Job {job_id}: Error processing audio")
        await message.reply_text(
            f"Sorry, there was an error processing your audio: {e}\n\n"
            "Please try again or send a different file."
        )

    finally:
        cleanup_job_dir(job_dir)


async def handle_unsupported(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """Handle unsupported message types."""
    await update.message.reply_text(
        "I can only transcribe voice notes and audio files.\n\n" + HELP_TEXT,
        parse_mode="Markdown",
    )


def create_application() -> Application:
    """Create and configure the Telegram application."""
    if not TELEGRAM_BOT_TOKEN:
        raise ValueError("TELEGRAM_BOT_TOKEN environment variable is required")

    app = Application.builder().token(TELEGRAM_BOT_TOKEN).build()

    # Command handlers
    app.add_handler(CommandHandler("start", start_command))
    app.add_handler(CommandHandler("help", help_command))

    # Audio handlers
    app.add_handler(MessageHandler(filters.VOICE, handle_audio))
    app.add_handler(MessageHandler(filters.AUDIO, handle_audio))
    app.add_handler(MessageHandler(filters.Document.ALL, handle_audio))

    # Catch-all for unsupported messages (text, photos, etc.)
    app.add_handler(
        MessageHandler(
            filters.ALL & ~filters.COMMAND & ~filters.VOICE & ~filters.AUDIO & ~filters.Document.ALL,
            handle_unsupported,
        )
    )

    return app
