"""API endpoint for checking a video processing job's status."""

from flask import Blueprint, jsonify, Response
from app.utils.status_store import get_status

status_bp = Blueprint('status', __name__)


@status_bp.route('/status/<job_id>', methods=['GET'])
def check_status(job_id: str) -> tuple[Response, int]:
    """Return the current processing status for a given job_id."""
    job_data = get_status(job_id)

    if job_data is None:
        return jsonify({'error': 'Job ID not found'}), 404

    return jsonify({
        'job_id': job_id,
        'status': job_data['status'],
        'details': job_data['details']
    }), 200