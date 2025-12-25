FROM python:3.11-slim

# Install ffmpeg and ffprobe
RUN apt-get update && apt-get install -y --no-install-recommends \
    ffmpeg \
    && rm -rf /var/lib/apt/lists/*

# Set working directory
WORKDIR /app

# Copy requirements first for caching
COPY requirements.txt .

# Install Python dependencies
RUN pip install --no-cache-dir -r requirements.txt

# Copy application code
COPY app/ ./app/

# Create temp directory
RUN mkdir -p /tmp/telegram_whisper_bot

# Set environment defaults
ENV PYTHONUNBUFFERED=1
ENV TMP_DIR=/tmp/telegram_whisper_bot

# Run the bot
CMD ["python", "-m", "app.main"]
