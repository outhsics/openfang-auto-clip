#!/bin/bash
# Start OpenFang Auto Clip Web Manager v2

PROJECT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
cd "$PROJECT_DIR"

echo "Starting OpenFang Auto Clip Web Manager v2..."

# Check if required dependencies are installed
if ! command -v python3 &> /dev/null; then
    echo "Error: python3 is not installed"
    exit 1
fi

# Check if flask is installed
if ! python3 -c "import flask" 2> /dev/null; then
    echo "Flask not found. Installing..."
    pip install flask flask-cors
fi

# Start the web server
python3 src/web_manager_v2.py "$@"
