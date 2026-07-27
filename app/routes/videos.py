"""API endpoint listing recent video processing jobs and their status."""

from flask import Blueprint, jsonify  # type: ignore[import]
from app.utils.status_store import get_all_statuses
from app.utils.logger import setup_logger

videos_bp = Blueprint('videos', __name__)
logger = setup_logger(__name__)


@videos_bp.route('/videos/list', methods=['GET'])
def list_videos():
    """Return a list of all known video jobs and their current status."""
    all_statuses = get_all_statuses()

    video_list = []
    for job_id, data in all_statuses.items():
        video_list.append({
            'job_id': job_id,
            'status': data.get('status', 'unknown'),
            'details': data.get('details', {})
        })

    video_list.sort(key=lambda v: v['job_id'], reverse=True)

    return jsonify({'videos': video_list}), 200