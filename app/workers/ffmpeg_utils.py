"""Utilities for running FFmpeg commands via Python's subprocess module."""

import subprocess
import os
from app.utils.logger import setup_logger

logger = setup_logger(__name__)


def convert_to_resolution(input_path: str, output_path: str, height: int) -> bool:
    """
    Convert a video to a specific resolution (height in pixels) using FFmpeg.
    Returns True if conversion succeeded, False if it failed for any reason.
    """
    # Safety Check 1: Does the input file exist?
    if not os.path.exists(input_path):
        logger.error(f"Input file does not exist: {input_path}")
        return False

    # Safety Check 2: Is the file empty?
    if os.path.getsize(input_path) == 0:
        logger.error(f"Input file is empty (0 bytes): {input_path}")
        return False

    command = [
        'ffmpeg',
        '-i', input_path,
        '-vf', f'scale=-2:{height}',
        '-c:v', 'libx264',
        '-preset', 'fast',
        '-crf', '23',
        '-y',
        output_path
    ]

    logger.info(f"Running FFmpeg command: {' '.join(command)}")

    try:
        result = subprocess.run(
            command,
            capture_output=True,
            text=True,
            timeout=300  # 5-minute safety timeout per resolution
        )
    except subprocess.TimeoutExpired:
        logger.error(f"FFmpeg timed out after 300s for {input_path} at {height}p")
        return False
    except FileNotFoundError:
        logger.error("FFmpeg executable not found. Is it installed and on PATH?")
        return False
    except Exception as e:
        logger.error(f"Unexpected error running FFmpeg: {str(e)}")
        return False

    # Check if FFmpeg reported success
    if result.returncode != 0:
        logger.error(f"FFmpeg failed for {input_path} at {height}p: {result.stderr}")
        return False

    # Safety Check 3: Did FFmpeg actually create the output file?
    if not os.path.exists(output_path) or os.path.getsize(output_path) == 0:
        logger.error(f"FFmpeg reported success but output is missing/empty: {output_path}")
        return False

    logger.info(f"Successfully converted {input_path} to {height}p at {output_path}")
    return True