"""Unit tests for the /upload API endpoint."""

import io


def test_upload_missing_file(client):
    """Uploading with no 'video' field should return 400."""
    # Simulate a POST request with an empty data payload
    response = client.post('/upload', data={})

    assert response.status_code == 400
    assert response.get_json()['error'] == 'No video file provided'


def test_upload_invalid_extension(client):
    """Uploading a .txt file should be rejected."""
    # Create a fake file in memory using io.BytesIO
    fake_file = (io.BytesIO(b'this is not a video'), 'notes.txt')

    response = client.post(
        '/upload',
        data={'video': fake_file},
        content_type='multipart/form-data'  # Crucial for file uploads!
    )

    assert response.status_code == 400
    assert 'Invalid file type' in response.get_json()['error']


def test_upload_empty_file(client):
    """Uploading a 0-byte file with a valid extension should be rejected."""
    # Create a 0-byte fake file
    fake_file = (io.BytesIO(b''), 'empty.mp4')

    response = client.post(
        '/upload',
        data={'video': fake_file},
        content_type='multipart/form-data'
    )

    assert response.status_code == 400
    assert response.get_json()['error'] == 'Uploaded file is empty'


def test_upload_valid_video(client):
    """Uploading a small valid fake .mp4 file should succeed."""
    # Create fake video bytes (starts with real MP4 magic bytes)
    fake_video_content = b'\x00\x00\x00\x18ftypmp42' + b'0' * 1000
    fake_file = (io.BytesIO(fake_video_content), 'sample.mp4')

    response = client.post(
        '/upload',
        data={'video': fake_file},
        content_type='multipart/form-data'
    )

    json_data = response.get_json()

    assert response.status_code == 201
    assert 'job_id' in json_data
    assert json_data['filename'].endswith('.mp4')
    # Verify our Day 5 chunked saving wrote every single byte correctly
    assert json_data['size_bytes'] == len(fake_video_content) 