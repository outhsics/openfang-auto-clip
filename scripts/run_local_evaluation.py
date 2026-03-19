#!/usr/bin/env python3
"""Run the fastest reproducible local evaluation path."""

from __future__ import annotations

import argparse
import json
import sys
from datetime import datetime
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(REPO_ROOT))

import auto_clip  # noqa: E402
from scripts import run_demo_benchmark, run_level2_demo_suite  # noqa: E402


def summarize_doctor(report: dict) -> dict:
    """Summarize doctor output for the combined evaluation report."""
    checks = report.get("checks", [])
    errors = [check for check in checks if check["status"] == "error"]
    warns = [check for check in checks if check["status"] == "warn"]
    return {
        "status": "pass" if not errors else "fail",
        "error_count": len(errors),
        "warn_count": len(warns),
        "checks": checks,
    }


def render_local_evaluation_markdown(report: dict) -> str:
    """Render a bilingual local evaluation summary."""
    lines = [
        "# Local Evaluation Report / 本地评估报告",
        "",
        f"- Generated / 生成时间: {report['created_at']}",
        f"- Overall status / 总状态: {report['status_en']} / {report['status_zh']}",
        "",
        "## Doctor / 环境检查",
        "",
        f"- Status / 状态: {report['doctor']['status']}",
        f"- Errors / 错误数: {report['doctor']['error_count']}",
        f"- Warnings / 警告数: {report['doctor']['warn_count']}",
        "",
        "## Benchmark / 基准测试",
        "",
        f"- Status / 状态: {report['benchmark']['status_en']} / {report['benchmark']['status_zh']}",
        f"- Report / 报告: {report['benchmark'].get('report_path') or 'none'}",
        "",
        "## Level 2 Suite / Level 2 套件",
        "",
        f"- Status / 状态: {report['level2_suite']['status_en']} / {report['level2_suite']['status_zh']}",
        f"- Average score / 平均得分: {report['level2_suite'].get('average_score', 0)}/100",
        f"- Report / 报告: {report['level2_suite'].get('report_markdown_path') or 'none'}",
        "",
        "## Next Steps / 下一步",
        "",
    ]
    for item_en, item_zh in zip(report["next_steps_en"], report["next_steps_zh"]):
        lines.append(f"- {item_en} / {item_zh}")
    lines.append("")
    return "\n".join(lines)


def run_local_evaluation(output_dir: Path, benchmark_duration: int, segment_duration: int, level2_duration: int) -> dict:
    """Run doctor, benchmark, and Level 2 suite in one reproducible flow."""
    output_dir = output_dir.resolve()
    output_dir.mkdir(parents=True, exist_ok=True)

    doctor_raw = auto_clip.build_doctor_report()
    doctor = summarize_doctor(doctor_raw)

    benchmark_dir = output_dir / "benchmark"
    suite_dir = output_dir / "level2_suite"

    benchmark_result = {
        "status": "skipped",
        "status_en": "Skipped",
        "status_zh": "已跳过",
        "report_path": None,
    }

    ffmpeg_ready = any(
        check["name"] == "ffmpeg" and check["status"] == "ok"
        for check in doctor_raw.get("checks", [])
    )
    if ffmpeg_ready:
        benchmark_report = run_demo_benchmark.run_benchmark(
            benchmark_dir,
            duration=benchmark_duration,
            transform_level=1,
            segment_duration=segment_duration,
        )
        benchmark_result = {
            "status": "pass",
            "status_en": "Completed",
            "status_zh": "已完成",
            "report_path": str(benchmark_dir / "benchmark_report.json"),
            "clip_count": benchmark_report["artifacts"]["clip_count"],
            "storyboard_path": benchmark_report["artifacts"]["storyboard_path"],
        }
    else:
        benchmark_result = {
            "status": "skipped",
            "status_en": "Skipped because ffmpeg is unavailable",
            "status_zh": "由于缺少 ffmpeg 已跳过",
            "report_path": None,
        }

    suite_report = run_level2_demo_suite.run_suite(suite_dir, duration=level2_duration)
    level2_suite = {
        "status": "pass",
        "status_en": "Completed",
        "status_zh": "已完成",
        "average_score": suite_report["average_score"],
        "report_json_path": suite_report["report_json_path"],
        "report_markdown_path": suite_report["report_markdown_path"],
    }

    if doctor["status"] == "fail":
        status_en = "Needs environment fixes"
        status_zh = "需要先修环境"
    elif benchmark_result["status"] == "skipped":
        status_en = "Partially complete"
        status_zh = "部分完成"
    else:
        status_en = "Ready for deeper evaluation"
        status_zh = "可进入更深入评估"

    report = {
        "created_at": datetime.now().isoformat(timespec="seconds"),
        "output_dir": str(output_dir),
        "status_en": status_en,
        "status_zh": status_zh,
        "doctor": doctor,
        "benchmark": benchmark_result,
        "level2_suite": level2_suite,
        "next_steps_en": [
            "Fix doctor errors first if any required tools are missing",
            "Inspect the benchmark storyboard and Level 2 suite reports before trying a real URL",
            "Use a real transcript next after the bundled Level 2 suite looks healthy",
        ],
        "next_steps_zh": [
            "如果 doctor 有错误，先补齐必需工具",
            "在测试真实 URL 前，先检查 benchmark storyboard 和 Level 2 suite 报告",
            "当内置 Level 2 suite 表现正常后，再接入真实 transcript",
        ],
    }

    report_json_path = output_dir / "local_evaluation_report.json"
    report_json_path.write_text(json.dumps(report, ensure_ascii=False, indent=2), encoding="utf-8")
    report_markdown_path = output_dir / "local_evaluation_report.md"
    report_markdown_path.write_text(render_local_evaluation_markdown(report), encoding="utf-8")

    report["report_json_path"] = str(report_json_path)
    report["report_markdown_path"] = str(report_markdown_path)
    return report


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Run the local OpenFang evaluation path")
    parser.add_argument("--output-dir", default="tmp/local-evaluation", help="Output directory")
    parser.add_argument("--benchmark-duration", type=int, default=18, help="Synthetic benchmark duration")
    parser.add_argument("--segment-duration", type=int, default=6, help="Benchmark clip segment duration")
    parser.add_argument("--level2-duration", type=int, default=45, help="Level 2 target script duration")
    return parser.parse_args()


def main() -> int:
    args = parse_args()
    report = run_local_evaluation(
        REPO_ROOT / args.output_dir,
        benchmark_duration=args.benchmark_duration,
        segment_duration=args.segment_duration,
        level2_duration=args.level2_duration,
    )
    print("✅ Local evaluation complete")
    print("✅ 本地评估已完成")
    print(f"   Status / 状态: {report['status_en']} / {report['status_zh']}")
    print(f"   JSON report / JSON 报告: {report['report_json_path']}")
    print(f"   Markdown report / Markdown 报告: {report['report_markdown_path']}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
