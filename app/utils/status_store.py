"""
Simple JSON-file-based storage for job status tracking.

NOTE: This is a temporary solution for Week 2. In Week 3, this will be
replaced by a proper PostgreSQL table once we set up the database.
"""

import json
import os
import threading
from app.config import JOB_STATUS_FILE

# A lock prevents two threads from writing to the file at the exact same moment
_file_lock = threading.Lock()


def _read_all_statuses() -> dict:
    """Read the entire status file and return it as a dict. Returns {} if missing."""
    if not os.path.exists(JOB_STATUS_FILE):
        return {}

    with open(JOB_STATUS_FILE, 'r') as f:
        try:
            return json.load(f)
        except json.JSONDecodeError:
            return {}


def _write_all_statuses(data: dict) -> None:
    """Write the entire status dict back to the file."""
    with open(JOB_STATUS_FILE, 'w') as f:
        json.dump(data, f, indent=2)


def set_status(job_id: str, status: str, details: dict = None) -> None:
    """
    Create or update the status entry for a given job_id.

    status: one of 'pending', 'processing', 'completed', 'failed'
    details: optional extra info, e.g. {'resolutions': {...}, 'thumbnail': True}
    """
    with _file_lock:
        all_statuses = _read_all_statuses()
        all_statuses[job_id] = {
            'status': status,
            'details': details or {}
        }
        _write_all_statuses(all_statuses)


def get_status(job_id: str) -> dict:
    """
    Retrieve the status entry for a given job_id.
    Returns None if the job_id doesn't exist.
    """
    with _file_lock:
        all_statuses = _read_all_statuses()
        return all_statuses.get(job_id)
    