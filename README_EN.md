# OpenFang Auto Clip

Local-first short-form CLI: long video in, 9:16 caption-burned clips out. MIT.

Your media stays on the machine. Chinese and English both work.

```bash
pip install -e .
openfang clip "https://www.youtube.com/watch?v=VIDEO_ID" --transcript talk.srt
openfang clip lecture.mp4 --transcript lecture.srt --duration 45
```

Output: `~/.openfang/clips/clips/<timestamp>/clip_01_....mp4`

No transcript? `--transcribe` runs local Whisper (slow, offline).

## Honest scope

| Capability | Status |
|---|---|
| `openfang clip` → 9:16 MP4 with burned captions | Works (v0.6) |
| Hook windows from SRT/VTT, not even slices | Works |
| Level 1 visual remix | Works via `python auto_clip.py URL --transform 1` |
| Level 2 script package | JSON/Markdown only, **not a rendered video** |
| Level 3 recreation | Not built |
| Speaker tracking / karaoke captions | Not yet |
| Hosted SaaS / mobile app | Out of scope |

Needs Python 3.9+, ffmpeg with subtitle support, and yt-dlp for URLs.

Roadmap: [ROADMAP.md](ROADMAP.md). 中文：[README.md](README.md).
