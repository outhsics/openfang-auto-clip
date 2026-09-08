"""v0.6 clip path: local file or URL in, 9:16 caption-burned MP4s out."""

from __future__ import annotations

import argparse
import json
import re
import shutil
import subprocess
import sys
from datetime import datetime
from pathlib import Path
from typing import Iterable, List, Optional

HOOK_EN = re.compile(
    r"\b(wait|secret|actually|never|why|how|tip|mistake|first|truth|don't|must|stop)\b",
    re.IGNORECASE,
)
HOOK_ZH = re.compile(r"但是|其实|千万|秘密|为什么|怎么|注意|第一|原来|关键|记住|别再|一定|真相")


def format_srt_time(seconds: float) -> str:
    milliseconds = max(0, int(round(seconds * 1000)))
    hours, remainder = divmod(milliseconds, 3_600_000)
    minutes, remainder = divmod(remainder, 60_000)
    whole_seconds, milliseconds = divmod(remainder, 1000)
    return f"{hours:02d}:{minutes:02d}:{whole_seconds:02d},{milliseconds:03d}"


def write_srt(segments: List[dict], path: Path, start_offset: float = 0.0) -> None:
    lines = []
    index = 1
    for segment in segments:
        text = (segment.get("text") or "").strip()
        if not text:
            continue
        start = max(0.0, float(segment["start"]) - start_offset)
        end = max(start + 0.2, float(segment["end"]) - start_offset)
        lines.append(str(index))
        lines.append(f"{format_srt_time(start)} --> {format_srt_time(end)}")
        lines.append(text)
        lines.append("")
        index += 1
    path.write_text("\n".join(lines), encoding="utf-8")


def format_ass_time(seconds: float) -> str:
    milliseconds = max(0, int(round(seconds * 1000)))
    hours, remainder = divmod(milliseconds, 3_600_000)
    minutes, remainder = divmod(remainder, 60_000)
    whole_seconds, milliseconds = divmod(remainder, 1000)
    centiseconds = milliseconds // 10
    return f"{hours}:{minutes:02d}:{whole_seconds:02d}.{centiseconds:02d}"


def write_ass(segments: List[dict], path: Path) -> None:
    events = []
    for segment in segments:
        cue = (segment.get("text") or "").strip()
        cue = cue.replace(chr(92), "/").replace("{", "(").replace("}", ")")
        if not cue:
            continue
        start = max(0.0, float(segment["start"]))
        end = max(start + 0.2, float(segment["end"]))
        events.append(
            f"Dialogue: 0,{format_ass_time(start)},{format_ass_time(end)},Default,,0,0,0,,{cue}"
        )
    header = chr(10).join([
        "[Script Info]",
        "ScriptType: v4.00+",
        "PlayResX: 1080",
        "PlayResY: 1920",
        "WrapStyle: 0",
        "ScaledBorderAndShadow: yes",
        "",
        "[V4+ Styles]",
        "Format: Name, Fontname, Fontsize, PrimaryColour, SecondaryColour, OutlineColour, BackColour, Bold, Italic, Underline, StrikeOut, ScaleX, ScaleY, Spacing, Angle, BorderStyle, Outline, Shadow, Alignment, MarginL, MarginR, MarginV, Encoding",
        "Style: Default,Arial,48,&H00FFFFFF,&H000000FF,&H80000000,&H00000000,0,0,0,0,100,100,0,0,1,3,0,2,48,48,96,1",
        "",
        "[Events]",
        "Format: Layer, Start, End, Style, Name, MarginL, MarginR, MarginV, Effect, Text",
        "",
    ])
    path.write_text(header + chr(10).join(events) + chr(10), encoding="utf-8")


def score_segment(segment: dict, language: str) -> float:
    text = segment.get("text") or ""
    start = segment.get("start") or 0.0
    score = 1.0
    if language == "zh":
        score += 2.0 * len(HOOK_ZH.findall(text))
        score += min(len(text), 40) / 40.0
    else:
        score += 2.0 * len(HOOK_EN.findall(text))
        score += min(len(text.split()), 12) / 12.0
    if start < 8:
        score *= 0.35
    return score


def pick_windows(
    segments: List[dict],
    media_duration: float,
    clip_duration: float = 45.0,
    max_clips: int = 5,
) -> List[dict]:
    """Pick non-overlapping highlight windows from timed transcript segments."""
    usable = [
        segment
        for segment in segments
        if segment.get("start") is not None and segment.get("end") is not None and (segment.get("text") or "").strip()
    ]
    if not usable:
        windows = []
        start = 0.0
        index = 1
        while start < media_duration and len(windows) < max_clips:
            end = min(media_duration, start + clip_duration)
            if end - start < max(3.0, clip_duration * 0.5):
                break
            windows.append(
                {
                    "start": start,
                    "end": end,
                    "score": 1.0,
                    "reason": f"even-window-{index}",
                }
            )
            start = end
            index += 1
        return windows

    from auto_clip import detect_transcript_language

    language = detect_transcript_language(" ".join(segment["text"] for segment in usable))
    ranked = sorted(usable, key=lambda segment: score_segment(segment, language), reverse=True)

    windows: List[dict] = []
    for segment in ranked:
        if len(windows) >= max_clips:
            break
        center = (float(segment["start"]) + float(segment["end"])) / 2.0
        start = max(0.0, center - clip_duration * 0.35)
        end = min(media_duration, start + clip_duration)
        start = max(0.0, end - clip_duration)
        if end - start < max(3.0, clip_duration * 0.5):
            continue
        overlaps = any(
            not (end <= window["start"] + 1 or start >= window["end"] - 1)
            for window in windows
        )
        if overlaps:
            continue
        windows.append(
            {
                "start": round(start, 3),
                "end": round(end, 3),
                "score": round(score_segment(segment, language), 3),
                "reason": (segment["text"][:80]).strip(),
            }
        )
    windows.sort(key=lambda window: window["start"])
    return windows


def segments_in_window(segments: List[dict], start: float, end: float) -> List[dict]:
    chosen = []
    for segment in segments:
        if segment.get("start") is None or segment.get("end") is None:
            continue
        if segment["end"] <= start or segment["start"] >= end:
            continue
        chosen.append(segment)
    return chosen


def probe_duration(media_path: Path) -> float:
    result = subprocess.run(
        [
            "ffprobe",
            "-v",
            "error",
            "-show_entries",
            "format=duration",
            "-of",
            "default=noprint_wrappers=1:nokey=1",
            str(media_path),
        ],
        capture_output=True,
        text=True,
        check=False,
    )
    if result.returncode != 0:
        raise RuntimeError(result.stderr.strip() or "ffprobe failed")
    return float(result.stdout.strip())


def _caption_font(size: int = 52):
    from PIL import ImageFont

    candidates = [
        Path("/System/Library/Fonts/Hiragino Sans GB.ttc"),
        Path("/System/Library/Fonts/STHeiti Medium.ttc"),
        Path("/System/Library/Fonts/PingFang.ttc"),
        Path("/usr/share/fonts/truetype/noto/NotoSansCJK-Regular.ttc"),
        Path("/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf"),
        Path("C:/Windows/Fonts/msyh.ttc"),
        Path("C:/Windows/Fonts/arial.ttf"),
    ]
    for candidate in candidates:
        if candidate.exists():
            try:
                return ImageFont.truetype(str(candidate), size)
            except OSError:
                continue
    return ImageFont.load_default()


def wrap_caption(text: str, max_chars: int = 14) -> str:
    text = " ".join(text.split())
    if len(text) <= max_chars:
        return text
    lines = []
    current = ""
    for char in text:
        current += char
        if len(current) >= max_chars and char in " ，。！？,.!? ":
            lines.append(current.strip())
            current = ""
        elif len(current) >= max_chars + 4:
            lines.append(current.strip())
            current = ""
    if current.strip():
        lines.append(current.strip())
    return "\n".join(lines[:3])


def render_caption_png(text: str, path: Path, size=(1080, 1920)) -> None:
    from PIL import Image, ImageDraw

    image = Image.new("RGBA", size, (0, 0, 0, 0))
    draw = ImageDraw.Draw(image)
    font = _caption_font(52)
    wrapped = wrap_caption(text)
    bbox = draw.multiline_textbbox((0, 0), wrapped, font=font, align="center", spacing=8)
    text_w = bbox[2] - bbox[0]
    text_h = bbox[3] - bbox[1]
    x = (size[0] - text_w) / 2
    y = size[1] - text_h - 180
    pad = 22
    draw.rounded_rectangle(
        [x - pad, y - pad, x + text_w + pad, y + text_h + pad],
        radius=18,
        fill=(0, 0, 0, 150),
    )
    draw.multiline_text((x, y), wrapped, font=font, fill=(255, 255, 255, 255), align="center", spacing=8)
    image.save(path)


def ffmpeg_has_filter(name: str) -> bool:
    result = subprocess.run(["ffmpeg", "-hide_banner", "-filters"], capture_output=True, text=True)
    return f" {name} " in (result.stdout or "")


def burn_clip(
    source: Path,
    output: Path,
    start: float,
    duration: float,
    srt_path: Optional[Path],
) -> None:
    workdir = output.parent
    workdir.mkdir(parents=True, exist_ok=True)
    scale = "scale=1080:1920:force_original_aspect_ratio=decrease,pad=1080:1920:(ow-iw)/2:(oh-ih)/2,setsar=1"
    inputs = ["-y", "-ss", f"{start:.3f}", "-t", f"{duration:.3f}", "-i", str(source.resolve())]
    vf = scale
    filter_complex = None

    cues = []
    if srt_path and srt_path.exists() and srt_path.stat().st_size > 0:
        from auto_clip import build_transcript_payload

        cues = [
            cue
            for cue in (build_transcript_payload(srt_path).get("segments") or [])
            if (cue.get("text") or "").strip()
        ][:12]

    if cues and ffmpeg_has_filter("subtitles"):
        ass_path = workdir / (srt_path.stem + ".ass")
        write_ass(cues, ass_path)
        vf = f"{scale},subtitles={ass_path.name}"
    elif cues:
        overlays = []
        for index, cue in enumerate(cues, start=1):
            png = workdir / f"{srt_path.stem}_cap{index:02d}.png"
            render_caption_png(cue["text"], png)
            inputs.extend(["-i", str(png)])
            cue_start = max(0.0, float(cue["start"]))
            cue_end = max(cue_start + 0.2, float(cue["end"]))
            overlays.append((index, cue_start, cue_end))
        parts = [f"[0:v]{scale}[v0]"]
        last = "v0"
        for index, cue_start, cue_end in overlays:
            nxt = f"v{index}"
            parts.append(
                f"[{last}][{index}:v]overlay=0:0:enable='between(t,{cue_start:.3f},{cue_end:.3f})'[{nxt}]"
            )
            last = nxt
        filter_complex = ";".join(parts)
        map_video = f"[{last}]"

    command = ["ffmpeg", *inputs]
    if filter_complex:
        command.extend(["-filter_complex", filter_complex, "-map", map_video, "-map", "0:a?"])
    else:
        command.extend(["-vf", vf])
    command.extend(
        [
            "-c:v",
            "libx264",
            "-preset",
            "fast",
            "-crf",
            "23",
            "-c:a",
            "aac",
            "-b:a",
            "128k",
            "-shortest",
            "-movflags",
            "+faststart",
            output.name,
        ]
    )
    result = subprocess.run(command, capture_output=True, text=True, cwd=str(workdir))
    if result.returncode != 0:
        raise RuntimeError(result.stderr[-800:] or "ffmpeg failed")


def transcribe_if_possible(media_path: Path, model_name: str = "base") -> List[dict]:
    try:
        import whisper
    except ImportError as exc:
        raise RuntimeError("openai-whisper is not installed") from exc
    model = whisper.load_model(model_name)
    result = model.transcribe(str(media_path), word_timestamps=False)
    segments = []
    for item in result.get("segments") or []:
        text = (item.get("text") or "").strip()
        if not text:
            continue
        segments.append({"start": float(item["start"]), "end": float(item["end"]), "text": text})
    return segments


def resolve_source(source: str, download_dir: Path) -> dict:
    path = Path(source).expanduser()
    if path.exists():
        duration = probe_duration(path)
        return {"path": str(path.resolve()), "title": path.stem, "duration": duration, "id": path.stem}

    from auto_clip import download_video

    info = download_video(source, download_dir)
    if not info.get("duration"):
        info["duration"] = probe_duration(Path(info["path"]))
    return info


def run_clip_job(
    source: str,
    output_dir: Path,
    transcript_path: Optional[Path] = None,
    clip_duration: float = 45.0,
    max_clips: int = 5,
    transcribe: bool = False,
    whisper_model: str = "base",
) -> dict:
    output_dir.mkdir(parents=True, exist_ok=True)
    info = resolve_source(source, output_dir / "_source")
    media_path = Path(info["path"])
    duration = float(info.get("duration") or probe_duration(media_path))

    segments: List[dict] = []
    if transcript_path:
        from auto_clip import build_transcript_payload

        payload = build_transcript_payload(Path(transcript_path))
        segments = payload.get("segments") or []
    elif transcribe:
        segments = transcribe_if_possible(media_path, whisper_model)

    windows = pick_windows(segments, duration, clip_duration=clip_duration, max_clips=max_clips)
    clips = []
    for index, window in enumerate(windows, start=1):
        window_segments = segments_in_window(segments, window["start"], window["end"])
        srt_path = None
        if window_segments:
            srt_path = output_dir / f"clip_{index:02d}.srt"
            shifted = [
                {
                    "start": max(0.0, float(segment["start"]) - window["start"]),
                    "end": max(0.2, float(segment["end"]) - window["start"]),
                    "text": segment["text"],
                }
                for segment in window_segments
            ]
            write_srt(shifted, srt_path, start_offset=0.0)
        clip_path = output_dir / f"clip_{index:02d}_{int(window['start']):04d}s-{int(window['end']):04d}s.mp4"
        burn_clip(
            media_path,
            clip_path,
            window["start"],
            window["end"] - window["start"],
            srt_path,
        )
        clips.append(
            {
                "path": str(clip_path),
                "start": window["start"],
                "end": window["end"],
                "score": window.get("score"),
                "reason": window.get("reason"),
                "captions": str(srt_path) if srt_path else None,
            }
        )

    report = {
        "source": info,
        "clips": clips,
        "created_at": datetime.now().isoformat(),
        "output_dir": str(output_dir),
        "mode": "v0.6-clip",
    }
    (output_dir / "report.json").write_text(json.dumps(report, indent=2, ensure_ascii=False), encoding="utf-8")
    return report


def build_clip_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        prog="openfang clip",
        description="Turn a local file or URL into 9:16 caption-burned clips.",
    )
    parser.add_argument("source", help="Local video/audio path or a yt-dlp URL")
    parser.add_argument("--transcript", help="SRT/VTT/JSON transcript used to pick hooks and burn captions")
    parser.add_argument("--duration", type=float, default=45, help="Target clip length in seconds")
    parser.add_argument("--max-clips", type=int, default=5)
    parser.add_argument("--out", help="Output directory")
    parser.add_argument("--transcribe", action="store_true", help="Run local Whisper if no transcript is given")
    parser.add_argument("--whisper-model", default="base")
    return parser


def clip_main(argv: Optional[Iterable[str]] = None) -> int:
    parser = build_clip_parser()
    args = parser.parse_args(list(argv) if argv is not None else None)
    from auto_clip import OUTPUT_DIR

    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    output_dir = Path(args.out) if args.out else OUTPUT_DIR / "clips" / timestamp
    transcript = Path(args.transcript).expanduser() if args.transcript else None
    print("OpenFang clip  v0.6")
    print(f"source: {args.source}")
    report = run_clip_job(
        args.source,
        output_dir,
        transcript_path=transcript,
        clip_duration=args.duration,
        max_clips=args.max_clips,
        transcribe=args.transcribe,
        whisper_model=args.whisper_model,
    )
    print(f"output: {report['output_dir']}")
    print(f"clips:  {len(report['clips'])}")
    for clip in report["clips"]:
        print(f"  - {Path(clip['path']).name}  {clip['start']:.0f}s-{clip['end']:.0f}s")
    return 0 if report["clips"] else 1


if __name__ == "__main__":
    sys.exit(clip_main())
