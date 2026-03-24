#!/bin/bash
# Docker entrypoint script for OpenFang Auto Clip

set -e

echo "🎬 OpenFang Auto Clip - Docker Container"
echo "=========================================="

# Create necessary directories
mkdir -p /app/output/clips
mkdir -p /app/output/downloads
mkdir -p /app/output/script_packages
mkdir -p /app/config

# Check if OpenFang API is available
if [ -n "$OPENFANG_API_URL" ]; then
    echo "📡 OpenFang API configured: $OPENFANG_API_URL"
fi

# Check environment
echo ""
echo "🩺 Running environment check..."
python3 auto_clip.py --doctor

# If command is "web", start web manager
if [ "$1" = "web" ]; then
    echo ""
    echo "🌐 Starting Web Manager..."
    exec python3 web_manager.py
fi

# If command is "worker", start as worker
if [ "$1" = "worker" ]; then
    echo ""
    echo "👷 Starting in worker mode..."
    exec tail -f /dev/null
fi

# Default: show help
echo ""
echo "📖 Available commands:"
echo "  docker-compose run openfang-auto-clip --help"
echo "  docker-compose run openfang-auto-clip --quick-demo"
echo "  docker-compose run openfang-auto-clip --doctor"
echo "  docker-compose up openfang-auto-clip web  # Start web manager"
echo ""
exec "$@"
