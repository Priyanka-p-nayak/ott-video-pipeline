import os
import uuid
from flask import Blueprint, request, jsonify, Response

from app.config import UPLOAD_FOLDER, MAX_CONTENT_LENGTH
from app.utils.validators import validate_upload_request, get_extension, check_content_length
from app.utils.file_handler import save_file_in_chunks
from app.utils.logger import setup_logger

upload_bp = Blueprint('upload', __name__)
logger = setup_logger(__name__)


@upload_bp.route('/upload', methods=['POST'])
def upload_video() -> tuple[Response, int]:
    """Handle incoming video upload requests and save the file to disk."""

    # Step 1: Early rejection based on declared Content-Length
    is_size_ok, size_error = check_content_length(request, MAX_CONTENT_LENGTH)
    if not is_size_ok:
        logger.warning(f"Rejected upload: {size_error}")
        return jsonify({'error': size_error}), 413

    # Step 2: Standard validation
    is_valid, error_message, file = validate_upload_request(request.files)
    if not is_valid:
        logger.warning(f"Rejected upload: {error_message}")
        return jsonify({'error': error_message}), 400

    # Step 3: Build safe filename (Notice the type hints!)
    job_id: str = str(uuid.uuid4())
    extension: str = get_extension(file.filename)
    saved_filename: str = f"{job_id}.{extension}"
    save_path: str = os.path.join(UPLOAD_FOLDER, saved_filename)

    os.makedirs(UPLOAD_FOLDER, exist_ok=True)

    # Step 4: Save the file in chunks
    try:
        total_bytes: int = save_file_in_chunks(file, save_path)
    except Exception as e:
        logger.error(f"Failed to save file for job {job_id}: {str(e)}")
        return jsonify({'error': f'Failed to save file: {str(e)}'}), 500

    logger.info(f"Upload successful: job_id={job_id}, size={total_bytes} bytes")

    return jsonify({
        'message': 'Upload successful',
        'job_id': job_id,
        'filename': saved_filename,
        'size_bytes': total_bytes
    }), 201