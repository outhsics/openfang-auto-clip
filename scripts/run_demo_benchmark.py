#!/usr/bin/env python3
"""Generate a reproducible local benchmark/demo run with synthetic media."""

from __future__ import annotations

import argparse
import json
import shutil
import subprocess
import sys
import tempfile
from pathlib import Path
from time import perf_counter

REPO_ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(REPO_ROOT))

from auto_clip import CopyrightTransformer, TransformLevel, create_clips, load_config  # noqa: E402


def ensure_ffmpeg() -> None:
    """Fail fast if ffmpeg is unavailable."""
    if shutil.which("ffmpeg") is None:
        raise RuntimeError("ffmpeg is required for the demo benchmark")


def generate_synthetic_source(output_path: Path, duration: int) -> None:
    """Create a synthetic demo input video using FFmpeg test sources."""
    output_path.parent.mkdir(parents=True, exist_ok=True)
    command = [
        "ffmpeg",
        "-f",
        "lavfi",
        "-i",
        "testsrc=size=1280x720:rate=30",
        "-f",
        "lavfi",
        "-i",
        "sine=frequency=880:sample_rate=44100",
        "-t",
        str(duration),
        "-c:v",
        "libx264",
        "-pix_fmt",
        "yuv420p",
        "-c:a",
        "aac",
        "-b:a",
        "128k",
        "-movflags",
        "+faststart",
        "-y",
        str(output_path),
    ]
    result = subprocess.run(command, capture_output=True, text=True)
    if result.returncode != 0:
        raise RuntimeError(f"failed to generate synthetic source: {result.stderr[:300]}")


def build_highlights(total_duration: int, segment_duration: int) -> list[dict]:
    """Build evenly sized demo highlight windows."""
    highlights = []
    current_start = 0
    clip_index = 1

    while current_start < total_duration:
        current_end = min(current_start + segment_duration, total_duration)
        highlights.append(
            {
                "start": current_start,
                "end": current_end,
                "reason": f"Benchmark clip {clip_index}",
                "score": 5,
            }
        )
        current_start = current_end
        clip_index += 1

    return highlights


def extract_preview_frame(video_path: Path, output_path: Path) -> None:
    """Extract a single preview frame from the first generated clip."""
    command = [
        "ffmpeg",
        "-i",
        str(video_path),
        "-vf",
        "select=eq(n\\,10)",
        "-vframes",
        "1",
        "-y",
        str(output_path),
    ]
    result = subprocess.run(command, capture_output=True, text=True)
    if result.returncode != 0:
        raise RuntimeError(f"failed to extract preview frame: {result.stderr[:300]}")


def extract_clip_previews(clip_paths: list[Path], output_dir: Path) -> list[Path]:
    """Extract one preview frame per clip for storyboard generation."""
    output_dir.mkdir(parents=True, exist_ok=True)
    preview_paths = []

    for index, clip_path in enumerate(clip_paths, start=1):
        preview_path = output_dir / f"clip_preview_{index:02d}.png"
        extract_preview_frame(clip_path, preview_path)
        if preview_path.exists():
            preview_paths.append(preview_path)

    return preview_paths


def create_storyboard(preview_paths: list[Path], output_path: Path) -> None:
    """Create a horizontal contact sheet from clip preview frames."""
    if not preview_paths:
        return

    command = ["ffmpeg"]
    for preview_path in preview_paths:
        command.extend(["-i", str(preview_path)])

    filter_parts = [f"[{index}:v]scale=320:-1[v{index}]" for index in range(len(preview_paths))]
    inputs = "".join(f"[v{index}]" for index in range(len(preview_paths)))
    filter_parts.append(f"{inputs}hstack=inputs={len(preview_paths)}[out]")

    command.extend(
        [
            "-filter_complex",
            ";".join(filter_parts),
            "-map",
            "[out]",
            "-frames:v",
            "1",
            "-y",
            str(output_path),
        ]
    )

    result = subprocess.run(command, capture_output=True, text=True)
    if result.returncode != 0:
        raise RuntimeError(f"failed to create storyboard: {result.stderr[:300]}")


def build_benchmark_summary(report: dict) -> dict:
    """Build human-readable summary metrics from the benchmark report."""
    clips = report.get("clips", [])
    clip_sizes = [clip.get("size_mb", 0.0) for clip in clips]
    return {
        "clip_count": len(clips),
        "total_clip_size_mb": round(sum(clip_sizes), 3),
        "average_clip_size_mb": round(sum(clip_sizes) / len(clip_sizes), 3) if clip_sizes else 0.0,
        "has_storyboard": bool(report["artifacts"].get("storyboard_path")),
        "has_preview": bool(report["artifacts"].get("preview_path")),
    }


def render_benchmark_summary_markdown(report: dict) -> str:
    """Render a bilingual markdown summary for the benchmark run."""
    summary = report["summary"]
    benchmark = report["benchmark"]
    timings = report["timings"]
    artifacts = report["artifacts"]
    lines = [
        "# Benchmark Summary / Benchmark 摘要",
        "",
        f"- Duration / 时长: {benchmark['duration_seconds']}s",
        f"- Segment duration / 分段时长: {benchmark['segment_duration']}s",
        f"- Transform level / 转换等级: {benchmark['transform_level']}",
        f"- Clip count / Clip 数量: {summary['clip_count']}",
        f"- Total clip size / Clip 总大小: {summary['total_clip_size_mb']} MB",
        f"- Average clip size / 平均 Clip 大小: {summary['average_clip_size_mb']} MB",
        f"- Total runtime / 总耗时: {timings['total_seconds']}s",
        "",
        "## Artifacts / 产物",
        "",
        f"- Report / 报告: {artifacts['report_path']}",
        f"- Summary / 摘要: {artifacts['summary_markdown_path']}",
        f"- Preview / 预览图: {artifacts['preview_path'] or 'none'}",
        f"- Storyboard / 分镜图: {artifacts['storyboard_path'] or 'none'}",
        f"- Clips dir / Clips 目录: {artifacts['clips_dir']}",
        "",
        "## Notes / 说明",
        "",
        "- This benchmark uses synthetic media, so it is safe to reproduce publicly. / 这个 benchmark 使用合成媒体，适合公开复现。",
        "- Use the storyboard and summary when sharing the repo or filing issues. / 对外展示仓库或提 issue 时，优先附上 storyboard 和摘要。",
        "",
    ]
    return "\n".join(lines)


def run_benchmark(
    output_dir: Path,
    duration: int,
    transform_level: int,
    segment_duration: int,
) -> dict:
    """Run a synthetic benchmark through the local processing primitives."""
    ensure_ffmpeg()
    config = load_config()
    config["default_duration"] = segment_duration

    benchmark_dir = output_dir.resolve()
    benchmark_dir.mkdir(parents=True, exist_ok=True)

    source_path = benchmark_dir / "synthetic_source.mp4"
    source_started = perf_counter()
    generate_synthetic_source(source_path, duration)
    source_seconds = round(perf_counter() - source_started, 3)

    video_path = source_path
    transform_summary = {"status": "skipped", "level": 0}
    transform_seconds = 0.0

    if transform_level > 0:
        transform_started = perf_counter()
        transformer = CopyrightTransformer(config)
        transform_summary = transformer.transform(str(source_path), TransformLevel(transform_level))
        transform_seconds = round(perf_counter() - transform_started, 3)
        if transform_summary.get("status") == "success":
            video_path = Path(transform_summary["output_path"])

    highlights = build_highlights(duration, segment_duration)
    clips_dir = benchmark_dir / "clips"

    clips_started = perf_counter()
    created_clips = create_clips(str(video_path), highlights, clips_dir, config)
    clip_seconds = round(perf_counter() - clips_started, 3)

    preview_path = benchmark_dir / "preview.png"
    storyboard_path = benchmark_dir / "storyboard.png"
    if created_clips:
        extract_preview_frame(Path(created_clips[0]["path"]), preview_path)
        with tempfile.TemporaryDirectory() as tmp_dir:
            preview_frames = extract_clip_previews(
                [Path(clip["path"]) for clip in created_clips[:4]],
                Path(tmp_dir),
            )
            create_storyboard(preview_frames, storyboard_path)

    report = {
        "benchmark": {
            "duration_seconds": duration,
            "segment_duration": segment_duration,
            "transform_level": transform_level,
            "created_at": __import__("datetime").datetime.now().isoformat(timespec="seconds"),
        },
        "timings": {
            "synthetic_source_generation_seconds": source_seconds,
            "transformation_seconds": transform_seconds,
            "clip_creation_seconds": clip_seconds,
            "total_seconds": round(source_seconds + transform_seconds + clip_seconds, 3),
        },
        "artifacts": {
            "source_path": str(source_path),
            "processed_video_path": str(video_path),
            "clips_dir": str(clips_dir),
            "preview_path": str(preview_path) if preview_path.exists() else None,
            "storyboard_path": str(storyboard_path) if storyboard_path.exists() else None,
            "clip_count": len(created_clips),
        },
        "transform_result": transform_summary,
        "clips": created_clips,
    }
    report["summary"] = build_benchmark_summary(report)

    report_path = benchmark_dir / "benchmark_report.json"
    report["artifacts"]["report_path"] = str(report_path)
    report_path.write_text(json.dumps(report, indent=2))

    summary_markdown_path = benchmark_dir / "benchmark_summary.md"
    report["artifacts"]["summary_markdown_path"] = str(summary_markdown_path)
    summary_markdown_path.write_text(render_benchmark_summary_markdown(report), encoding="utf-8")
    return report


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Run a synthetic OpenFang demo benchmark")
    parser.add_argument("--output-dir", default="tmp/demo-benchmark", help="Benchmark output directory")
    parser.add_argument("--duration", type=int, default=18, help="Synthetic source duration in seconds")
    parser.add_argument("--segment-duration", type=int, default=6, help="Clip segment duration in seconds")
    parser.add_argument("--transform", type=int, choices=[0, 1, 2, 3], default=1, help="Transform level")
    return parser.parse_args()


def main() -> int:
    args = parse_args()
    report = run_benchmark(
        REPO_ROOT / args.output_dir,
        duration=args.duration,
        transform_level=args.transform,
        segment_duration=args.segment_duration,
    )
    print("✅ Demo benchmark complete")
    print(f"   Clips: {report['artifacts']['clip_count']}")
    print(f"   Report: {Path(report['artifacts']['clips_dir']).parent / 'benchmark_report.json'}")
    print(f"   Summary: {report['artifacts']['summary_markdown_path']}")
    if report["artifacts"]["storyboard_path"]:
        print(f"   Storyboard: {report['artifacts']['storyboard_path']}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
