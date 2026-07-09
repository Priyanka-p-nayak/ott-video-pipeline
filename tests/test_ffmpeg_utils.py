"""Unit tests for FFmpeg conversion logic, using mocking to avoid
needing real video files or actually running FFmpeg during tests.
"""

from unittest.mock import patch, MagicMock
from app.workers.ffmpeg_utils import convert_to_resolution


@patch('app.workers.ffmpeg_utils.os.path.getsize')
@patch('app.workers.ffmpeg_utils.os.path.exists')
@patch('app.workers.ffmpeg_utils.subprocess.run')
def test_convert_success(mock_run, mock_exists, mock_getsize):
    """If FFmpeg returns success (returncode 0) and output file is valid, return True."""
    mock_exists.return_value = True       # pretend input AND output files exist
    mock_getsize.return_value = 5000       # pretend files have real content (non-zero size)

    mock_result = MagicMock()
    mock_result.returncode = 0
    mock_run.return_value = mock_result

    success = convert_to_resolution('fake_input.mp4', 'fake_output.mp4', 720)

    assert success is True
    mock_run.assert_called_once()  # confirm FFmpeg was actually invoked


@patch('app.workers.ffmpeg_utils.os.path.getsize')
@patch('app.workers.ffmpeg_utils.os.path.exists')
@patch('app.workers.ffmpeg_utils.subprocess.run')
def test_convert_ffmpeg_failure(mock_run, mock_exists, mock_getsize):
    """If FFmpeg returns a non-zero exit code, return False."""
    mock_exists.return_value = True
    mock_getsize.return_value = 5000

    mock_result = MagicMock()
    mock_result.returncode = 1
    mock_result.stderr = 'Invalid data found when processing input'
    mock_run.return_value = mock_result

    success = convert_to_resolution('fake_input.mp4', 'fake_output.mp4', 720)

    assert success is False


@patch('app.workers.ffmpeg_utils.subprocess.run')
@patch('app.workers.ffmpeg_utils.os.path.exists')
def test_convert_missing_input_file(mock_exists, mock_run):
    """If the input file doesn't exist, return False without calling FFmpeg at all."""
    mock_exists.return_value = False

    success = convert_to_resolution('does_not_exist.mp4', 'fake_output.mp4', 720)

    assert success is False
    mock_run.assert_not_called()  # confirm we never even tried to run FFmpeg


@patch('app.workers.ffmpeg_utils.os.path.getsize')
@patch('app.workers.ffmpeg_utils.os.path.exists')
@patch('app.workers.ffmpeg_utils.subprocess.run')
def test_convert_timeout(mock_run, mock_exists, mock_getsize):
    """If FFmpeg hangs and times out, return False instead of crashing."""
    import subprocess
    
    mock_exists.return_value = True
    mock_getsize.return_value = 5000  # Pretend the file has size so it passes the empty check
    
    # Instead of returning a value, side_effect forces the mock to raise an exception
    mock_run.side_effect = subprocess.TimeoutExpired(cmd='ffmpeg', timeout=300)

    success = convert_to_resolution('fake_input.mp4', 'fake_output.mp4', 720)

    assert success is False