"""Main entrypoint for the Telegram Transcription Bot."""

import logging
import sys

from app.bot import create_application
from app.config import TMP_DIR, WEBHOOK_URL, PORT


def setup_logging() -> None:
    """Configure logging."""
    logging.basicConfig(
        level=logging.INFO,
        format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
        handlers=[logging.StreamHandler(sys.stdout)],
    )

    # Reduce noise from httpx
    logging.getLogger("httpx").setLevel(logging.WARNING)
    logging.getLogger("httpcore").setLevel(logging.WARNING)


def main() -> None:
    """Run the bot."""
    setup_logging()
    logger = logging.getLogger(__name__)

    # Ensure temp directory exists
    TMP_DIR.mkdir(parents=True, exist_ok=True)

    logger.info("Starting Telegram Transcription Bot (OpenAI Whisper API)")
    logger.info(f"Temp directory: {TMP_DIR}")

    app = create_application()

    if WEBHOOK_URL:
        # Webhook mode for free hosting (Render, Railway, etc.)
        logger.info(f"Running in webhook mode on port {PORT}")
        logger.info(f"Webhook URL: {WEBHOOK_URL}")
        app.run_webhook(
            listen="0.0.0.0",
            port=PORT,
            url_path="webhook",
            webhook_url=f"{WEBHOOK_URL}/webhook",
            allowed_updates=["message"],
        )
    else:
        # Polling mode for local development
        logger.info("Running in polling mode")
        logger.info("Bot is running. Press Ctrl+C to stop.")
        app.run_polling(allowed_updates=["message"])


if __name__ == "__main__":
    main()
