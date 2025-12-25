"""Audio utilities: download paths, ffmpeg conversion, ffprobe duration."""

import logging
import shutil
import subprocess
import uuid
from pathlib import Path

from app.config import TMP_DIR

logger = logging.getLogger(__name__)


def create_job_dir() -> tuple[str, Path]:
    """Create a unique job directory for processing.

    Returns:
        Tuple of (job_id, job_dir_path)
    """
    job_id = str(uuid.uuid4())
    job_dir = TMP_DIR / job_id
    job_dir.mkdir(parents=True, exist_ok=True)
    logger.debug(f"Created job directory: {job_dir}")
    return job_id, job_dir


def cleanup_job_dir(job_dir: Path) -> None:
    """Remove job directory and all contents."""
    try:
        if job_dir.exists():
            shutil.rmtree(job_dir)
            logger.debug(f"Cleaned up job directory: {job_dir}")
    except Exception as e:
        logger.warning(f"Failed to cleanup {job_dir}: {e}")


def get_audio_duration(file_path: Path) -> float:
    """Get audio duration in seconds using ffprobe.

    Args:
        file_path: Path to audio file

    Returns:
        Duration in seconds

    Raises:
        RuntimeError: If ffprobe fails
    """
    try:
        result = subprocess.run(
            [
                "ffprobe",
                "-v", "error",
                "-show_entries", "format=duration",
                "-of", "default=noprint_wrappers=1:nokey=1",
                str(file_path),
            ],
            capture_output=True,
            text=True,
            timeout=30,
        )

        if result.returncode != 0:
            raise RuntimeError(f"ffprobe error: {result.stderr}")

        duration = float(result.stdout.strip())
        logger.debug(f"Audio duration: {duration:.1f}s for {file_path.name}")
        return duration

    except subprocess.TimeoutExpired:
        raise RuntimeError("ffprobe timed out")
    except ValueError as e:
        raise RuntimeError(f"Could not parse duration: {e}")


def convert_to_wav(input_path: Path, output_path: Path) -> None:
    """Convert audio file to WAV format (16kHz, mono) for Whisper.

    Args:
        input_path: Source audio file
        output_path: Destination WAV file

    Raises:
        RuntimeError: If ffmpeg conversion fails
    """
    try:
        result = subprocess.run(
            [
                "ffmpeg",
                "-y",  # Overwrite output
                "-i", str(input_path),
                "-ar", "16000",  # 16kHz sample rate
                "-ac", "1",  # Mono
                "-c:a", "pcm_s16le",  # 16-bit PCM
                str(output_path),
            ],
            capture_output=True,
            text=True,
            timeout=120,
        )

        if result.returncode != 0:
            raise RuntimeError(f"ffmpeg error: {result.stderr}")

        logger.debug(f"Converted to WAV: {output_path}")

    except subprocess.TimeoutExpired:
        raise RuntimeError("Audio conversion timed out")


def get_input_path(job_dir: Path, original_filename: str | None) -> Path:
    """Get the input file path with appropriate extension.

    Args:
        job_dir: Job directory
        original_filename: Original filename (may be None)

    Returns:
        Path for input file
    """
    if original_filename:
        ext = Path(original_filename).suffix.lower() or ".ogg"
    else:
        ext = ".ogg"  # Default for voice notes

    return job_dir / f"input{ext}"


def get_wav_path(job_dir: Path) -> Path:
    """Get the WAV output path."""
    return job_dir / "audio.wav"
