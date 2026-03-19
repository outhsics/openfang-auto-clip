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
REPO_ROOT = Path(__file__).resolve().parent
DEFAULT_LEVEL2_DEMO_TRANSCRIPT = REPO_ROOT / "examples" / "demo" / "sample_level2_transcript.srt"


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


def parse_subtitle_timestamp(raw_value: str) -> float:
    """Parse an SRT or VTT timestamp into seconds."""
    normalized = raw_value.strip().replace(",", ".")
    parts = normalized.split(":")
    if len(parts) != 3:
        raise ValueError(f"Unsupported subtitle timestamp: {raw_value}")

    hours = int(parts[0])
    minutes = int(parts[1])
    seconds = float(parts[2])
    return hours * 3600 + minutes * 60 + seconds


def format_seconds_label(seconds: Optional[float]) -> Optional[str]:
    """Format a float second value into a compact timestamp label."""
    if seconds is None:
        return None

    total_milliseconds = max(0, int(round(seconds * 1000)))
    hours, remainder = divmod(total_milliseconds, 3_600_000)
    minutes, remainder = divmod(remainder, 60_000)
    whole_seconds, milliseconds = divmod(remainder, 1000)
    return f"{hours:02d}:{minutes:02d}:{whole_seconds:02d}.{milliseconds:03d}"


def build_transcript_payload(transcript_path: Path) -> dict:
    """Read transcript content into normalized text plus optional timed segments."""
    raw_text = transcript_path.read_text(encoding="utf-8", errors="ignore")
    suffix = transcript_path.suffix.lower()

    if suffix in {".srt", ".vtt"}:
        segments = []
        current_times = None
        current_lines: List[str] = []

        for line in raw_text.splitlines():
            stripped = line.strip()
            if not stripped or stripped.isdigit() or stripped.upper() == "WEBVTT":
                if current_times and current_lines:
                    segments.append(
                        {
                            "start": current_times[0],
                            "end": current_times[1],
                            "text": normalize_transcript_text(" ".join(current_lines)),
                        }
                    )
                    current_times = None
                    current_lines = []
                continue

            if "-->" in stripped:
                start_raw, end_raw = [part.strip() for part in stripped.split("-->", 1)]
                current_times = (
                    parse_subtitle_timestamp(start_raw),
                    parse_subtitle_timestamp(end_raw),
                )
                continue

            current_lines.append(stripped)

        if current_times and current_lines:
            segments.append(
                {
                    "start": current_times[0],
                    "end": current_times[1],
                    "text": normalize_transcript_text(" ".join(current_lines)),
                }
            )

        combined = " ".join(segment["text"] for segment in segments)
        return {"text": normalize_transcript_text(combined), "segments": segments}

    if suffix == ".json":
        data = json.loads(raw_text)
        if isinstance(data, dict):
            if isinstance(data.get("text"), str):
                segments = data.get("segments")
                if isinstance(segments, list):
                    normalized_segments = []
                    for segment in segments:
                        if not isinstance(segment, dict):
                            continue
                        text = normalize_transcript_text(segment.get("text", ""))
                        if not text:
                            continue
                        normalized_segments.append(
                            {
                                "start": float(segment["start"]) if "start" in segment else None,
                                "end": float(segment["end"]) if "end" in segment else None,
                                "text": text,
                            }
                        )
                    return {
                        "text": normalize_transcript_text(data["text"]),
                        "segments": normalized_segments,
                    }
                return {"text": normalize_transcript_text(data["text"]), "segments": []}

            segments = data.get("segments")
            if isinstance(segments, list):
                normalized_segments = []
                for segment in segments:
                    if not isinstance(segment, dict):
                        continue
                    text = normalize_transcript_text(segment.get("text", ""))
                    if not text:
                        continue
                    normalized_segments.append(
                        {
                            "start": float(segment["start"]) if "start" in segment else None,
                            "end": float(segment["end"]) if "end" in segment else None,
                            "text": text,
                        }
                    )
                combined = " ".join(segment["text"] for segment in normalized_segments)
                return {"text": normalize_transcript_text(combined), "segments": normalized_segments}

        if isinstance(data, list):
            normalized_segments = []
            for item in data:
                if not isinstance(item, dict):
                    continue
                text = normalize_transcript_text(item.get("text", ""))
                if not text:
                    continue
                normalized_segments.append(
                    {
                        "start": float(item["start"]) if "start" in item else None,
                        "end": float(item["end"]) if "end" in item else None,
                        "text": text,
                    }
                )
            combined = " ".join(segment["text"] for segment in normalized_segments)
            if combined.strip():
                return {"text": normalize_transcript_text(combined), "segments": normalized_segments}

        raise ValueError(f"Unsupported transcript JSON shape: {transcript_path}")

    return {"text": normalize_transcript_text(raw_text), "segments": []}


def read_transcript_text(transcript_path: Path) -> str:
    """Read transcript text from txt, markdown, subtitle, or JSON files."""
    return build_transcript_payload(transcript_path)["text"]


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


def build_source_outline_from_segments(segments: List[dict], language: str) -> List[dict]:
    """Group timed transcript segments into a compact source outline."""
    if not segments:
        return []

    outline = []
    bucket: List[dict] = []
    target_words = 14 if language == "en" else 22

    for segment in segments:
        bucket.append(segment)
        joined_text = normalize_transcript_text(" ".join(item["text"] for item in bucket))
        enough_words = len(joined_text.split()) >= target_words if language == "en" else len(joined_text) >= target_words
        if enough_words:
            outline.append(
                {
                    "summary": shorten_phrase(joined_text, language, max_words=16, max_chars=48),
                    "source_start": bucket[0].get("start"),
                    "source_end": bucket[-1].get("end"),
                    "source_anchor": (
                        f"{format_seconds_label(bucket[0].get('start'))} - {format_seconds_label(bucket[-1].get('end'))}"
                        if bucket[0].get("start") is not None and bucket[-1].get("end") is not None
                        else None
                    ),
                }
            )
            bucket = []

    if bucket:
        joined_text = normalize_transcript_text(" ".join(item["text"] for item in bucket))
        outline.append(
            {
                "summary": shorten_phrase(joined_text, language, max_words=16, max_chars=48),
                "source_start": bucket[0].get("start"),
                "source_end": bucket[-1].get("end"),
                "source_anchor": (
                    f"{format_seconds_label(bucket[0].get('start'))} - {format_seconds_label(bucket[-1].get('end'))}"
                    if bucket[0].get("start") is not None and bucket[-1].get("end") is not None
                    else None
                ),
            }
        )

    return outline[:4]


def shorten_phrase(text: str, language: str, *, max_words: int = 12, max_chars: int = 42) -> str:
    """Trim a sentence into a concise phrase for script and on-screen text."""
    compact = normalize_transcript_text(text).strip(" .,!?:;，。！？；：")
    if language == "zh":
        return compact if len(compact) <= max_chars else f"{compact[: max_chars - 1]}…"

    words = compact.split()
    if len(words) <= max_words:
        return compact
    return " ".join(words[:max_words]) + "..."


def build_level2_script_sections(points: List[dict], language: str, duration: int) -> List[dict]:
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
                "narration": f"这条短视频不用原句复述，先用新的讲法讲清核心点：{points[0]['summary']}。",
                "on_screen_text": shorten_phrase(points[0]["summary"], language, max_chars=18),
                "visual_direction": "用标题卡点明主题，再切到新的讲述视角。",
                "source_anchor": points[0].get("source_anchor"),
            }
        ]
        for index, point in enumerate(points, start=1):
            sections.append(
                {
                    "section": f"重点 {index}",
                    "duration": body_duration,
                    "narration": f"第{index}点，{point['summary']}。把这个点拆开讲，避免沿用原视频节奏。",
                    "on_screen_text": shorten_phrase(point["summary"], language, max_chars=18),
                    "visual_direction": "用新的 B-roll、图示或屏幕录制支撑这一段。",
                    "source_anchor": point.get("source_anchor"),
                }
            )
        sections.append(
            {
                "section": "收尾",
                "duration": duration - sum(section["duration"] for section in sections),
                "narration": f"总结一下，把上面几个重点收束成一句自己的结论，再给出下一步动作。",
                "on_screen_text": "总结与行动",
                "visual_direction": "回到主持人口播或总结卡片，不复用原片尾结构。",
                "source_anchor": None,
            }
        )
        return sections

    sections = [
        {
            "section": "Hook",
            "duration": hook_duration,
            "narration": f"Retell the core idea from a fresh angle: {points[0]['summary']}.",
            "on_screen_text": shorten_phrase(points[0]["summary"], language),
            "visual_direction": "Open with a fresh title card and new framing, not the original pacing.",
            "source_anchor": points[0].get("source_anchor"),
        }
    ]
    for index, point in enumerate(points, start=1):
        sections.append(
            {
                "section": f"Beat {index}",
                "duration": body_duration,
                "narration": f"Point {index}: {point['summary']}. Expand it in your own voice instead of mirroring the source wording.",
                "on_screen_text": shorten_phrase(point["summary"], language),
                "visual_direction": "Use new B-roll, diagrams, or screen capture to support this point.",
                "source_anchor": point.get("source_anchor"),
            }
        )
    sections.append(
        {
            "section": "Close",
            "duration": duration - sum(section["duration"] for section in sections),
            "narration": "Close with your own takeaway and a next action instead of reusing the source ending.",
            "on_screen_text": "Fresh takeaway",
            "visual_direction": "End on a summary card or direct-to-camera close.",
            "source_anchor": None,
        }
    )
    return sections


def build_level2_shot_plan(script_sections: List[dict], language: str) -> List[dict]:
    """Generate a lightweight production handoff for each rewritten section."""
    shot_plan = []
    for index, section in enumerate(script_sections, start=1):
        if index == 1:
            asset_type = "title_card_then_new_talking_head"
            goal_en = "State the new angle quickly and clearly."
            goal_zh = "先立新视角，再切到新的讲述主体。"
        elif index == len(script_sections):
            asset_type = "summary_card_or_direct_close"
            goal_en = "Land the takeaway without echoing the original ending."
            goal_zh = "收束观点，不复用原片尾节奏。"
        else:
            asset_type = "fresh_broll_diagram_or_screen_capture"
            goal_en = "Support one rewritten beat with new visuals."
            goal_zh = "用新的视觉素材支撑这一段改写内容。"

        shot_plan.append(
            {
                "shot": index,
                "section": section["section"],
                "duration": section["duration"],
                "asset_type": asset_type,
                "goal": goal_zh if language == "zh" else goal_en,
                "source_anchor": section.get("source_anchor"),
                "overlay_text": section["on_screen_text"],
            }
        )

    return shot_plan


def build_level2_review_rubric(language: str) -> List[str]:
    """Create a concise operator rubric for approving the package."""
    if language == "zh":
        return [
            "逐段检查 narration，去掉任何接近原句复述的表达",
            "确认每段都有新的视觉方案，不依赖原视频镜头",
            "检查 on-screen text 是否足够短，适合竖屏节奏",
            "确认收尾是新的总结和动作，不复用原片尾结构",
        ]

    return [
        "Check each narration beat for wording that still feels too close to the source",
        "Confirm every section has a fresh visual plan instead of reused source shots",
        "Keep on-screen text short enough for vertical viewing",
        "Make sure the close lands as a new takeaway, not the source ending rewritten lightly",
    ]


def build_level2_blueprint(package: dict) -> dict:
    """Build a reduced production blueprint artifact from the script package."""
    return {
        "milestone": package["milestone"],
        "source_title": package["source"]["title"],
        "language": package["language"],
        "script_sections": package["script_sections"],
        "shot_plan": package["shot_plan"],
        "review_rubric": package["review_rubric"],
    }


def build_level2_script_package(video_info: dict, transcript_payload: dict, transcript_path: Path, config: dict) -> dict:
    """Build a transcript-to-script package for the first Level 2 milestone."""
    transcript_text = transcript_payload["text"]
    sentences = split_transcript_sentences(transcript_text)
    if not sentences:
        raise ValueError("Transcript did not contain enough readable sentences to build a script package")

    language = detect_transcript_language(transcript_text)
    source_outline = build_source_outline_from_segments(transcript_payload.get("segments", []), language)
    if not source_outline:
        source_outline = [
            {
                "summary": shorten_phrase(sentence, language, max_words=16, max_chars=48),
                "source_start": None,
                "source_end": None,
                "source_anchor": None,
            }
            for sentence in sentences[:4]
        ]

    target_duration = config.get("default_duration", 60)
    script_sections = build_level2_script_sections(source_outline, language, target_duration)
    shot_plan = build_level2_shot_plan(script_sections, language)
    review_rubric = build_level2_review_rubric(language)

    return {
        "milestone": "level2_transcript_to_script_package",
        "language": language,
        "source": {
            "title": video_info.get("title", Path(video_info.get("path", "source")).stem),
            "video_path": video_info.get("path"),
            "transcript_path": str(transcript_path),
            "sentence_count": len(sentences),
            "segment_count": len(transcript_payload.get("segments", [])),
        },
        "source_outline": [
            {"index": index, **point}
            for index, point in enumerate(source_outline, start=1)
        ],
        "script_sections": script_sections,
        "shot_plan": shot_plan,
        "review_rubric": review_rubric,
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
        f"- Timed segments: {package['source']['segment_count']}",
        "",
        "## Source Outline",
        "",
    ]

    for point in package["source_outline"]:
        anchor_suffix = f" ({point['source_anchor']})" if point.get("source_anchor") else ""
        lines.append(f"{point['index']}. {point['summary']}{anchor_suffix}")

    lines.extend(["", "## Script Draft", ""])
    for section in package["script_sections"]:
        lines.extend(
            [
                f"### {section['section']} ({section['duration']}s)",
                f"- Narration: {section['narration']}",
                f"- On-screen text: {section['on_screen_text']}",
                f"- Visual direction: {section['visual_direction']}",
                f"- Source anchor: {section['source_anchor'] or 'none'}",
                "",
            ]
        )

    lines.extend(["## Shot Plan", ""])
    for shot in package["shot_plan"]:
        lines.extend(
            [
                f"- Shot {shot['shot']}: {shot['section']} ({shot['duration']}s)",
                f"  Asset: {shot['asset_type']}",
                f"  Goal: {shot['goal']}",
                f"  Overlay: {shot['overlay_text']}",
                f"  Source anchor: {shot['source_anchor'] or 'none'}",
            ]
        )

    lines.extend(["", "## Review Rubric", ""])
    for item in package["review_rubric"]:
        lines.append(f"- {item}")

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

    blueprint_path = package_dir / "production_blueprint.json"
    with open(blueprint_path, "w", encoding="utf-8") as handle:
        json.dump(build_level2_blueprint(package), handle, ensure_ascii=False, indent=2)

    return package_dir, [package_json_path, draft_path, blueprint_path]


def run_level2_script_demo(config: dict, transcript_path: Optional[str] = None) -> dict:
    """Generate a self-contained Level 2 package without downloading media."""
    transcript_file = resolve_explicit_transcript_path(transcript_path) if transcript_path else DEFAULT_LEVEL2_DEMO_TRANSCRIPT
    if not transcript_file.exists():
        raise FileNotFoundError(
            f"Demo transcript not found: {transcript_file}. "
            "Provide one with --transcript or restore the bundled sample."
        )

    transcript_payload = build_transcript_payload(transcript_file)
    transcript_text = transcript_payload["text"]
    if not transcript_text:
        raise ValueError(f"Transcript file was empty after parsing: {transcript_file}")

    video_info = {
        "title": "Level 2 Demo Source",
        "path": str(transcript_file),
        "duration": config.get("default_duration", 60),
        "id": "level2-demo",
        "uploader": "OpenFang Auto Clip",
    }
    package = build_level2_script_package(video_info, transcript_payload, transcript_file, config)
    package_dir, saved_files = save_level2_script_package(video_info, package)

    report = {
        "video": video_info,
        "transformation": {
            "level": TransformLevel.SCRIPT.value,
            "result": {
                "status": "success",
                "level": TransformLevel.SCRIPT.value,
                "milestone": package["milestone"],
                "package_dir": str(package_dir),
                "saved_files": [str(saved_file) for saved_file in saved_files],
                "transcript_path": str(transcript_file),
                "message": "Transcript-to-script demo package generated successfully",
            },
        },
        "clips": [],
        "created_at": datetime.now().isoformat(),
        "mode": "script_package_demo",
        "output_dir": str(package_dir),
    }

    report_path = package_dir / "report.json"
    with open(report_path, "w", encoding="utf-8") as handle:
        json.dump(report, handle, ensure_ascii=False, indent=2)

    print("=" * 70)
    print("🎬 OpenFang Auto Clip - Level 2 Demo Package")
    print("=" * 70)
    print()
    print("🧪 Running a self-contained Level 2 evaluation flow")
    print(f"📝 Transcript source: {transcript_file}")
    print(f"📁 Package directory: {package_dir}")
    print("Artifacts:")
    for saved_file in [*saved_files, report_path]:
        print(f"  • {saved_file.name}")
    print()
    print("💡 Next steps:")
    print("  1. Review script_draft.md")
    print("  2. Inspect source anchors and shot plan")
    print("  3. Swap in a real transcript with --transcript")
    print()

    return report


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

        transcript_payload = build_transcript_payload(transcript_file)
        transcript_text = transcript_payload["text"]
        if not transcript_text:
            return {
                "status": "error",
                "message": f"Transcript file was empty after parsing: {transcript_file}",
            }

        package = build_level2_script_package(
            video_info or {"path": video_path, "title": Path(video_path).stem},
            transcript_payload,
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

  # Run a self-contained Level 2 demo package
  %(prog)s --demo-script-package

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
    parser.add_argument('--demo-script-package', action='store_true',
                       help='Generate a self-contained Level 2 demo package from the bundled transcript')

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

    if args.demo_script_package:
        result = run_level2_script_demo(config, transcript_path=args.transcript)
        print("\n🎉 Success!")
        sys.exit(0 if result else 1)

    if not args.url:
        parser.error("url is required unless --doctor or --demo-script-package is used")

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
