"""Unit tests for analytics event validation logic."""

from app.utils.validators import validate_analytics_event

def test_valid_event():
    """A correctly formed event should pass validation."""
    data = {"video_id": "123", "event": "play"}
    is_valid, error = validate_analytics_event(data)
    assert is_valid is True
    assert error is None

def test_missing_video_id():
    """Missing video_id should be rejected."""
    data = {"event": "play"}
    is_valid, error = validate_analytics_event(data)
    assert is_valid is False
    assert error == 'Missing required field: video_id'

def test_missing_event_field():
    """Missing event field should be rejected."""
    data = {"video_id": "123"}
    is_valid, error = validate_analytics_event(data)
    assert is_valid is False
    assert error == 'Missing required field: event'

def test_invalid_event_type():
    """An event type outside the allowed set should be rejected."""
    data = {"video_id": "123", "event": "explode"}
    is_valid, error = validate_analytics_event(data)
    assert is_valid is False
    assert 'event must be one of' in error

def test_non_string_video_id():
    """A non-string video_id (e.g. an integer) should be rejected."""
    data = {"video_id": 123, "event": "play"}
    is_valid, error = validate_analytics_event(data)
    assert is_valid is False
    assert error == 'video_id must be a non-empty string'

def test_null_json_body():
    """A None/malformed JSON body should be rejected."""
    is_valid, error = validate_analytics_event(None)
    assert is_valid is False
    assert error == 'Request body must be valid JSON'