"""Reusable validation functions for incoming uploads."""

from app.config import ALLOWED_EXTENSIONS


def is_allowed_extension(filename):
    """Return True if the filename ends in an allowed video extension."""
    if '.' not in filename:
        return False
    extension = filename.rsplit('.', 1)[1].lower()
    return extension in ALLOWED_EXTENSIONS


def get_extension(filename):
    """Extract and return the lowercase extension of a filename."""
    return filename.rsplit('.', 1)[1].lower()


def validate_upload_request(request_files):
    """
    Run all validation checks on an incoming upload request.
    Returns (is_valid: bool, error_message: str or None, file_obj or None).
    """
    if 'video' not in request_files:
        return False, 'No video file provided', None

    file = request_files['video']

    if file.filename == '':
        return False, 'No file selected', None

    if not is_allowed_extension(file.filename):
        return False, 'Invalid file type. Allowed: mp4, mov, avi, mkv', None

    # Check for an empty (0-byte) file
    file.seek(0, 2)          # move the "read cursor" to the end of the file
    file_size = file.tell()  # tell() reports the current cursor position = file size
    file.seek(0)             # reset cursor back to the start so it can be saved properly later

    if file_size == 0:
        return False, 'Uploaded file is empty', None

    return True, None, file

def check_content_length(request_obj, max_size):
    """
    Reject the upload early based on the Content-Length header,
    before we spend time reading the file body at all.
    Returns (is_valid: bool, error_message: str or None).
    """
    content_length = request_obj.content_length

    if content_length is None:
        # Some clients don't send this header; we allow it through
        # and rely on MAX_CONTENT_LENGTH + chunk reading as backup safety.
        return True, None

    if content_length > max_size:
        return False, f'File too large. Maximum allowed size is {max_size // (1024*1024)}MB'

    return True, None