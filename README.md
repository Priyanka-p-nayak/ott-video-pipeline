# OTT Video Transcoding & Analytics Pipeline

A backend system simulating how streaming platforms like Netflix/YouTube process uploaded videos — transcoding them into multiple resolutions for Adaptive Bitrate Streaming, and tracking real-time viewer analytics through an event-driven pipeline.

Built as a 4-week internship project at Infotact Solutions & Co.

---

## Table of Contents
- [Overview](#overview)
- [Tech Stack](#tech-stack)
- [Architecture](#architecture)
- [Setup Instructions](#setup-instructions)
- [API Documentation](#api-documentation)
- [Running Tests](#running-tests)
- [CI/CD](#cicd)
- [Known Limitations](#known-limitations)
- [Project Structure](#project-structure)
- [Weekly Progress Summary](#weekly-progress-summary)

---

## Overview

When a user uploads a video to a streaming platform, the raw file can't be served directly to viewers — it must be compressed and transcoded into multiple resolutions (1080p, 720p, 480p) to support Adaptive Bitrate Streaming for users with varying internet speeds. Platforms also need to track real-time analytics on viewer engagement.

This project implements a high-throughput video transcoding pipeline and streaming analytics engine. It:

1. Accepts video uploads and transcodes them into 1080p, 720p, and 480p using FFmpeg, running as a non-blocking background job
2. Generates a thumbnail preview image from each video
3. Tracks job progress via a status-polling API
4. Receives real-time viewer events (play/pause/buffer/complete) through a Flask API, publishes them to Apache Kafka, and a separate consumer persists them into PostgreSQL
5. Displays aggregated statistics on a live Bootstrap 5 dashboard

---

## Tech Stack

| Component | Technology |
|---|---|
| Backend API | Python, Flask |
| Video Processing | FFmpeg (via `subprocess`) |
| Message Broker | Apache Kafka + Zookeeper |
| Database | PostgreSQL + SQLAlchemy (ORM) |
| Frontend | Bootstrap 5, Bootstrap Icons, Chart.js, Google Fonts |
| Containerization | Docker, Docker Compose |
| Testing | pytest, unittest.mock |
| CI/CD | GitHub Actions (flake8 + pytest) |

---

## Architecture

```
                  ┌─────────────┐
   User Upload →  │  Flask API  │ → saves to uploads/, returns job_id
                  └──────┬──────┘
                         │ triggers background thread
                         ▼
                ┌──────────────────┐
                │  FFmpeg Worker    │ → generates 1080p / 720p / 480p + thumbnail
                └──────────────────┘
                         │
                         ▼
                  job_status.json  ←── polled by GET /status/<job_id>


   Viewer Event → POST /analytics/track → Kafka topic "viewer-events"
                                                    │
                                                    ▼
                                          Standalone Consumer
                                                    │
                                                    ▼
                                    PostgreSQL (viewer_events table)
                                                    │
                                                    ▼
                              GET /stats/summary → Dashboard (Chart.js)
```

**Request flow — Video Upload:**
`POST /upload` → validate → save file in chunks → return `job_id` immediately → background thread runs FFmpeg → status updates through `pending` → `processing` → `completed`/`failed`.

**Request flow — Analytics:**
`POST /analytics/track` → validate JSON → publish to Kafka topic `viewer-events` → standalone consumer reads it → row inserted into PostgreSQL → `GET /stats/summary` aggregates and serves it to the dashboard.

---

## Setup Instructions

### Option A: Full Docker Setup (Recommended)

**Prerequisites:** Docker Desktop installed and running.

```bash
git clone https://github.com/YOUR-USERNAME/ott-video-pipeline.git
cd ott-video-pipeline
docker-compose up --build
```

This single command starts everything: Flask, Kafka, Zookeeper, PostgreSQL, and the analytics consumer.

Visit: **http://127.0.0.1:5000/dashboard**

### Option B: Local Development Setup

**Prerequisites:** Python 3.11+, FFmpeg installed and added to PATH, Docker Desktop (for Kafka/Postgres only).

```bash
# 1. Clone and enter the project
git clone https://github.com/YOUR-USERNAME/ott-video-pipeline.git
cd ott-video-pipeline

# 2. Start Kafka, Zookeeper, and PostgreSQL only
docker-compose up -d zookeeper kafka postgres

# 3. Set up the Python environment
python -m venv venv
venv\Scripts\activate
pip install -r requirements.txt

# 4. Run the Flask app
python run.py

# 5. In a second terminal (with venv activated), run the Kafka consumer
python -m app.analytics.consumer
```

---

## API Documentation

### `POST /upload`
Uploads a video for processing.

**Request:** `multipart/form-data`, field name `video`
**Success Response (201):**
```json
{
  "message": "Upload successful, processing started",
  "job_id": "a3f1c9e2-4b2a-4a1e-9f3d-7c8e2d1b5f6a",
  "filename": "a3f1c9e2-....mp4",
  "size_bytes": 10485760
}
```
**Error Responses:** `400` (validation failure), `413` (file too large), `500` (server error)

---

### `GET /status/<job_id>`
Checks video processing status.

**Success Response (200):**
```json
{
  "job_id": "a3f1c9e2-...",
  "status": "completed",
  "details": {
    "resolutions": {"1080": true, "720": true, "480": true},
    "thumbnail": true
  }
}
```
**Error Response (404):** Job ID not found

---

### `POST /analytics/track`
Records a viewer event and publishes it to Kafka.

**Request:**
```json
{"video_id": "123", "event": "play"}
```
Allowed `event` values: `play`, `pause`, `buffer`, `complete`, `seek`

**Success Response (202):**
```json
{
  "message": "Event recorded",
  "event": {
    "video_id": "123",
    "event": "play",
    "timestamp": "2026-07-15T10:15:30.123456+00:00"
  }
}
```
**Error Responses:** `400` (validation failure), `503` (Kafka unreachable)

---

### `GET /stats/summary`
Returns aggregated analytics for the dashboard.

**Success Response (200):**
```json
{
  "total_videos": 12,
  "total_views": 340,
  "average_watch_time_seconds": 145.2,
  "concurrent_viewers": 3
}
```

---

### `GET /videos/list`
Returns all known video jobs with their current status, used to populate the dashboard's video table.

### `GET /dashboard`
Serves the live analytics dashboard (HTML page).

---

## Running Tests

```bash
pytest -v              # run all unit tests
flake8 app/ tests/      # run the linter (PEP-8 compliance check)
```

Tests use `unittest.mock` to simulate FFmpeg and Kafka, so the full suite runs quickly without needing real running containers. A separate manual end-to-end checklist (`docs/e2e-checklist.md`) verifies the complete live pipeline with real services.

---

## CI/CD

Every push to `main` or any `feature/**` branch, and every Pull Request into `main`, automatically triggers a GitHub Actions workflow (`.github/workflows/python-app.yml`) that:
1. Installs all dependencies from `requirements.txt`
2. Runs `flake8` to enforce PEP-8 style compliance
3. Runs the full `pytest` suite

Results are visible under the repository's **Actions** tab, providing a timestamped, auditable record of code quality across the project's development.

---

## Known Limitations

These are deliberate, documented scope decisions for a 4-week internship timeline:

- **Job status storage** uses a JSON file, not a database table — a beginner-friendly stepping stone chosen before introducing PostgreSQL. A production system would use a proper `jobs` table.
- **Average watch time** is approximated by measuring the time gap between consecutive events per video, not true session-based tracking.
- **Concurrent viewers** is approximated via recent `play` events within a 5-minute window, not live session state (which would require WebSockets or heartbeat pings).
- **Dashboard charts** (views-over-time, event-type breakdown) currently render with placeholder data; wiring them to real grouped SQL queries is a natural next step.
- **Background jobs** use Python's built-in `threading` module rather than a dedicated task queue (e.g., Celery, RQ) — sufficient at this project's scale, but worth revisiting for production-level concurrency.

---

## Project Structure

```
ott-video-pipeline/
│
├── app/
│   ├── routes/            # Flask blueprints: upload, status, analytics, stats, videos, dashboard
│   ├── services/           # (reserved for future business-logic extraction)
│   ├── workers/            # FFmpeg transcoding, thumbnails, background job orchestration
│   ├── analytics/          # Kafka producer, consumer, DB session setup
│   ├── models/              # SQLAlchemy models (ViewerEvent)
│   ├── utils/                # Validators, logging, file handling, status store
│   ├── templates/             # Dashboard HTML (Jinja2)
│   ├── static/                 # CSS/JS for the dashboard
│   └── config.py                # Centralized app configuration
│
├── tests/                  # pytest unit tests (upload, FFmpeg, analytics, producer)
├── .github/workflows/        # GitHub Actions CI pipeline
├── uploads/                   # Raw uploaded videos (gitignored)
├── outputs/                    # Transcoded videos per job (gitignored)
├── thumbnails/                  # Generated thumbnail images (gitignored)
├── logs/                         # Application logs (gitignored)
├── docker-compose.yml
├── Dockerfile
├── requirements.txt
├── .flake8
├── .gitignore
└── README.md
```

---

## Weekly Progress Summary

| Week | Focus | Key Deliverables |
|---|---|---|
| **1** | Flask Upload API | UUID-based uploads, chunked large-file handling, validation, logging, pytest tests |
| **2** | FFmpeg Transcoding | Multi-resolution transcoding, thumbnails, background threading, status tracking, error handling |
| **3** | Kafka Analytics Pipeline | Kafka + Zookeeper (Docker), `/analytics/track` producer, standalone consumer, PostgreSQL storage |
| **4** | Dashboard & DevOps | Stats aggregation API, Bootstrap 5 + Chart.js dashboard, full Docker Compose stack, GitHub Actions CI |

---

## Author

Built by [Your Name] as part of the Software Engineering Internship at Infotact Solutions & Co.