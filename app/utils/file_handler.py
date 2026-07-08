"""Handles safely saving uploaded files to disk in chunks."""

CHUNK_SIZE = 1024 * 1024  # 1 MB per chunk


def save_file_in_chunks(file_storage, destination_path):
    """
    Save an uploaded file to disk by reading it in fixed-size chunks,
    instead of loading it into memory all at once.

    file_storage: the Werkzeug FileStorage object (from request.files['video'])
    destination_path: full path where the file should be saved
    """
    bytes_written = 0

    # Open the file in 'wb' (write-binary) mode. 
    # Binary mode is mandatory for video files!
    with open(destination_path, 'wb') as output_file:
        while True:
            # Read exactly 1MB from the incoming stream
            chunk = file_storage.stream.read(CHUNK_SIZE)
            
            # If the chunk is empty, we've reached the end of the file
            if not chunk:
                break
                
            # Write this 1MB piece to the hard drive immediately
            output_file.write(chunk)
            bytes_written += len(chunk)

    return bytes_written