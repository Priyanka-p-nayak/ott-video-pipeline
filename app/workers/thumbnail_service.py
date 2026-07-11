"""Generates a thumbnail image from a video using FFmpeg."""

import subprocess
import os
from app.config import THUMBNAIL_FOLDER, THUMBNAIL_TIMESTAMP_SECONDS
from app.utils.logger import setup_logger

logger = setup_logger(__name__)


def generate_thumbnail(job_id: str, input_path: str) -> bool:
    """
    Extract a single frame from the video at THUMBNAIL_TIMESTAMP_SECONDS
    and save it as a JPG thumbnail named after the job_id.

    Returns True if the thumbnail was created successfully, False otherwise.
    """
    os.makedirs(THUMBNAIL_FOLDER, exist_ok=True)

    # Thumbnails are saved in a flat folder: thumbnails/{job_id}.jpg
    output_path = os.path.join(THUMBNAIL_FOLDER, f"{job_id}.jpg")
    
    # Format the timestamp as HH:MM:SS (e.g., 00:00:05)
    timestamp = f"00:00:{THUMBNAIL_TIMESTAMP_SECONDS:02d}"

    command = [
        'ffmpeg',
        '-ss', timestamp,      # Fast seek to the timestamp
        '-i', input_path,      # Input file
        '-vframes', '1',       # Output exactly 1 video frame
        '-y',                  # Overwrite without asking
        output_path            # Output file
    ]

    logger.info(f"[{job_id}] Generating thumbnail at {timestamp}")

    result = subprocess.run(
        command,
        capture_output=True,
        text=True
    )

    if result.returncode != 0:
        logger.error(f"[{job_id}] Thumbnail generation failed: {result.stderr}")
        return False

    # Extra safety check: ensure the file actually exists on disk
    if not os.path.exists(output_path):
        logger.error(f"[{job_id}] Thumbnail command succeeded but file not found")
        return False

    logger.info(f"[{job_id}] Thumbnail saved at {output_path}")
    return True