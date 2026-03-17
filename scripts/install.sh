#!/bin/bash
# OpenFang Auto Clip - Installation Script

set -euo pipefail

echo "╔═══════════════════════════════════════════════════════════════╗"
echo "║                                                               ║"
echo "║   🎬 OpenFang Auto Clip - Installation                      ║"
echo "║   Copyright-Safe Video Editing with AI                       ║"
echo "║                                                               ║"
echo "╚═══════════════════════════════════════════════════════════════╝"
echo ""

# Detect OS
OS="$(uname -s)"
ARCH="$(uname -m)"
OPENFANG_HOME="${HOME}/.openfang"
VENV_DIR="${OPENFANG_HOME}/venv"

echo "🖥️  Detected OS: $OS $ARCH"
echo ""

# Check Python
echo "🐍 Checking Python..."
if ! command -v python3 &> /dev/null; then
    echo "❌ Python 3 not found. Please install Python 3.9+"
    exit 1
fi

PYTHON_VERSION=$(python3 --version | awk '{print $2}')
echo "   ✅ Python $PYTHON_VERSION"

# Check FFmpeg
echo "🎬 Checking FFmpeg..."
if ! command -v ffmpeg &> /dev/null; then
    echo "   ⚠️  FFmpeg not found. Installing..."
    if [[ "$OS" == "Darwin" ]]; then
        brew install ffmpeg
    else
        sudo apt-get install -y ffmpeg
    fi
fi
echo "   ✅ $(ffmpeg -version | head -1)"

# Check OpenFang
echo "🤖 Checking OpenFang..."
if ! command -v openfang &> /dev/null; then
    echo "   ⚠️  OpenFang not found. Installing..."
    curl -fsSL https://openfang.sh/install | sh
fi
echo "   ✅ $(openfang --version | head -1)"

# Create virtual environment
echo "📦 Creating Python virtual environment..."
python3 -m venv "$VENV_DIR"
source "$VENV_DIR/bin/activate"

# Install Python dependencies
echo "📚 Installing Python dependencies..."
pip install --upgrade pip
pip install -e . --no-build-isolation

# Create directories
echo "📁 Creating directories..."
mkdir -p "${OPENFANG_HOME}/"{downloads,clips,logs,styles}
mkdir -p "${OPENFANG_HOME}/clips/downloads"

# Initialize OpenFang
echo "🔧 Initializing OpenFang..."
if [ ! -f "${OPENFANG_HOME}/config.toml" ]; then
    openfang init --quick
fi

# Copy default config
if [ ! -f "${OPENFANG_HOME}/auto_clip_config.json" ]; then
    cp config/example_config.json "${OPENFANG_HOME}/auto_clip_config.json"
fi

echo ""
echo "╔═══════════════════════════════════════════════════════════════╗"
echo "║                                                               ║"
echo "║   ✅ Installation Complete!                                  ║"
echo "║                                                               ║"
echo "╚═══════════════════════════════════════════════════════════════╝"
echo ""
echo "🚀 Quick Start:"
echo ""
echo "   1. Start OpenFang:"
echo "      openfang start &"
echo ""
echo "   2. Process a video:"
echo "      ./auto_clip.sh 'https://youtube.com/watch?v=VIDEO_ID'"
echo ""
echo "   3. View output:"
echo "      open ~/.openfang/clips/"
echo ""
echo "📚 Documentation:"
echo "   • README.md - Overview and quick start"
echo "   • docs/INSTALLATION.md - Detailed installation guide"
echo "   • docs/TRANSFORMATION.md - Copyright transformation guide"
echo ""
echo "💡 Need help?"
echo "   • GitHub Issues: https://github.com/outhsics/openfang-auto-clip/issues"
echo "   • Discussions: https://github.com/outhsics/openfang-auto-clip/discussions"
echo ""
