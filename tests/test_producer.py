"""Unit tests for the Kafka producer, using mocking to avoid needing
a real running Kafka broker during test runs."""

from unittest.mock import patch, MagicMock
from app.analytics.producer import send_event

@patch('app.analytics.producer.get_producer')
def test_send_event_success(mock_get_producer):
    """If Kafka acknowledges the send, send_event should return True."""
    mock_producer = MagicMock()
    mock_future = MagicMock()
    mock_result = MagicMock()
    mock_result.topic = 'viewer-events'
    mock_result.partition = 0
    mock_result.offset = 5

    mock_future.get.return_value = mock_result
    mock_producer.send.return_value = mock_future
    mock_get_producer.return_value = mock_producer

    success = send_event({"video_id": "123", "event": "play"})

    assert success is True
    mock_producer.send.assert_called_once()

@patch('app.analytics.producer.get_producer')
def test_send_event_failure(mock_get_producer):
    """If Kafka raises an exception, send_event should return False, not crash."""
    mock_producer = MagicMock()
    mock_producer.send.side_effect = Exception("Kafka broker unreachable")
    mock_get_producer.return_value = mock_producer

    success = send_event({"video_id": "123", "event": "play"})

    assert success is False