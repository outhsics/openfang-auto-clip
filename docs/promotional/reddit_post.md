# Reddit Post Template (r/Python, r/VideoEditing, r/opensource)

## Title
OpenFang Auto Clip - A fully customizable, local-first video automation tool

## Body

Hey everyone! 👋

I've been working on an open-source video automation tool that I think might be useful for this community:

**OpenFang Auto Clip** - A local-first Python + FFmpeg pipeline for turning long videos into short clips.

## Why I Built This

I was frustrated with:
- **SaaS video tools** requiring cloud uploads (privacy concerns)
- **Expensive subscriptions** ($20-100/month + API fees)
- **Black-box features** limiting customization

So I built a local-first alternative.

## Key Features

✅ **Privacy-First**: Everything runs locally - your content never leaves your machine
✅ **Free & Open-Source**: MIT licensed, no API costs
✅ **Fully Customizable**: Built with Python + FFmpeg - extend it however you want
✅ **Production-Ready**: Includes benchmark, evaluation suite, and web UI
✅ **Bilingual Docs**: English and Chinese documentation

## Quick Start (30 seconds)

```bash
git clone https://github.com/outhsics/openfang-auto-clip.git
cd openfang-auto-clip
pip install -e .

# Quick demo (5 seconds, no download needed!)
python3 auto_clip.py --quick-demo

# Process your first video
./auto_clip.sh "https://www.youtube.com/watch?v=VIDEO_ID" --transform 1
```

## What It Does

1. **Download videos** from YouTube and 1000+ other sites (yt-dlp)
2. **Apply transformations**:
   - Level 1: Visual remix (FFmpeg filters like flip, zoom, color grade)
   - Level 2: Script package generation (transcript-to-script)
3. **Generate clips** for TikTok, Shorts, Reels
4. **Export** to local directory

## Use Cases

- **Content creators**: Repurpose long videos into shorts
- **Podcasters**: Extract highlights from episodes
- **Developers**: Build custom video workflows
- **Marketing teams**: Batch process for multiple platforms

## Tech Stack

- Python 3.9+
- FFmpeg (video processing)
- yt-dlp (video downloading)
- Local-first architecture

## What's Unique

Compared to other tools:
- **No cloud dependencies** - runs 100% locally
- **No API costs** - uses FFmpeg instead of paid APIs
- **Fully extensible** - add custom FFmpeg filters or Python code
- **Reproducible benchmarks** - synthetic demos without external media

## Current Status

- ✅ Level 1: Visual remix (available)
- ✅ Level 2: Script packages (available)
- 🚧 Level 3: Complete recreation (roadmap)

## Looking For Feedback

Would love feedback on:
- Feature requests
- Performance optimizations
- Platform integrations
- Documentation improvements

**GitHub**: https://github.com/outhsics/openfang-auto-clip
**Docs**: https://github.com/outhsics/openfang-auto-clip/blob/main/docs/

Would love to hear your thoughts! 🙏
