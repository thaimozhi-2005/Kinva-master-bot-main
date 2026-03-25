# Use official Python runtime as base image
FROM python:3.11-slim

# Set working directory
WORKDIR /app

# Set environment variables
ENV PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1 \
    DEBIAN_FRONTEND=noninteractive \
    OPENCV_IO_ENABLE_OPENEXR=1

# Install minimal system dependencies
RUN apt-get update && apt-get install -y --no-install-recommends \
    ffmpeg \
    libsm6 \
    libxext6 \
    libxrender1 \
    libgomp1 \
    libglib2.0-0 \
    libgl1 \
    curl \
    imagemagick \
    fonts-liberation \
    fonts-dejavu-core \
    && rm -rf /var/lib/apt/lists/* \
    && apt-get clean

# Fix ImageMagick policy for MoviePy
RUN if [ -f /etc/ImageMagick-6/policy.xml ]; then \
        sed -i 's/pixel cache limit="1GiB"/pixel cache limit="2GiB"/' /etc/ImageMagick-6/policy.xml; \
        sed -i 's/rights="none" pattern="PDF"/rights="read|write" pattern="PDF"/' /etc/ImageMagick-6/policy.xml; \
    elif [ -f /etc/ImageMagick-7/policy.xml ]; then \
        sed -i 's/pixel cache limit="1GiB"/pixel cache limit="2GiB"/' /etc/ImageMagick-7/policy.xml; \
        sed -i 's/rights="none" pattern="PDF"/rights="read|write" pattern="PDF"/' /etc/ImageMagick-7/policy.xml; \
    elif [ -f /etc/ImageMagick/policy.xml ]; then \
        sed -i 's/pixel cache limit="1GiB"/pixel cache limit="2GiB"/' /etc/ImageMagick/policy.xml; \
        sed -i 's/rights="none" pattern="PDF"/rights="read|write" pattern="PDF"/' /etc/ImageMagick/policy.xml; \
    fi

# Copy requirements
COPY requirements.txt .

# Install Python dependencies (without OpenCV first)
RUN pip install --no-cache-dir --upgrade pip && \
    pip install --no-cache-dir numpy pillow python-telegram-bot Flask Flask-SocketIO pymongo redis python-dotenv requests moviepy

# Create directories
RUN mkdir -p temp uploads outputs logs static/css static/js templates fonts

# Copy application
COPY . .

# Create user
RUN useradd -m -u 1000 -s /bin/bash kinva && \
    chown -R kinva:kinva /app

USER kinva

EXPOSE 5000

CMD ["python", "run.py", "--mode", "both"]
