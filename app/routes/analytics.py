"""API endpoint for receiving viewer analytics events and publishing to Kafka."""

from datetime import datetime, timezone
from flask import Blueprint, request, jsonify  # type: ignore[reportMissingImports]

from app.utils.validators import validate_analytics_event
from app.analytics.producer import send_event
from app.utils.logger import setup_logger

analytics_bp = Blueprint('analytics', __name__)
logger = setup_logger(__name__)


@analytics_bp.route('/analytics/track', methods=['POST'])
def track_event() -> tuple[dict, int]:
    """Receive a viewer event as JSON and publish it to the Kafka topic."""

    # Parse JSON safely. silent=True prevents Flask from crashing on bad JSON
    json_data = request.get_json(silent=True)

    # 1. Validate the incoming payload
    is_valid, error_message = validate_analytics_event(json_data)
    if not is_valid:
        logger.warning(f"Rejected analytics event: {error_message}")
        return jsonify({'error': error_message}), 400

    # 2. Build a clean payload with a server-side UTC timestamp
    event_payload = {
        'video_id': json_data['video_id'],
        'event': json_data['event'],
        'timestamp': datetime.now(timezone.utc).isoformat()
    }

    # 3. Publish to Kafka
    success = send_event(event_payload)

    if not success:
        logger.error(f"Failed to publish event to Kafka: {event_payload}")
        return jsonify({'error': 'Failed to record event, please try again'}), 503

    # 202 Accepted means "we got it and queued it for processing"
    return jsonify({
        'message': 'Event recorded',
        'event': event_payload
    }), 202