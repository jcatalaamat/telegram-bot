"""Environment configuration."""

import os
from pathlib import Path

from dotenv import load_dotenv

load_dotenv()


# Telegram
TELEGRAM_BOT_TOKEN: str = os.getenv("TELEGRAM_BOT_TOKEN", "")

# OpenAI
OPENAI_API_KEY: str = os.getenv("OPENAI_API_KEY", "")

# Limits
MAX_AUDIO_SECONDS: int = int(os.getenv("MAX_AUDIO_SECONDS", "600"))
MAX_FILE_MB: int = int(os.getenv("MAX_FILE_MB", "25"))

# Temp directory
TMP_DIR: Path = Path(os.getenv("TMP_DIR", "/tmp/telegram_whisper_bot"))

# Supported audio extensions
AUDIO_EXTENSIONS: set[str] = {".ogg", ".opus", ".m4a", ".mp3", ".wav", ".mp4", ".webm", ".mkv"}

# Supported MIME prefixes
AUDIO_MIME_PREFIXES: tuple[str, ...] = ("audio/", "video/")
