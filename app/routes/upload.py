import os
import uuid
from flask import Blueprint, request, jsonify, Response

from app.config import UPLOAD_FOLDER, MAX_CONTENT_LENGTH
from app.utils.validators import validate_upload_request, get_extension, check_content_length
from app.utils.file_handler import save_file_in_chunks
from app.utils.logger import setup_logger
from app.workers.job_runner import start_background_job
from app.utils.status_store import set_status

upload_bp = Blueprint('upload', __name__)
logger = setup_logger(__name__)


@upload_bp.route('/upload', methods=['POST'])
def upload_video() -> tuple[Response, int]:
    """Handle incoming video upload requests, save the file, and trigger processing."""

    # Step 1: Early rejection based on Content-Length
    is_size_ok, size_error = check_content_length(request, MAX_CONTENT_LENGTH)
    if not is_size_ok:
        logger.warning(f"Rejected upload: {size_error}")
        return jsonify({'error': size_error}), 413

    # Step 2: Standard validation
    is_valid, error_message, file = validate_upload_request(request.files)
    if not is_valid:
        logger.warning(f"Rejected upload: {error_message}")
        return jsonify({'error': error_message}), 400

    # Step 3: Build safe filename and save path
    job_id: str = str(uuid.uuid4())
    extension: str = get_extension(file.filename)
    saved_filename: str = f"{job_id}.{extension}"
    save_path: str = os.path.join(UPLOAD_FOLDER, saved_filename)

    os.makedirs(UPLOAD_FOLDER, exist_ok=True)

    # Step 4: Save the file in chunks (memory-safe)
    try:
        total_bytes: int = save_file_in_chunks(file, save_path)
    except Exception as e:
        logger.error(f"Failed to save file for job {job_id}: {str(e)}")
        return jsonify({'error': f'Failed to save file: {str(e)}'}), 500

    logger.info(f"Upload successful: job_id={job_id}, size={total_bytes} bytes")

   # Set initial status
    set_status(job_id, 'pending', {'message': 'Upload received, processing queued'})
   
   # Trigger background processing
    start_background_job(job_id, save_path)

    # Return the response to the user instantly
    return jsonify({
        'message': 'Upload successful, processing started',
        'job_id': job_id,
        'filename': saved_filename,
        'size_bytes': total_bytes
    }), 201