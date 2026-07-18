import os

MAX_CONTENT_LENGTH = 500 * 1024 * 1024
UPLOAD_FOLDER = 'uploads'
ALLOWED_EXTENSIONS = {'mp4', 'mov', 'avi', 'mkv'}
RESOLUTIONS = [1080, 720, 480]
OUTPUT_FOLDER = 'outputs'
THUMBNAIL_FOLDER = 'thumbnails'
THUMBNAIL_TIMESTAMP_SECONDS = 5
JOB_STATUS_FILE = 'job_status.json'

# Env vars let Docker override these local defaults
KAFKA_BOOTSTRAP_SERVERS = os.environ.get('KAFKA_BOOTSTRAP_SERVERS', 'localhost:9092')
KAFKA_TOPIC_VIEWER_EVENTS = 'viewer-events'
ALLOWED_EVENT_TYPES = {'play', 'pause', 'buffer', 'complete', 'seek'}

DATABASE_URL = os.environ.get(
    'DATABASE_URL',
    'postgresql://ott_user:ott_password@localhost:5432/ott_pipeline'
)
