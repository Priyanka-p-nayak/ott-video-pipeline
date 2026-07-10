# OTT Video Transcoding & Analytics Pipeline

A backend system simulating how platforms like Netflix/YouTube process uploaded
videos: transcoding into multiple resolutions and tracking viewer analytics
in real time.

## Tech Stack
- Python 3.x, Flask
- FFmpeg (video transcoding)
- Apache Kafka (event streaming)
- PostgreSQL (data storage)
- Docker & Docker Compose

## Week 1 Progress: Upload API
- ✅ Flask app factory pattern
- ✅ `/upload` endpoint with UUID-based file naming
- ✅ File validation (extension, empty file, size limits)
- ✅ Chunked file saving (memory-safe for large uploads)
- ✅ Centralized logging
- ✅ Unit tests with pytest

## Setup Instructions

1. Clone the repo:
   ```bash
   git clone https://github.com/YOUR-USERNAME/ott-video-pipeline.git
   cd ott-video-pipeline


## Week 2 Progress: FFmpeg Transcoding Worker
- ✅ FFmpeg subprocess wrapper with timeout and error handling
- ✅ Multi-resolution transcoding (1080p, 720p, 480p) per job
- ✅ Thumbnail generation from 5-second mark
- ✅ Background thread processing (non-blocking uploads)
- ✅ Job status tracking (`pending` → `processing` → `completed`/`failed`)
- ✅ Robust error handling: missing files, timeouts, crashes
- ✅ Mocked unit tests for FFmpeg logic

### New Endpoint: `GET /status/<job_id>`
Checks the processing status of a specific video job.

**Success Response (200):**

## Week 3 Concepts: Apache Kafka

Kafka is a distributed message broker that decouples our analytics API from our database. 
It allows the API to respond instantly to viewer events while a separate consumer processes 
them at a sustainable pace, preventing database overload during traffic spikes.

**Key Concepts:**
- **Topic**: A named channel for messages (we will use `viewer-events`).
- **Producer**: Code that sends messages into a topic (our Flask `/analytics/track` endpoint).
- **Consumer**: Code that reads messages from a topic (our standalone Python consumer script).
- **Partition**: Topics are split into parallel "lanes" for scalability. Message order is guaranteed only within a single partition.
- **Offset**: A sequential ID for each message within a partition. It acts like a bookmark, allowing consumers to resume exactly where they left off after a restart.

**Why Kafka instead of writing directly to PostgreSQL?**
Kafka absorbs sudden bursts of high-velocity events (e.g., 1,000+ per second) without 
overwhelming the database or blocking the API's response time. It ensures zero data loss 
even if the database experiences temporary downtime.