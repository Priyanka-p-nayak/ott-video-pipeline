"""Application-wide configuration settings."""

# Maximum allowed upload size: 500 MB
MAX_CONTENT_LENGTH = 500 * 1024 * 1024  # 500 MB in bytes

# Folder where raw uploaded videos are stored
UPLOAD_FOLDER = 'uploads'

# File extensions we trust as valid video files
ALLOWED_EXTENSIONS = {'mp4', 'mov', 'avi', 'mkv'}

# Target resolutions for transcoding (height in pixels)
RESOLUTIONS = [1080, 720, 480]

# Folder where transcoded outputs are stored
OUTPUT_FOLDER = 'outputs'

# Folder where generated thumbnail images are stored
THUMBNAIL_FOLDER = 'thumbnails'

# Timestamp (in seconds) to grab the thumbnail frame from
THUMBNAIL_TIMESTAMP_SECONDS = 5

# File used to persist job status (temporary solution before PostgreSQL in Week 3)
JOB_STATUS_FILE = 'job_status.json'