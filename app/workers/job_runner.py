"""Orchestrates the full background processing job for one uploaded video."""

import threading
from app.workers.transcode_service import transcode_all_resolutions
from app.workers.thumbnail_service import generate_thumbnail
from app.utils.status_store import set_status
from app.utils.logger import setup_logger

logger = setup_logger(__name__)


def process_video_job(job_id: str, input_path: str) -> None:
    """
    Run the full processing pipeline for one video: all resolutions + thumbnail.
    Wrapped in a top-level try/except so that ANY unexpected error still
    results in a 'failed' status being written, instead of leaving the
    job stuck at 'processing' forever.
    """
    try:
        logger.info(f"[{job_id}] Background job started")
        set_status(job_id, 'processing', {'message': 'Transcoding in progress'})

        resolution_results = transcode_all_resolutions(job_id, input_path)
        thumbnail_success = generate_thumbnail(job_id, input_path)

        all_resolutions_ok = all(resolution_results.values())

        if all_resolutions_ok and thumbnail_success:
            logger.info(f"[{job_id}] Background job COMPLETED successfully")
            set_status(job_id, 'completed', {
                'resolutions': resolution_results,
                'thumbnail': thumbnail_success
            })
        else:
            logger.warning(
                f"[{job_id}] Background job finished with issues: "
                f"resolutions={resolution_results}, thumbnail={thumbnail_success}"
            )
            set_status(job_id, 'failed', {
                'resolutions': resolution_results,
                'thumbnail': thumbnail_success,
                'reason': 'One or more processing steps failed. Check server logs.'
            })

    except Exception as e:
        # This is our safety net: catches ANYTHING we didn't anticipate
        # (disk full, permissions error, a bug in our own code, etc.)
        logger.error(f"[{job_id}] Background job CRASHED with unexpected error: {str(e)}")
        set_status(job_id, 'failed', {
            'reason': f'Unexpected server error: {str(e)}'
        })


def start_background_job(job_id: str, input_path: str) -> None:
    """Launch process_video_job() in a separate background thread."""
    thread = threading.Thread(
        target=process_video_job,
        args=(job_id, input_path),
        daemon=True
    )
    thread.start()
    logger.info(f"[{job_id}] Background thread launched")