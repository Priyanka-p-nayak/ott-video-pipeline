"""Orchestrates converting one uploaded video into multiple resolutions."""

import os
from app.config import RESOLUTIONS, OUTPUT_FOLDER
from app.workers.ffmpeg_utils import convert_to_resolution
from app.utils.logger import setup_logger

logger = setup_logger(__name__)


def transcode_all_resolutions(job_id: str, input_path: str) -> dict:
    """
    Convert one input video into all configured resolutions.

    job_id: the unique ID for this upload (used to name the output folder)
    input_path: full path to the original uploaded video

    Returns a dict summarizing which resolutions succeeded and which failed.
    Example: {'1080': True, '720': True, '480': False}
    """
    # Create a dedicated folder for this specific job: outputs/{job_id}/
    job_output_folder = os.path.join(OUTPUT_FOLDER, job_id)
    os.makedirs(job_output_folder, exist_ok=True)

    results = {}

    # Loop through every resolution defined in our config
    for height in RESOLUTIONS:
        output_filename = f"{height}p.mp4"
        output_path = os.path.join(job_output_folder, output_filename)

        logger.info(f"[{job_id}] Starting conversion to {height}p")
        
        # Reuse the FFmpeg utility we built on Day 8!
        success = convert_to_resolution(input_path, output_path, height)
        
        # Store the result (convert integer height to string for JSON compatibility later)
        results[str(height)] = success

        if not success:
            logger.error(f"[{job_id}] Conversion to {height}p FAILED")
        else:
            logger.info(f"[{job_id}] Conversion to {height}p SUCCESS")

    return results