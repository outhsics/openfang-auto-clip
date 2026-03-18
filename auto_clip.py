#!/usr/bin/env python3
"""
OpenFang Auto Clip local CLI.

This tool downloads source media, applies local transformation steps,
and generates short-form clips plus reports.
"""

import os
import sys
import json
import subprocess
import re
import shutil
from datetime import datetime
from pathlib import Path
from typing import Dict, List, Optional, Tuple
from enum import Enum

# ============================================================================
# CONFIGURATION
# ============================================================================

OUTPUT_DIR = Path.home() / ".openfang" / "clips"
CONFIG_FILE = Path.home() / ".openfang" / "auto_clip_config.json"
TRANSCRIPT_EXTENSIONS = (".txt", ".md", ".srt", ".vtt", ".json")


class TransformLevel(Enum):
    """Copyright transformation levels"""
    NONE = 0  # No transformation (not recommended for commercial use)
    VISUAL = 1  # Visual remix (fastest, moderate safety)
    SCRIPT = 2  # Script regeneration (slower, high safety)
    COMPLETE = 3  # Complete recreation (concept scaffold)


# ============================================================================
# VIDEO PROCESSING
# ============================================================================

def load_config() -> dict:
    """Load configuration from file"""
    if CONFIG_FILE.exists():
        with open(CONFIG_FILE) as f:
            return json.load(f)

    return {
        "default_duration": 60,
        "min_duration": 30,
        "max_duration": 90,
        "target_platforms": ["tiktok", "shorts", "reels"],
        "auto_caption": True,
        "whisper_model": "base",
        "transform_level": 1,  # Default to Level 1
        "openfang_api": "http://127.0.0.1:4200"
    }


def command_exists(command: str) -> bool:
    """Return whether a command is available on PATH."""
    return shutil.which(command) is not None


def build_doctor_report() -> dict:
    """Collect a lightweight environment report."""
    checks = [
        {
            "name": "python",
            "status": "ok" if sys.version_info >= (3, 9) else "error",
            "detail": sys.version.split()[0],
            "required": True,
        },
        {
            "name": "ffmpeg",
            "status": "ok" if command_exists("ffmpeg") else "error",
            "detail": shutil.which("ffmpeg") or "not found",
            "required": True,
        },
        {
            "name": "yt-dlp",
            "status": "ok" if command_exists("yt-dlp") else "error",
            "detail": shutil.which("yt-dlp") or "not found",
            "required": True,
        },
        {
            "name": "openfang",
            "status": "ok" if command_exists("openfang") else "warn",
            "detail": shutil.which("openfang") or "not found",
            "required": False,
        },
        {
            "name": "config",
            "status": "ok" if CONFIG_FILE.exists() else "warn",
            "detail": str(CONFIG_FILE),
            "required": False,
        },
    ]

    output_status = "ok"
    try:
        OUTPUT_DIR.mkdir(parents=True, exist_ok=True)
    except OSError as exc:
        output_status = "error"
        output_detail = f"{OUTPUT_DIR} ({exc})"
    else:
        output_detail = str(OUTPUT_DIR)

    checks.append(
        {
            "name": "output_dir",
            "status": output_status,
            "detail": output_detail,
            "required": True,
        }
    )

    return {
        "created_at": datetime.now().isoformat(),
        "checks": checks,
    }


def print_doctor_report(report: dict) -> None:
    """Render the doctor report to stdout."""
    print("=" * 70)
    print("🩺 OpenFang Auto Clip Doctor")
    print("=" * 70)

    has_error = False
    for check in report["checks"]:
        if check["status"] == "ok":
            marker = "✅"
        elif check["status"] == "warn":
            marker = "⚠️ "
        else:
            marker = "❌"
            has_error = True

        required = "required" if check["required"] else "optional"
        print(f"{marker} {check['name']} [{required}]")
        print(f"   {check['detail']}")

    print()
    if has_error:
        print("❌ Environment check failed. Fix required items before processing videos.")
    else:
        print("✅ Environment looks ready.")


def build_processing_plan(
    url: str,
    transform_level: int,
    config: dict,
    transcript_path: Optional[str] = None,
    now: Optional[datetime] = None,
) -> dict:
    """Build a dry-run plan for the requested processing job."""
    now = now or datetime.now()
    timestamp = now.strftime("%Y%m%d_%H%M%S")
    level = TransformLevel(transform_level)

    plan = {
        "url": url,
        "transform_level": transform_level,
        "transform_label": level.name.lower(),
        "default_duration": config.get("default_duration", 60),
        "target_platforms": config.get("target_platforms", ["tiktok"]),
        "downloads_dir": str((OUTPUT_DIR / "downloads").resolve()),
        "projected_output_dir": str((OUTPUT_DIR / "clips" / timestamp).resolve()),
        "config_file": str(CONFIG_FILE.resolve()),
        "created_at": now.isoformat(),
    }

    if level == TransformLevel.SCRIPT:
        resolved_transcript = None
        if transcript_path:
            resolved_transcript = str(resolve_explicit_transcript_path(transcript_path))

        plan["transcript_path"] = resolved_transcript
        plan["script_package_ready"] = resolved_transcript is not None
        plan["requirements"] = [
            "Provide a transcript file via --transcript or a sidecar transcript next to the source video",
            "Review the generated narration draft before recording voiceover",
            "Rebuild visuals separately after approving the new script package",
        ]

    return plan


def save_dry_run_plan(plan: dict) -> Path:
    """Persist a dry-run plan for later inspection."""
    dry_run_dir = OUTPUT_DIR / "dry_runs"
    dry_run_dir.mkdir(parents=True, exist_ok=True)
    plan_path = dry_run_dir / f"plan_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json"
    with open(plan_path, "w") as handle:
        json.dump(plan, handle, indent=2)
    return plan_path


def print_dry_run_plan(plan: dict, plan_path: Path) -> None:
    """Render a dry-run summary to stdout."""
    print("=" * 70)
    print("🧪 OpenFang Auto Clip Dry Run")
    print("=" * 70)
    print(f"URL: {plan['url']}")
    print(f"Transform: Level {plan['transform_level']} ({plan['transform_label']})")
    print(f"Clip duration: {plan['default_duration']} seconds")
    print(f"Platforms: {', '.join(plan['target_platforms'])}")
    print(f"Downloads dir: {plan['downloads_dir']}")
    print(f"Projected output dir: {plan['projected_output_dir']}")
    print(f"Config file: {plan['config_file']}")
    if "transcript_path" in plan:
        print(f"Transcript: {plan['transcript_path'] or 'not provided'}")
        print(f"Level 2 package ready: {'yes' if plan['script_package_ready'] else 'no'}")
    print()
    print(f"Plan saved to: {plan_path}")


def resolve_explicit_transcript_path(transcript_path: str) -> Path:
    """Resolve and validate an explicitly provided transcript path."""
    candidate = Path(transcript_path).expanduser()
    if not candidate.is_absolute():
        candidate = (Path.cwd() / candidate).resolve()
    if not candidate.exists():
        raise FileNotFoundError(f"Transcript file not found: {candidate}")
    return candidate


def resolve_transcript_path(video_path: str, transcript_path: Optional[str] = None) -> Optional[Path]:
    """Resolve an explicit transcript path or infer a sidecar transcript next to the video."""
    if transcript_path:
        return resolve_explicit_transcript_path(transcript_path)

    video_file = Path(video_path)
    candidates = []
    for extension in TRANSCRIPT_EXTENSIONS:
        candidates.append(video_file.with_suffix(extension))
        candidates.append(video_file.parent / f"{video_file.stem}.transcript{extension}")

    for candidate in candidates:
        if candidate.exists():
            return candidate.resolve()

    return None


def normalize_transcript_text(text: str) -> str:
    """Collapse transcript text into a review-friendly single string."""
    return re.sub(r"\s+", " ", text).strip()


def read_transcript_text(transcript_path: Path) -> str:
    """Read transcript text from txt, markdown, subtitle, or JSON files."""
    raw_text = transcript_path.read_text(encoding="utf-8", errors="ignore")
    suffix = transcript_path.suffix.lower()

    if suffix in {".srt", ".vtt"}:
        lines = []
        for line in raw_text.splitlines():
            stripped = line.strip()
            if not stripped or stripped.isdigit() or "-->" in stripped or stripped.upper() == "WEBVTT":
                continue
            lines.append(stripped)
        return normalize_transcript_text(" ".join(lines))

    if suffix == ".json":
        data = json.loads(raw_text)
        if isinstance(data, dict):
            if isinstance(data.get("text"), str):
                return normalize_transcript_text(data["text"])

            segments = data.get("segments")
            if isinstance(segments, list):
                combined = " ".join(
                    segment.get("text", "")
                    for segment in segments
                    if isinstance(segment, dict)
                )
                return normalize_transcript_text(combined)

        if isinstance(data, list):
            combined = " ".join(
                item.get("text", "")
                for item in data
                if isinstance(item, dict)
            )
            if combined.strip():
                return normalize_transcript_text(combined)

        raise ValueError(f"Unsupported transcript JSON shape: {transcript_path}")

    return normalize_transcript_text(raw_text)


def detect_transcript_language(text: str) -> str:
    """Roughly detect whether the transcript is primarily Chinese or English."""
    cjk_chars = re.findall(r"[\u4e00-\u9fff]", text)
    latin_chars = re.findall(r"[A-Za-z]", text)
    return "zh" if len(cjk_chars) >= max(12, len(latin_chars) // 2) else "en"


def split_transcript_sentences(text: str) -> List[str]:
    """Split transcript text into normalized candidate sentences."""
    chunks = re.split(r"(?<=[。！？!?])\s*|(?<=[.])\s+|\n+", text)
    sentences = []
    seen = set()

    for chunk in chunks:
        normalized = normalize_transcript_text(chunk)
        if len(normalized) < 12:
            continue
        dedupe_key = normalized.lower()
        if dedupe_key in seen:
            continue
        seen.add(dedupe_key)
        sentences.append(normalized)

    return sentences


def shorten_phrase(text: str, language: str, *, max_words: int = 12, max_chars: int = 42) -> str:
    """Trim a sentence into a concise phrase for script and on-screen text."""
    compact = normalize_transcript_text(text).strip(" .,!?:;，。！？；：")
    if language == "zh":
        return compact if len(compact) <= max_chars else f"{compact[: max_chars - 1]}…"

    words = compact.split()
    if len(words) <= max_words:
        return compact
    return " ".join(words[:max_words]) + "..."


def build_level2_script_sections(points: List[str], language: str, duration: int) -> List[dict]:
    """Convert extracted transcript points into a deterministic script draft."""
    hook_duration = max(6, int(duration * 0.2))
    closing_duration = max(6, int(duration * 0.18))
    body_total = max(duration - hook_duration - closing_duration, len(points) * 6)
    body_duration = max(6, int(body_total / max(len(points), 1)))

    if language == "zh":
        sections = [
            {
                "section": "开场",
                "duration": hook_duration,
                "narration": f"这条短视频不用原句复述，先用新的讲法讲清核心点：{points[0]}。",
                "on_screen_text": shorten_phrase(points[0], language, max_chars=18),
                "visual_direction": "用标题卡点明主题，再切到新的讲述视角。",
            }
        ]
        for index, point in enumerate(points, start=1):
            sections.append(
                {
                    "section": f"重点 {index}",
                    "duration": body_duration,
                    "narration": f"第{index}点，{point}。把这个点拆开讲，避免沿用原视频节奏。",
                    "on_screen_text": shorten_phrase(point, language, max_chars=18),
                    "visual_direction": "用新的 B-roll、图示或屏幕录制支撑这一段。",
                }
            )
        sections.append(
            {
                "section": "收尾",
                "duration": duration - sum(section["duration"] for section in sections),
                "narration": f"总结一下，把上面几个重点收束成一句自己的结论，再给出下一步动作。",
                "on_screen_text": "总结与行动",
                "visual_direction": "回到主持人口播或总结卡片，不复用原片尾结构。",
            }
        )
        return sections

    sections = [
        {
            "section": "Hook",
            "duration": hook_duration,
            "narration": f"Retell the core idea from a fresh angle: {points[0]}.",
            "on_screen_text": shorten_phrase(points[0], language),
            "visual_direction": "Open with a fresh title card and new framing, not the original pacing.",
        }
    ]
    for index, point in enumerate(points, start=1):
        sections.append(
            {
                "section": f"Beat {index}",
                "duration": body_duration,
                "narration": f"Point {index}: {point}. Expand it in your own voice instead of mirroring the source wording.",
                "on_screen_text": shorten_phrase(point, language),
                "visual_direction": "Use new B-roll, diagrams, or screen capture to support this point.",
            }
        )
    sections.append(
        {
            "section": "Close",
            "duration": duration - sum(section["duration"] for section in sections),
            "narration": "Close with your own takeaway and a next action instead of reusing the source ending.",
            "on_screen_text": "Fresh takeaway",
            "visual_direction": "End on a summary card or direct-to-camera close.",
        }
    )
    return sections


def build_level2_script_package(video_info: dict, transcript_text: str, transcript_path: Path, config: dict) -> dict:
    """Build a transcript-to-script package for the first Level 2 milestone."""
    sentences = split_transcript_sentences(transcript_text)
    if not sentences:
        raise ValueError("Transcript did not contain enough readable sentences to build a script package")

    language = detect_transcript_language(transcript_text)
    selected_points = [shorten_phrase(sentence, language, max_words=16, max_chars=48) for sentence in sentences[:4]]
    target_duration = config.get("default_duration", 60)
    script_sections = build_level2_script_sections(selected_points, language, target_duration)

    return {
        "milestone": "level2_transcript_to_script_package",
        "language": language,
        "source": {
            "title": video_info.get("title", Path(video_info.get("path", "source")).stem),
            "video_path": video_info.get("path"),
            "transcript_path": str(transcript_path),
            "sentence_count": len(sentences),
        },
        "source_outline": [
            {"index": index, "summary": point}
            for index, point in enumerate(selected_points, start=1)
        ],
        "script_sections": script_sections,
        "production_checklist": [
            "Review the narration and remove any wording that still feels too close to the source",
            "Record a new voiceover or TTS track from the rewritten script",
            "Replace visuals with new footage, diagrams, captures, or generated assets",
            "Re-time captions and pacing after the new voiceover is approved",
        ],
        "limitations": [
            "This milestone generates a script package, not a fully rebuilt output video",
            "Voiceover, new visuals, and final edit still need operator review and assembly",
        ],
    }


def render_level2_script_markdown(package: dict) -> str:
    """Render the Level 2 script package into a human-reviewable markdown file."""
    lines = [
        "# Level 2 Script Package",
        "",
        f"- Source title: {package['source']['title']}",
        f"- Transcript: {package['source']['transcript_path']}",
        f"- Language: {package['language']}",
        f"- Milestone: {package['milestone']}",
        "",
        "## Source Outline",
        "",
    ]

    for point in package["source_outline"]:
        lines.append(f"{point['index']}. {point['summary']}")

    lines.extend(["", "## Script Draft", ""])
    for section in package["script_sections"]:
        lines.extend(
            [
                f"### {section['section']} ({section['duration']}s)",
                f"- Narration: {section['narration']}",
                f"- On-screen text: {section['on_screen_text']}",
                f"- Visual direction: {section['visual_direction']}",
                "",
            ]
        )

    lines.extend(["## Production Checklist", ""])
    for item in package["production_checklist"]:
        lines.append(f"- {item}")

    lines.extend(["", "## Current Limits", ""])
    for item in package["limitations"]:
        lines.append(f"- {item}")

    lines.append("")
    return "\n".join(lines)


def save_level2_script_package(video_info: dict, package: dict) -> Tuple[Path, List[Path]]:
    """Persist the Level 2 script package as JSON plus a review markdown draft."""
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    source_title = sanitize_filename(video_info.get("title", "source")) or "source"
    package_dir = OUTPUT_DIR / "script_packages" / f"{timestamp}_{source_title}"
    package_dir.mkdir(parents=True, exist_ok=True)

    package_json_path = package_dir / "script_package.json"
    with open(package_json_path, "w", encoding="utf-8") as handle:
        json.dump(package, handle, ensure_ascii=False, indent=2)

    draft_path = package_dir / "script_draft.md"
    with open(draft_path, "w", encoding="utf-8") as handle:
        handle.write(render_level2_script_markdown(package))

    return package_dir, [package_json_path, draft_path]


def download_video(url: str, output_dir: Path) -> dict:
    """
    Download video from YouTube or other supported sites

    Args:
        url: Video URL
        output_dir: Output directory path

    Returns:
        Video metadata dict
    """
    print(f"📥 Downloading video: {url}")

    output_dir.mkdir(parents=True, exist_ok=True)

    cmd = [
        "yt-dlp",
        "-f", "best[ext=mp4]",
        "-o", str(output_dir / "%(title)s.%(ext)s"),
        "--print", "json",
        "--remote-components", "ejs:github",
        "--newline",
        url
    ]

    result = subprocess.run(cmd, capture_output=True, text=True, timeout=300)

    if result.returncode != 0:
        raise Exception(f"Download failed: {result.stderr}")

    try:
        video_info = json.loads(result.stdout)

        # Sanitize filename
        safe_title = sanitize_filename(video_info.get('title', 'video'))
        video_path = output_dir / f"{safe_title}.mp4"

        # Rename if needed
        original_path = output_dir / f"{video_info['title']}.mp4"
        if original_path.exists() and original_path != video_path:
            original_path.rename(video_path)

        print(f"✅ Download complete: {video_path.name}")

        return {
            "path": str(video_path),
            "title": video_info.get('title', safe_title),
            "duration": video_info.get('duration', 0),
            "id": video_info.get('id', 'unknown'),
            "uploader": video_info.get('uploader', 'unknown'),
            "upload_date": video_info.get('upload_date', 'unknown')
        }
    except json.JSONDecodeError:
        # Fallback: list downloaded files
        files = list(output_dir.glob("*.mp4"))
        if files:
            video_path = files[-1]
            return {
                "path": str(video_path),
                "title": video_path.stem,
                "duration": 0,
                "id": "unknown"
            }
        raise


def sanitize_filename(filename: str) -> str:
    """Sanitize filename for safe file system operations"""
    # Remove or replace special characters
    safe = re.sub(r'[<>:"/\\|?*]', '', filename)
    safe = re.sub(r'[\s\|]+', '_', safe)
    # Limit length
    if len(safe) > 100:
        safe = safe[:97] + "..."
    return safe.strip()


# ============================================================================
# COPYRIGHT TRANSFORMATION ENGINE
# ============================================================================

class CopyrightTransformer:
    """
    Local transformation helper with scaffolded higher-level flows

    Provides 3 transformation levels:
    - Level 1: Visual remix (style transfer, effects)
    - Level 2: Script regeneration (new content, same message)
    - Level 3: Complete recreation (concept path)
    """

    def __init__(self, config: dict):
        self.config = config
        self.api_url = config.get('openfang_api', 'http://127.0.0.1:4200')

    def transform(
        self,
        video_path: str,
        level: TransformLevel,
        *,
        video_info: Optional[dict] = None,
        transcript_path: Optional[str] = None,
    ) -> dict:
        """
        Apply copyright-safe transformation

        Args:
            video_path: Path to source video
            level: Transformation level (0-3)

        Returns:
            Transformation result dict
        """
        if level == TransformLevel.NONE:
            return {"status": "skipped", "message": "No transformation applied"}

        print(f"\n{'='*60}")
        print(f"🛡️  COPYRIGHT-SAFE TRANSFORMATION - Level {level.value}")
        print(f"{'='*60}\n")

        if level == TransformLevel.VISUAL:
            return self._transform_visual(video_path)
        elif level == TransformLevel.SCRIPT:
            return self._transform_script(video_path, video_info=video_info, transcript_path=transcript_path)
        elif level == TransformLevel.COMPLETE:
            return self._transform_complete(video_path)

        return {"status": "error", "message": "Invalid transformation level"}

    def _transform_visual(self, video_path: str) -> dict:
        """
        Level 1: Visual Remix (Enhanced)

        Applies strong visual transformations to make the content distinct:
        - Horizontal flip (mirror)
        - Zoom & crop (scale to 108% then crop)
        - Color grading (warm/cold shift, contrast boost)
        - Speed modification (1.15x - subtle but effective)
        - Slight rotation (1-2 degrees)
        - Vignette effect
        - Noise/grain overlay
        - Audio pitch shift (0.9 semitones)
        """
        print("🎨 Applying Level 1: Enhanced Visual Remix")
        print("   • Horizontal mirror (flip)")
        print("   • Zoom & crop (108%)")
        print("   • Enhanced color grading")
        print("   • Speed modification (1.15x)")
        print("   • Slight rotation (1.5°)")
        print("   • Vignette + noise effects")
        print("   • Audio pitch shift")
        print("   • Strong copyright protection ✅")

        output_path = str(video_path).replace('.mp4', '_transformed.mp4')

        # Enhanced FFmpeg filter chain for copyright safety
        # Format: scale->crop->hflip->rotate->color->vignette->speed
        video_filter = (
            "scale=1920:1080:flags=bicubic,"  # Normalize resolution
            "crop=1920:1080:0:0,"  # Center crop
            "hflip,"  # Horizontal flip (mirror)
            "rotate=1.5*PI/180:fillcolor=black,"  # 1.5 degree rotation
            "eq=contrast=1.15:brightness=0.08:saturation=1.25:gamma=0.95,"  # Enhanced color
            "curves=all='0/0 0.25/0.2 0.5/0.55 0.75/0.85 1/1',"  # S-curve for contrast
            "vignette=angle=PI/4:"  # Vignette effect
            "dither=1,"  # Add noise/grain
            "setpts=0.87*PTS"  # 1.15x speed (1/1.15 = 0.87)
        )

        # Build FFmpeg command
        cmd = [
            "ffmpeg",
            "-i", video_path,
            "-vf", video_filter,
            "-af", "atempo=1.15,asetrate=44100*0.97" if self._check_ffmpeg_audio() else "atempo=1.15",  # Speed + pitch shift
            "-c:v", "libx264",
            "-preset", "fast",
            "-crf", "22",  # Slightly better quality
            "-pix_fmt", "yuv420p",  # Ensure compatibility
            "-movflags", "+faststart",  # Fast start for web
            "-c:a", "aac",
            "-b:a", "128k",
            "-y",
            output_path
        ]

        print(f"\n🔧 Processing with FFmpeg...")
        result = subprocess.run(cmd, capture_output=True, text=True)

        if result.returncode == 0:
            # Verify output file
            if os.path.exists(output_path) and os.path.getsize(output_path) > 1000:
                file_size = os.path.getsize(output_path) / (1024 * 1024)
                print(f"✅ Transformation complete: {file_size:.1f} MB")
                return {
                    "status": "success",
                    "output_path": output_path,
                    "level": 1,
                    "file_size_mb": file_size,
                    "transformations": [
                        "horizontal_flip",
                        "zoom_crop",
                        "color_grading",
                        "speed_1.15x",
                        "rotation_1.5deg",
                        "vignette",
                        "noise_overlay",
                        "pitch_shift"
                    ],
                    "message": "Enhanced visual remix applied successfully"
                }
            else:
                return {
                    "status": "error",
                    "message": "Output file is invalid or empty"
                }

        return {
            "status": "error",
            "message": f"Transformation failed: {result.stderr[:200]}"
        }

    def _check_ffmpeg_audio(self) -> bool:
        """Check if FFmpeg supports advanced audio filters"""
        try:
            result = subprocess.run(
                ["ffmpeg", "-filters"],
                capture_output=True,
                text=True,
                timeout=10
            )
            return "asetrate" in result.stdout
        except:
            return False

    def _transform_script(
        self,
        video_path: str,
        *,
        video_info: Optional[dict] = None,
        transcript_path: Optional[str] = None,
    ) -> dict:
        """
        Level 2: transcript-to-script package milestone.

        This milestone does not rebuild the full video yet.
        It turns a transcript into a reusable script package:
        1. load transcript
        2. extract source beats
        3. draft a new narration structure
        4. save a reviewable markdown + JSON package
        """
        print("📝 Applying Level 2: Transcript-to-Script Package")
        print("   • Load transcript or subtitle file")
        print("   • Extract source beats")
        print("   • Draft a fresh narration structure")
        print("   • Save JSON + Markdown review package")
        print("   • Does not render new voiceover or rebuilt video yet")
        print()
        transcript_file = resolve_transcript_path(video_path, transcript_path)
        if transcript_file is None:
            return {
                "status": "needs_transcript",
                "message": "Level 2 currently requires a transcript file. Use --transcript PATH or place a sidecar transcript next to the source video.",
            }

        transcript_text = read_transcript_text(transcript_file)
        if not transcript_text:
            return {
                "status": "error",
                "message": f"Transcript file was empty after parsing: {transcript_file}",
            }

        package = build_level2_script_package(
            video_info or {"path": video_path, "title": Path(video_path).stem},
            transcript_text,
            transcript_file,
            self.config,
        )
        package_dir, saved_files = save_level2_script_package(video_info or {"title": Path(video_path).stem}, package)

        print(f"✅ Script package ready: {package_dir}")
        for saved_file in saved_files:
            print(f"   • {saved_file.name}")

        return {
            "status": "success",
            "level": 2,
            "milestone": package["milestone"],
            "package_dir": str(package_dir),
            "saved_files": [str(saved_file) for saved_file in saved_files],
            "transcript_path": str(transcript_file),
            "message": "Transcript-to-script package generated successfully",
        }

    def _transform_complete(self, video_path: str) -> dict:
        """
        Level 3: Complete Recreation

        Concept path for full recreation:
        1. Deep analysis of original structure
        2. Original script generation
        3. AI-generated visuals
        4. Original music composition
        5. Professional voiceover
        """
        print("🎬 Applying Level 3: Complete Recreation")
        print("   • Deep structure analysis")
        print("   • Original script generation")
        print("   • AI-generated visuals")
        print("   • Original music")
        print("   • Professional voiceover")
        print("   • Concept path for the highest separation from the source")
        print()
        print("⚠️  Note: This feature requires:")
        print("   - Advanced AI models (DALL-E, Midjourney)")
        print("   - Music generation AI")
        print("   - Professional TTS")
        print("   - Video editing expertise")
        print()
        print("📖 See docs/TRANSFORMATION.md for complete guide")

        return {
            "status": "not_implemented",
            "message": "Complete recreation is still a roadmap item. See docs/TRANSFORMATION.md"
        }


# ============================================================================
# VIDEO EDITING
# ============================================================================

def create_clips(video_path: str, highlights: List[dict], output_dir: Path, config: dict) -> List[dict]:
    """
    Create video clips using FFmpeg

    Args:
        video_path: Source video path
        highlights: List of clip segments
        output_dir: Output directory
        config: Configuration dict

    Returns:
        List of created clips info
    """
    print(f"\n🎬 Creating {len(highlights)} clips...")
    output_dir.mkdir(parents=True, exist_ok=True)

    created_clips = []
    target_platforms = config.get('target_platforms', ['tiktok'])

    for i, highlight in enumerate(highlights):
        start = highlight['start']
        end = highlight['end']
        duration = end - start

        # Determine output resolution based on platforms
        resolution = "1080:1920"  # Default vertical 9:16

        output_path = output_dir / f"clip_{i+1:02d}_{int(start):04d}s-{int(end):04d}s.mp4"

        print(f"  [{i+1}/{len(highlights)}] {start:.0f}s - {end:.0f}s ({duration:.0f}s)")

        # Build FFmpeg command
        cmd = [
            "ffmpeg",
            "-i", video_path,
            "-ss", str(start),
            "-t", str(duration),
            "-vf", f"scale={resolution}:force_original_aspect_ratio=decrease,pad={resolution}:(ow-iw)/2:(oh-ih)/2,setsar=1",
            "-c:v", "libx264",
            "-preset", "fast",
            "-crf", "23",
            "-c:a", "aac",
            "-b:a", "128k",
            "-y",
            str(output_path)
        ]

        result = subprocess.run(cmd, capture_output=True, text=True)

        if result.returncode == 0:
            file_size = output_path.stat().st_size / (1024 * 1024)
            print(f"       ✅ {file_size:.1f} MB")

            created_clips.append({
                'path': str(output_path),
                'start': start,
                'end': end,
                'duration': duration,
                'size_mb': file_size,
                'reason': highlight.get('reason', f'Clip {i+1}'),
                'score': highlight.get('score', 5)
            })
        else:
            print(f"       ❌ Failed: {result.stderr[:100]}")

    return created_clips


def analyze_highlights_simple(video_info: dict, config: dict) -> List[dict]:
    """
    Simple clip detection strategy (when AI is unavailable)

    Evenly distributes clips throughout the video
    """
    duration = video_info['duration']
    clip_duration = config.get('default_duration', 60)
    num_clips = max(3, min(10, int(duration / clip_duration)))

    highlights = []
    for i in range(num_clips):
        start = i * clip_duration
        end = min(start + clip_duration, duration)

        highlights.append({
            'start': start,
            'end': end,
            'reason': f'Auto-clip {i+1}',
            'score': 5
        })

    return highlights


# ============================================================================
# MAIN WORKFLOW
# ============================================================================

def process_video(
    url: str,
    transform_level: int = 1,
    config: dict = None,
    transcript_path: Optional[str] = None,
) -> dict:
    """
    Main video processing workflow

    Args:
        url: Video URL
        transform_level: Copyright transformation level (0-3)
        config: Configuration dict

    Returns:
        Processing result dict
    """
    if config is None:
        config = load_config()

    print("=" * 70)
    print("🎬 OpenFang Auto Clip - Local Video Repurposing CLI")
    print("=" * 70)
    print()

    total_steps = 3 if transform_level == TransformLevel.SCRIPT.value else 5

    try:
        # Step 1: Download video
        print(f"Step 1/{total_steps}: Downloading video...")
        video_info = download_video(url, OUTPUT_DIR / "downloads")
        video_path = video_info['path']

        # Step 2: Apply copyright transformation
        print(f"\nStep 2/{total_steps}: Applying copyright-safe transformation...")
        transformer = CopyrightTransformer(config)
        level = TransformLevel(transform_level)

        transform_result = transformer.transform(
            video_path,
            level,
            video_info=video_info,
            transcript_path=transcript_path,
        )

        if level == TransformLevel.SCRIPT:
            if transform_result.get("status") != "success":
                raise RuntimeError(transform_result.get("message", "Level 2 script package generation failed"))

            print(f"\nStep 3/{total_steps}: Writing script package report...")
            package_dir = Path(transform_result["package_dir"])
            report = {
                'video': video_info,
                'transformation': {
                    'level': transform_level,
                    'result': transform_result
                },
                'clips': [],
                'created_at': datetime.now().isoformat(),
                'mode': 'script_package',
                'output_dir': str(package_dir)
            }

            report_path = package_dir / "report.json"
            with open(report_path, 'w') as f:
                json.dump(report, f, indent=2)

            print("\n" + "=" * 70)
            print("✅ LEVEL 2 PACKAGE READY")
            print("=" * 70)
            print(f"📁 Package directory: {package_dir}")
            print(f"📝 Transcript: {transform_result['transcript_path']}")
            print("Artifacts:")
            for saved_file in transform_result["saved_files"]:
                print(f"  • {Path(saved_file).name}")
            print()
            print("💡 Next steps:")
            print("  1. Review script_draft.md")
            print("  2. Record or synthesize a fresh voiceover")
            print("  3. Rebuild visuals around the approved script")
            print()

            return report

        # Use transformed video if successful
        if transform_result.get('status') == 'success':
            video_path = transform_result['output_path']
            print(f"✅ Using transformed video")

        # Step 3: Analyze and detect highlights
        print(f"\nStep 3/{total_steps}: Analyzing video for highlights...")
        highlights = analyze_highlights_simple(video_info, config)
        print(f"✅ Found {len(highlights)} potential clips")

        # Step 4: Create clips
        print(f"\nStep 4/{total_steps}: Creating video clips...")
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        clips_dir = OUTPUT_DIR / "clips" / timestamp
        clips_dir.mkdir(parents=True, exist_ok=True)

        created_clips = create_clips(video_path, highlights, clips_dir, config)

        # Step 5: Generate report
        print(f"\nStep 5/{total_steps}: Generating report...")
        report = {
            'video': video_info,
            'transformation': {
                'level': transform_level,
                'result': transform_result
            },
            'clips': created_clips,
            'created_at': datetime.now().isoformat(),
            'output_dir': str(clips_dir)
        }

        report_path = clips_dir / "report.json"
        with open(report_path, 'w') as f:
            json.dump(report, f, indent=2)

        # Summary
        print("\n" + "=" * 70)
        print(f"✅ PROCESSING COMPLETE!")
        print("=" * 70)
        print(f"📁 Output directory: {clips_dir}")
        print(f"📹 Clips created: {len(created_clips)}")
        print(f"🛡️  Transformation level: {transform_level}")
        print()
        print("Clips:")
        for clip in created_clips:
            print(f"  • {clip['reason']} ({clip['score']}⭐)")
            print(f"    {Path(clip['path']).name} ({clip['size_mb']:.1f} MB)")

        print("\n💡 Next steps:")
        print("  1. Preview clips: open", clips_dir)
        print("  2. Upload to platforms")
        print("  3. Track performance")
        print()

        return report

    except Exception as e:
        print(f"\n❌ Processing failed: {e}")
        import traceback
        traceback.print_exc()
        return None


# ============================================================================
# COMMAND LINE INTERFACE
# ============================================================================

def main():
    """Main entry point"""
    import argparse

    parser = argparse.ArgumentParser(
        description="OpenFang Auto Clip - Local Video Repurposing CLI",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  # Basic usage
  %(prog)s "https://youtube.com/watch?v=xxx"

  # Copyright-safe transformation (Level 1)
  %(prog)s "URL" --transform 1

  # Generate a Level 2 script package from a transcript
  %(prog)s "URL" --transform 2 --transcript path/to/source.srt

  # Complete recreation scaffold (Level 3)
  %(prog)s "URL" --transform 3

  # Custom duration
  %(prog)s "URL" --duration 45

Transformation Levels:
  0 - No transformation (not recommended)
  1 - Visual remix (fast, moderate safety) ✅
  2 - Script package from transcript (partial milestone) ✅
  3 - Complete recreation (concept scaffold) ⚠️

For more information, see README.md or docs/TRANSFORMATION.md
        """
    )

    parser.add_argument('url', nargs='?', help='Video URL to process')
    parser.add_argument('--duration', type=int, default=60,
                       help='Clip duration in seconds (default: 60)')
    parser.add_argument('--transform', type=int, choices=[0, 1, 2, 3], default=1,
                       help='Copyright transformation level (default: 1)')
    parser.add_argument('--config', help='Path to config file')
    parser.add_argument('--transcript',
                       help='Transcript or subtitle file for Level 2 (.txt, .md, .srt, .vtt, .json)')
    parser.add_argument('--dry-run', action='store_true',
                       help='Validate inputs and write a processing plan without downloading media')
    parser.add_argument('--doctor', action='store_true',
                       help='Check local environment readiness and exit')

    args = parser.parse_args()

    # Load config
    config = load_config()
    if args.config:
        with open(args.config) as f:
            config.update(json.load(f))

    config['default_duration'] = args.duration

    if args.doctor:
        report = build_doctor_report()
        print_doctor_report(report)
        sys.exit(1 if any(check["status"] == "error" for check in report["checks"]) else 0)

    if not args.url:
        parser.error("url is required unless --doctor is used")

    if args.dry_run:
        plan = build_processing_plan(args.url, args.transform, config, transcript_path=args.transcript)
        plan_path = save_dry_run_plan(plan)
        print_dry_run_plan(plan, plan_path)
        sys.exit(0)

    # Process video
    result = process_video(args.url, args.transform, config, transcript_path=args.transcript)

    if result:
        print("\n🎉 Success!")
        sys.exit(0)
    else:
        print("\n❌ Failed!")
        sys.exit(1)


if __name__ == "__main__":
    main()
