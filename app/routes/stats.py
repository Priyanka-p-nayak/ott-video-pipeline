"""API endpoints for analytics statistics used by the dashboard."""

from datetime import datetime, timedelta, timezone
from flask import Blueprint, jsonify  # type: ignore[import]
from sqlalchemy import func, distinct  # type: ignore[import]

from app.analytics.db import get_session
from app.models.event import ViewerEvent
from app.utils.logger import setup_logger

stats_bp = Blueprint('stats', __name__)
logger = setup_logger(__name__)

CONCURRENT_WINDOW_MINUTES = 5


@stats_bp.route('/stats/summary', methods=['GET'])
def get_summary_stats() -> tuple[dict, int]:
    """Return overall summary statistics: total videos, views, avg watch time, concurrent viewers."""
    session = get_session()

    try:
        total_videos = session.query(func.count(distinct(ViewerEvent.video_id))).scalar()

        total_views = session.query(func.count(ViewerEvent.id)).filter(
            ViewerEvent.event_type == 'play'
        ).scalar()

        avg_watch_time_seconds = calculate_average_watch_time(session)
        concurrent_viewers = calculate_concurrent_viewers(session)

        return jsonify({
            'total_videos': total_videos or 0,
            'total_views': total_views or 0,
            'average_watch_time_seconds': round(avg_watch_time_seconds, 2),
            'concurrent_viewers': concurrent_viewers
        }), 200

    except Exception as e:
        logger.error(f"Failed to compute summary stats: {str(e)}")
        return jsonify({'error': 'Failed to compute statistics'}), 500

    finally:
        session.close()


def calculate_average_watch_time(session) -> float:
    """
    Simplified watch-time calculation: for each video_id, find pairs of
    consecutive events (play -> next event) and average the time gaps.

    NOTE: This is a simplified approximation. A production system would
    track distinct viewing sessions (e.g., via a session_id) for accuracy.
    """
    all_events = session.query(ViewerEvent).order_by(
        ViewerEvent.video_id, ViewerEvent.event_timestamp
    ).all()

    durations = []
    events_by_video = {}

    for event in all_events:
        events_by_video.setdefault(event.video_id, []).append(event)

    for video_id, events in events_by_video.items():
        for i in range(len(events) - 1):
            if events[i].event_type == 'play':
                gap = (events[i + 1].event_timestamp - events[i].event_timestamp).total_seconds()
                if gap > 0:
                    durations.append(gap)

    if not durations:
        return 0.0

    return sum(durations) / len(durations)


def calculate_concurrent_viewers(session) -> int:
    """
    Simplified concurrent-viewer proxy: count distinct video_ids that had
    a 'play' event within the last CONCURRENT_WINDOW_MINUTES minutes.

    NOTE: True concurrency tracking requires live session state (e.g. via
    WebSocket heartbeats), which is out of scope for this project.
    """
    cutoff_time = datetime.now(timezone.utc) - timedelta(minutes=CONCURRENT_WINDOW_MINUTES)

    recent_viewers = session.query(func.count(distinct(ViewerEvent.video_id))).filter(
        ViewerEvent.event_type == 'play',
        ViewerEvent.event_timestamp >= cutoff_time.replace(tzinfo=None)
    ).scalar()

    return recent_viewers or 0