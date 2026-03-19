# Installation Guide

## Requirements

- Python 3.9+
- `ffmpeg`
- `yt-dlp`
- OpenFang 0.1.9+ if you want to use the OpenFang-backed workflow

## Quick Install

```bash
git clone https://github.com/outhsics/openfang-auto-clip.git
cd openfang-auto-clip
./scripts/install.sh
```

The installer will:

- check for Python, FFmpeg, and OpenFang
- create a virtual environment in `~/.openfang/venv`
- install Python dependencies
- create `~/.openfang/clips`, `~/.openfang/downloads`, and `~/.openfang/logs`
- copy the default config to `~/.openfang/auto_clip_config.json`

## Manual Install

```bash
python3 -m venv ~/.openfang/venv
source ~/.openfang/venv/bin/activate
pip install --upgrade pip
pip install -r requirements.txt
```

If `ffmpeg` is missing:

```bash
# macOS
brew install ffmpeg

# Ubuntu / Debian
sudo apt-get update
sudo apt-get install -y ffmpeg
```

## Verify

```bash
./auto_clip.sh --doctor
python3 scripts/run_local_evaluation.py
./auto_clip.sh "https://www.youtube.com/watch?v=VIDEO_ID" --dry-run
./auto_clip.sh --help
python3 -m unittest discover -s tests
```

## Paths

- Config: `~/.openfang/auto_clip_config.json`
- Downloads: `~/.openfang/clips/downloads/`
- Clip outputs: `~/.openfang/clips/<timestamp>/`
- Web task state: `~/.openfang/web_tasks.json`
