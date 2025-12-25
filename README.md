# Telegram Transcription Bot

A Telegram bot that transcribes voice notes and audio files using OpenAI's Whisper API. Supports WhatsApp-exported audio files.

## Features

- Transcribe Telegram voice notes
- Transcribe drag/drop audio files (`.ogg`, `.opus`, `.m4a`, `.mp3`, `.wav`, `.mp4`, `.webm`, `.mkv`)
- WhatsApp voice message support (exported `.opus`/`.ogg` files)
- Language detection or manual override (`lang=es|en|ca|fr`)
- Optional timestamps (`timestamps=1`)
- **Free hosting** on Render with webhook mode
- Docker support

## Deploy Free on Render

[![Deploy to Render](https://render.com/images/deploy-to-render-button.svg)](https://render.com/deploy?repo=https://github.com/jcatalaamat/telegram-bot)

### Manual Deploy Steps:

1. Fork this repo
2. Go to [render.com](https://render.com) and sign up (free)
3. Click "New" → "Web Service"
4. Connect your GitHub repo
5. Set environment variables:
   - `TELEGRAM_BOT_TOKEN` - from @BotFather
   - `OPENAI_API_KEY` - from OpenAI
6. Deploy!

The `WEBHOOK_URL` is set automatically by Render.

**Note:** Free tier sleeps after 15 min inactivity. First message after sleep takes ~30s to wake up.

## Run Locally

### 1. Get API Keys

- **Telegram Bot Token**: Message [@BotFather](https://t.me/BotFather) → `/newbot`
- **OpenAI API Key**: [platform.openai.com/api-keys](https://platform.openai.com/api-keys)

### 2. Setup

```bash
cp .env.example .env
# Edit .env and add your tokens
```

### 3. Run with Docker

```bash
docker-compose up --build
```

### 4. Run without Docker

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

### Options (via caption)

| Option | Values | Default | Description |
|--------|--------|---------|-------------|
| `lang` | `es`, `en`, `ca`, `fr`, etc. | auto-detect | Force language |
| `timestamps` | `0`, `1` | `0` | Include timestamps |

**Examples:**
- Send voice note (auto-detect language)
- Send audio file with caption: `lang=es`
- Send document with caption: `timestamps=1 lang=en`

## Configuration

| Variable | Required | Description |
|----------|----------|-------------|
| `TELEGRAM_BOT_TOKEN` | Yes | Your Telegram bot token |
| `OPENAI_API_KEY` | Yes | Your OpenAI API key |
| `WEBHOOK_URL` | For Render | Your app URL (set automatically on Render) |
| `PORT` | No | Server port (default: 8080) |
| `MAX_AUDIO_SECONDS` | No | Max duration in seconds (default: 600) |
| `MAX_FILE_MB` | No | Max file size in MB (default: 25) |

## Cost

- **Hosting**: Free on Render
- **OpenAI Whisper API**: ~$0.006/minute of audio
  - 10 voice notes/day × 1 min = ~$1.80/month

## License

MIT
