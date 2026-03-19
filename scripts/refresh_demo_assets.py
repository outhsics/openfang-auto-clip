#!/usr/bin/env python3
"""Refresh committed demo assets used for repo evaluation."""

from __future__ import annotations

import argparse
import json
import shutil
import sys
from datetime import datetime
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(REPO_ROOT))

from scripts import export_level2_demo_samples, run_demo_benchmark, run_local_evaluation  # noqa: E402


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


def build_sample_local_evaluation_report(
    benchmark_report_path: str,
    benchmark_summary_path: str,
    level2_index_path: str,
    level2_index: dict,
) -> dict:
    """Build a committed local-evaluation snapshot from refreshed sample assets."""
    average_score = round(
        sum(case["score"] for case in level2_index.get("cases", [])) / max(len(level2_index.get("cases", [])), 1)
    )
    report = {
        "created_at": datetime.now().isoformat(timespec="seconds"),
        "output_dir": "examples/evaluation",
        "status_en": "Ready for deeper evaluation",
        "status_zh": "可进入更深入评估",
        "doctor": {
            "status": "pass",
            "error_count": 0,
            "warn_count": 1,
            "checks": [
                {"name": "python", "status": "ok", "detail": "sample snapshot"},
                {"name": "ffmpeg", "status": "ok", "detail": "sample snapshot"},
                {"name": "yt-dlp", "status": "ok", "detail": "sample snapshot"},
                {"name": "openfang", "status": "warn", "detail": "sample snapshot"},
            ],
        },
        "benchmark": {
            "status": "pass",
            "status_en": "Completed",
            "status_zh": "已完成",
            "report_path": benchmark_report_path,
            "summary_path": benchmark_summary_path,
        },
        "level2_suite": {
            "status": "pass",
            "status_en": "Completed",
            "status_zh": "已完成",
            "average_score": average_score,
            "report_json_path": level2_index_path,
            "report_markdown_path": str(Path(level2_index_path).with_name("README.md")),
        },
        "next_steps_en": [
            "Inspect the committed benchmark summary and Level 2 sample artifacts first",
            "Run the live local evaluation path only after the committed samples look healthy",
            "Use real transcripts or URLs after the reproducible paths make sense",
        ],
        "next_steps_zh": [
            "先查看已提交的 benchmark 摘要和 Level 2 样例产物",
            "当这些已提交样例看起来正常后，再运行本地实时评估链路",
            "只有当可复现路径表现合理后，再接入真实 transcript 或 URL",
        ],
    }
    return report


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
    level2_index_path = REPO_ROOT / "examples" / "demo" / "level2_samples" / "index.json"
    level2_index = json.loads(level2_index_path.read_text(encoding="utf-8"))

    local_evaluation_sample = build_sample_local_evaluation_report(
        benchmark_report_path=str(sample_report_path.relative_to(REPO_ROOT)),
        benchmark_summary_path=str(benchmark_summary_dst.relative_to(REPO_ROOT)),
        level2_index_path=str(level2_index_path.relative_to(REPO_ROOT)),
        level2_index=level2_index,
    )
    local_evaluation_json_path = REPO_ROOT / "examples" / "evaluation" / "sample_local_evaluation_report.json"
    local_evaluation_markdown_path = REPO_ROOT / "examples" / "evaluation" / "sample_local_evaluation_report.md"
    local_evaluation_json_path.write_text(json.dumps(local_evaluation_sample, ensure_ascii=False, indent=2), encoding="utf-8")
    local_evaluation_markdown_path.write_text(
        run_local_evaluation.render_local_evaluation_markdown(local_evaluation_sample),
        encoding="utf-8",
    )

    return {
        "benchmark_report_path": str(sample_report_path.relative_to(REPO_ROOT)),
        "benchmark_summary_path": str(benchmark_summary_dst.relative_to(REPO_ROOT)),
        "level2_output_dir": level2_report["output_dir"],
        "local_evaluation_report_path": str(local_evaluation_json_path.relative_to(REPO_ROOT)),
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
    print(f"   Local evaluation sample / 本地评估样例: {result['local_evaluation_report_path']}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
