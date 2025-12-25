# Telegram Transcription Bot

A Telegram bot that transcribes voice notes and audio files using faster-whisper (local Whisper implementation). Supports WhatsApp-exported audio files.

## Features

- Transcribe Telegram voice notes
- Transcribe drag/drop audio files (`.ogg`, `.opus`, `.m4a`, `.mp3`, `.wav`, `.mp4`, `.webm`, `.mkv`)
- WhatsApp voice message support (exported `.opus`/`.ogg` files)
- Language detection or manual override (`lang=es|en|ca|fr`)
- Optional timestamps (`timestamps=1`)
- No external API keys required (runs locally with faster-whisper)
- Docker support

## Requirements

- Python 3.11+
- ffmpeg and ffprobe
- ~2GB RAM for the `small` Whisper model

## Quick Start

### 1. Get a Telegram Bot Token

1. Message [@BotFather](https://t.me/BotFather) on Telegram
2. Send `/newbot` and follow the prompts
3. Copy the bot token

### 2. Setup Environment

```bash
cp .env.example .env
# Edit .env and add your TELEGRAM_BOT_TOKEN
```

### 3. Run with Docker (Recommended)

```bash
docker-compose up --build
```

### 4. Run Locally (Alternative)

```bash
# Install ffmpeg (macOS)
brew install ffmpeg

# Install ffmpeg (Ubuntu/Debian)
sudo apt-get install ffmpeg

# Create virtual environment
python3.11 -m venv venv
source venv/bin/activate

# Install dependencies
pip install -r requirements.txt

# Run the bot
python -m app.main
```

## Usage

### Send Audio to Transcribe

- **Voice note**: Just record and send a voice message
- **Audio file**: Drag and drop any supported audio file
- **WhatsApp export**: Export voice messages from WhatsApp and send them to the bot

### Options (via caption or text)

| Option | Values | Default | Description |
|--------|--------|---------|-------------|
| `lang` | `es`, `en`, `ca`, `fr`, etc. | auto-detect | Force language |
| `timestamps` | `0`, `1` | `0` | Include timestamps |

**Examples:**
- Send voice note (auto-detect language)
- Send audio file with caption: `lang=es`
- Send document with caption: `timestamps=1 lang=en`

## Configuration

Environment variables (see `.env.example`):

| Variable | Default | Description |
|----------|---------|-------------|
| `TELEGRAM_BOT_TOKEN` | (required) | Your Telegram bot token |
| `WHISPER_MODEL` | `small` | Whisper model: `tiny`, `base`, `small`, `medium`, `large-v3` |
| `WHISPER_DEVICE` | `cpu` | Device: `cpu` or `cuda` |
| `WHISPER_COMPUTE_TYPE` | `int8` | Compute type: `int8`, `float16`, `float32` |
| `MAX_AUDIO_SECONDS` | `600` | Max audio duration (10 minutes) |
| `MAX_FILE_MB` | `25` | Max file size in MB |
| `TMP_DIR` | `/tmp/telegram_whisper_bot` | Temp directory for processing |

## Limits

- Maximum audio duration: 10 minutes (configurable)
- Maximum file size: 25MB (configurable)
- Transcripts split into 3500-char chunks for Telegram

## Project Structure

```
telegram-transcription-bot/
├── README.md
├── .env.example
├── requirements.txt
├── Dockerfile
├── docker-compose.yml
└── app/
    ├── __init__.py
    ├── main.py          # Entrypoint
    ├── config.py        # Environment configuration
    ├── bot.py           # Telegram handlers
    ├── audio_utils.py   # ffmpeg/ffprobe utilities
    ├── transcribe.py    # faster-whisper transcription
    └── text_utils.py    # Option parsing, text chunking
```

## License

MIT
