#!/usr/bin/env python3
"""Run a reproducible bilingual Level 2 evaluation suite."""

from __future__ import annotations

import argparse
import json
import sys
from datetime import datetime
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(REPO_ROOT))

import auto_clip  # noqa: E402


CASES = [
    {
        "id": "en_srt",
        "label_en": "English SRT transcript",
        "label_zh": "英文 SRT transcript",
        "title": "Level 2 Demo EN SRT",
        "transcript": REPO_ROOT / "examples" / "demo" / "sample_level2_transcript.srt",
    },
    {
        "id": "zh_srt",
        "label_en": "Chinese SRT transcript",
        "label_zh": "中文 SRT transcript",
        "title": "Level 2 Demo ZH SRT",
        "transcript": REPO_ROOT / "examples" / "demo" / "sample_level2_transcript_zh.srt",
    },
    {
        "id": "en_json",
        "label_en": "English JSON transcript",
        "label_zh": "英文 JSON transcript",
        "title": "Level 2 Demo EN JSON",
        "transcript": REPO_ROOT / "examples" / "demo" / "sample_level2_transcript.json",
    },
    {
        "id": "zh_vtt",
        "label_en": "Chinese VTT transcript",
        "label_zh": "中文 VTT transcript",
        "title": "Level 2 Demo ZH VTT",
        "transcript": REPO_ROOT / "examples" / "demo" / "sample_level2_transcript_zh.vtt",
    },
]


def run_case(case: dict, config: dict) -> dict:
    """Generate one Level 2 package and extract summary metrics."""
    transcript_path = case["transcript"]
    transcript_payload = auto_clip.build_transcript_payload(transcript_path)
    video_info = {
        "title": case["title"],
        "path": str(transcript_path),
        "duration": config.get("default_duration", 60),
        "id": f"level2-suite-{case['id']}",
        "uploader": "OpenFang Auto Clip",
    }
    package = auto_clip.build_level2_script_package(video_info, transcript_payload, transcript_path, config)
    package_dir, saved_files = auto_clip.save_level2_script_package(video_info, package)
    review = auto_clip.build_level2_package_review(package)

    return {
        "id": case["id"],
        "label_en": case["label_en"],
        "label_zh": case["label_zh"],
        "language": package["language"],
        "transcript_format": transcript_path.suffix.lower().lstrip("."),
        "transcript_path": str(transcript_path),
        "package_dir": str(package_dir),
        "score": review["score"],
        "status": review["status"],
        "status_label_en": review["status_label_en"],
        "status_label_zh": review["status_label_zh"],
        "metrics": review["metrics"],
        "saved_files": [str(saved_file) for saved_file in saved_files],
    }


def render_suite_markdown(report: dict) -> str:
    """Render a bilingual markdown summary for the suite."""
    lines = [
        "# Level 2 Demo Suite / Level 2 演示套件",
        "",
        f"- Generated / 生成时间: {report['created_at']}",
        f"- Output dir / 输出目录: {report['output_dir']}",
        f"- Average score / 平均得分: {report['average_score']}/100",
        "",
        "## Cases / 用例",
        "",
    ]

    for case in report["cases"]:
        lines.extend(
            [
                f"### {case['label_en']} / {case['label_zh']}",
                f"- Status / 状态: {case['status_label_en']} / {case['status_label_zh']}",
                f"- Score / 得分: {case['score']}/100",
                f"- Format / 格式: {case['transcript_format']}",
                f"- Package / 包目录: {case['package_dir']}",
                f"- Transcript / Transcript 路径: {case['transcript_path']}",
                f"- Script sections / 脚本段落数: {case['metrics']['script_section_count']}",
                f"- Timed segments / 时间片段数: {case['metrics']['timed_segment_count']}",
                f"- Section anchors / 脚本锚点数: {case['metrics']['section_anchor_count']}",
                "",
            ]
        )

    lines.extend(["## Notes / 说明", ""])
    for item_en, item_zh in zip(report["notes_en"], report["notes_zh"]):
        lines.append(f"- {item_en} / {item_zh}")
    lines.append("")
    return "\n".join(lines)


def run_suite(output_dir: Path, duration: int) -> dict:
    """Run the bilingual Level 2 suite and persist summary artifacts."""
    output_dir = output_dir.resolve()
    output_dir.mkdir(parents=True, exist_ok=True)

    config = auto_clip.load_config()
    config["default_duration"] = duration
    auto_clip.OUTPUT_DIR = output_dir

    cases = [run_case(case, config) for case in CASES]
    average_score = round(sum(case["score"] for case in cases) / len(cases)) if cases else 0
    report = {
        "created_at": datetime.now().isoformat(timespec="seconds"),
        "output_dir": str(output_dir),
        "average_score": average_score,
        "cases": cases,
        "notes_en": [
            "This suite uses bundled bilingual transcript fixtures across multiple formats and does not download source media.",
            "Each case writes script package, blueprint, and bilingual review artifacts.",
            "Use these outputs to compare Level 2 structure before testing real operator transcripts.",
        ],
        "notes_zh": [
            "这个套件使用仓库内置的中英 transcript fixture，并覆盖多种格式，不会下载外部媒体素材。",
            "每个用例都会生成脚本包、blueprint 和双语 review 产物。",
            "可以先用这些结果比较 Level 2 结构，再接入真实 transcript。",
        ],
    }

    report_json_path = output_dir / "level2_demo_suite_report.json"
    report_json_path.write_text(json.dumps(report, ensure_ascii=False, indent=2), encoding="utf-8")

    report_markdown_path = output_dir / "level2_demo_suite_report.md"
    report_markdown_path.write_text(render_suite_markdown(report), encoding="utf-8")

    report["report_json_path"] = str(report_json_path)
    report["report_markdown_path"] = str(report_markdown_path)
    return report


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Run a bilingual Level 2 demo suite")
    parser.add_argument("--output-dir", default="tmp/level2-demo-suite", help="Suite output directory")
    parser.add_argument("--duration", type=int, default=45, help="Target script duration in seconds")
    return parser.parse_args()


def main() -> int:
    args = parse_args()
    report = run_suite(REPO_ROOT / args.output_dir, duration=args.duration)
    print("✅ Level 2 demo suite complete")
    print("✅ Level 2 演示套件已完成")
    print(f"   Average score / 平均得分: {report['average_score']}")
    print(f"   JSON report / JSON 报告: {report['report_json_path']}")
    print(f"   Markdown report / Markdown 报告: {report['report_markdown_path']}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
