# Start from an official, lightweight Python base image
FROM python:3.11-slim

# Set the working directory inside the container
WORKDIR /app

# Install FFmpeg (required for our video transcoding) via the OS package manager
RUN apt-get update && \
    apt-get install -y ffmpeg && \
    rm -rf /var/lib/apt/lists/*

# Copy only requirements.txt first (caching optimization)
COPY requirements.txt .

# Install Python dependencies
RUN pip install --no-cache-dir -r requirements.txt

# Now copy the rest of our application code
COPY . .

# Create the folders our app needs at runtime
RUN mkdir -p uploads outputs thumbnails logs

# Tell Docker this container listens on port 5000
EXPOSE 5000

# The command that runs when the container starts
CMD ["python", "run.py"]