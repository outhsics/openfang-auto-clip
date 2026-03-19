#!/usr/bin/env python3
"""Refresh committed demo assets used for repo evaluation."""

from __future__ import annotations

import argparse
import json
import shutil
import sys
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(REPO_ROOT))

from scripts import export_level2_demo_samples, run_demo_benchmark  # noqa: E402


def relativize_from(path: str | None, source_dir: Path, target_root: str) -> str | None:
    """Convert an absolute path under source_dir into a stable repo-relative sample path."""
    if not path:
        return None
    candidate = Path(path)
    try:
        relative = candidate.resolve().relative_to(source_dir.resolve())
    except ValueError:
        return path
    return str(Path(target_root) / relative)


def normalize_benchmark_report(report: dict, target_root: str = "tmp/demo-benchmark") -> dict:
    """Rewrite transient benchmark paths into stable sample paths."""
    normalized = json.loads(json.dumps(report))
    source_dir = Path(report["artifacts"]["clips_dir"]).parent

    artifacts = normalized["artifacts"]
    artifacts["source_path"] = relativize_from(artifacts.get("source_path"), source_dir, target_root)
    artifacts["processed_video_path"] = relativize_from(artifacts.get("processed_video_path"), source_dir, target_root)
    artifacts["clips_dir"] = relativize_from(artifacts.get("clips_dir"), source_dir, target_root)
    artifacts["preview_path"] = relativize_from(artifacts.get("preview_path"), source_dir, target_root)
    artifacts["storyboard_path"] = relativize_from(artifacts.get("storyboard_path"), source_dir, target_root)
    artifacts["report_path"] = str(Path(target_root) / "benchmark_report.json")
    artifacts["summary_markdown_path"] = str(Path(target_root) / "benchmark_summary.md")

    transform_result = normalized.get("transform_result", {})
    if transform_result.get("output_path"):
        transform_result["output_path"] = relativize_from(transform_result["output_path"], source_dir, target_root)

    for clip in normalized.get("clips", []):
        clip["path"] = relativize_from(clip.get("path"), source_dir, target_root)

    return normalized


def refresh_assets(
    benchmark_output_dir: Path,
    benchmark_duration: int = 18,
    segment_duration: int = 6,
    level2_duration: int = 45,
) -> dict:
    """Refresh committed benchmark and Level 2 sample assets."""
    benchmark_output_dir.mkdir(parents=True, exist_ok=True)
    benchmark_report = run_demo_benchmark.run_benchmark(
        benchmark_output_dir,
        duration=benchmark_duration,
        transform_level=1,
        segment_duration=segment_duration,
    )
    normalized_report = normalize_benchmark_report(benchmark_report)

    sample_report_path = REPO_ROOT / "examples" / "benchmark" / "sample_benchmark_report.json"
    sample_report_path.write_text(json.dumps(normalized_report, ensure_ascii=False, indent=2), encoding="utf-8")

    benchmark_summary_src = Path(benchmark_report["artifacts"]["summary_markdown_path"])
    benchmark_summary_dst = REPO_ROOT / "examples" / "benchmark" / "sample_benchmark_summary.md"
    shutil.copyfile(benchmark_summary_src, benchmark_summary_dst)

    level2_report = export_level2_demo_samples.export_samples(REPO_ROOT / "examples" / "demo" / "level2_samples", duration=level2_duration)

    return {
        "benchmark_report_path": str(sample_report_path.relative_to(REPO_ROOT)),
        "benchmark_summary_path": str(benchmark_summary_dst.relative_to(REPO_ROOT)),
        "level2_output_dir": level2_report["output_dir"],
    }


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Refresh committed repo demo assets")
    parser.add_argument("--benchmark-output-dir", default="tmp/refresh-demo-assets", help="Temporary benchmark output directory")
    parser.add_argument("--benchmark-duration", type=int, default=18, help="Benchmark duration in seconds")
    parser.add_argument("--segment-duration", type=int, default=6, help="Benchmark clip segment duration")
    parser.add_argument("--level2-duration", type=int, default=45, help="Level 2 target script duration")
    return parser.parse_args()


def main() -> int:
    args = parse_args()
    result = refresh_assets(
        REPO_ROOT / args.benchmark_output_dir,
        benchmark_duration=args.benchmark_duration,
        segment_duration=args.segment_duration,
        level2_duration=args.level2_duration,
    )
    print("✅ Refreshed demo assets")
    print("✅ 已刷新 demo 资产")
    print(f"   Benchmark report / Benchmark 报告: {result['benchmark_report_path']}")
    print(f"   Benchmark summary / Benchmark 摘要: {result['benchmark_summary_path']}")
    print(f"   Level 2 samples / Level 2 样例: {result['level2_output_dir']}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
