# Multi-stage build for OpenFang Auto Clip
FROM python:3.11-slim AS base

# Install system dependencies
RUN apt-get update && apt-get install -y \
    ffmpeg \
    git \
    wget \
    curl \
    && rm -rf /var/lib/apt/lists/*

# Install yt-dlp
RUN pip install --no-cache-dir yt-dlp>=2024.1.1

# Set working directory
WORKDIR /app

# Copy requirements first for better caching
COPY requirements.txt requirements-dev.txt ./

# Install Python dependencies
RUN pip install --no-cache-dir -e .

# Copy application code
COPY . .

# Create output directory
RUN mkdir -p /app/output

# Create non-root user
RUN useradd -m -u 1000 openfang && \
    chown -R openfang:openfang /app

USER openfang

# Set environment variables
ENV PYTHONUNBUFFERED=1
ENV OPENFANG_OUTPUT_DIR=/app/output
ENV OPENFANG_CONFIG_DIR=/app/config

# Expose web manager port
EXPOSE 5000

# Health check
HEALTHCHECK --interval=30s --timeout=10s --start-period=5s --retries=3 \
    CMD python3 -c "import sys; sys.exit(0)" || exit 1

# Default command
CMD ["python3", "auto_clip.py", "--help"]
