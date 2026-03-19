#!/usr/bin/env python3
"""Export deterministic bilingual Level 2 sample artifacts into the repo."""

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
        "id": "en",
        "label_en": "English SRT sample",
        "label_zh": "英文 SRT 样例",
        "title": "Level 2 Sample EN SRT",
        "transcript_path": REPO_ROOT / "examples" / "demo" / "sample_level2_transcript.srt",
    },
    {
        "id": "zh",
        "label_en": "Chinese SRT sample",
        "label_zh": "中文 SRT 样例",
        "title": "Level 2 Sample ZH SRT",
        "transcript_path": REPO_ROOT / "examples" / "demo" / "sample_level2_transcript_zh.srt",
    },
    {
        "id": "en_json",
        "label_en": "English JSON sample",
        "label_zh": "英文 JSON 样例",
        "title": "Level 2 Sample EN JSON",
        "transcript_path": REPO_ROOT / "examples" / "demo" / "sample_level2_transcript.json",
    },
    {
        "id": "zh_vtt",
        "label_en": "Chinese VTT sample",
        "label_zh": "中文 VTT 样例",
        "title": "Level 2 Sample ZH VTT",
        "transcript_path": REPO_ROOT / "examples" / "demo" / "sample_level2_transcript_zh.vtt",
    },
]


def write_json(path: Path, payload: dict) -> None:
    path.write_text(json.dumps(payload, ensure_ascii=False, indent=2), encoding="utf-8")


def display_path(path: Path) -> str:
    """Prefer repo-relative paths when possible."""
    try:
        return str(path.relative_to(REPO_ROOT))
    except ValueError:
        return str(path)


def export_case(case: dict, output_dir: Path, duration: int) -> dict:
    """Export deterministic artifacts for one transcript fixture."""
    output_dir.mkdir(parents=True, exist_ok=True)
    config = auto_clip.load_config()
    config["default_duration"] = duration

    transcript_path = case["transcript_path"]
    transcript_relative = str(transcript_path.relative_to(REPO_ROOT))
    transcript_payload = auto_clip.build_transcript_payload(transcript_path)
    video_info = {
        "title": case["title"],
        "path": transcript_relative,
        "duration": duration,
        "id": f"level2-sample-{case['id']}",
        "uploader": "OpenFang Auto Clip",
    }
    package = auto_clip.build_level2_script_package(video_info, transcript_payload, Path(transcript_relative), config)
    package["source"]["video_path"] = transcript_relative
    package["source"]["transcript_path"] = transcript_relative

    review = auto_clip.build_level2_package_review(package)

    package_json_path = output_dir / "script_package.json"
    draft_path = output_dir / "script_draft.md"
    blueprint_path = output_dir / "production_blueprint.json"
    review_json_path = output_dir / "review_report.json"
    review_markdown_path = output_dir / "review_report.md"

    write_json(package_json_path, package)
    draft_path.write_text(auto_clip.render_level2_script_markdown(package), encoding="utf-8")
    write_json(blueprint_path, auto_clip.build_level2_blueprint(package))
    write_json(review_json_path, review)
    review_markdown_path.write_text(auto_clip.render_level2_review_markdown(review), encoding="utf-8")

    return {
        "id": case["id"],
        "label_en": case["label_en"],
        "label_zh": case["label_zh"],
        "language": package["language"],
        "transcript_format": transcript_path.suffix.lower().lstrip("."),
        "score": review["score"],
        "status_en": review["status_label_en"],
        "status_zh": review["status_label_zh"],
        "transcript_path": transcript_relative,
        "output_dir": display_path(output_dir),
        "files": [
            display_path(package_json_path),
            display_path(draft_path),
            display_path(blueprint_path),
            display_path(review_json_path),
            display_path(review_markdown_path),
        ],
    }


def render_index_markdown(report: dict) -> str:
    """Render an English index for committed sample artifacts."""
    lines = [
        "# Level 2 Sample Artifacts",
        "",
        "These committed artifacts are generated from the bundled transcript fixtures.",
        "They let visitors inspect real Level 2 outputs without running the CLI first.",
        "",
        f"- Generated at: {report['generated_at']}",
        "",
        "## Samples",
        "",
    ]

    for case in report["cases"]:
        lines.extend(
            [
                f"### {case['label_en']}",
                f"- Language: {case['language']}",
                f"- Transcript format: {case['transcript_format']}",
                f"- Review status: {case['status_en']}",
                f"- Review score: {case['score']}/100",
                f"- Transcript fixture: `{case['transcript_path']}`",
                f"- Script package: `{case['files'][0]}`",
                f"- Script draft: `{case['files'][1]}`",
                f"- Blueprint: `{case['files'][2]}`",
                f"- Review JSON: `{case['files'][3]}`",
                f"- Review Markdown: `{case['files'][4]}`",
                "",
            ]
        )

    lines.extend(
        [
            "## Notes",
            "",
            "- Refresh these artifacts with `python3 scripts/export_level2_demo_samples.py`.",
            "- Use the live CLI if you want timestamped outputs under `~/.openfang/clips/script_packages/`.",
            "",
        ]
    )
    return "\n".join(lines)


def render_index_markdown_zh(report: dict) -> str:
    """Render a Chinese index for committed sample artifacts."""
    lines = [
        "# Level 2 样例产物",
        "",
        "这些已提交到仓库的产物由内置 transcript fixture 生成。",
        "它们让访客不用先跑 CLI，也能直接查看真实的 Level 2 输出结果。",
        "",
        f"- 生成时间：{report['generated_at']}",
        "",
        "## 样例列表",
        "",
    ]

    for case in report["cases"]:
        lines.extend(
            [
                f"### {case['label_zh']}",
                f"- 语言：{case['language']}",
                f"- Transcript 格式：{case['transcript_format']}",
                f"- 评审状态：{case['status_zh']}",
                f"- 评审得分：{case['score']}/100",
                f"- Transcript fixture：`{case['transcript_path']}`",
                f"- 脚本包：`{case['files'][0]}`",
                f"- 脚本草稿：`{case['files'][1]}`",
                f"- Blueprint：`{case['files'][2]}`",
                f"- 评审 JSON：`{case['files'][3]}`",
                f"- 评审 Markdown：`{case['files'][4]}`",
                "",
            ]
        )

    lines.extend(
        [
            "## 说明",
            "",
            "- 如需刷新这些产物，运行 `python3 scripts/export_level2_demo_samples.py`。",
            "- 如果你想要带时间戳的实时产物，请直接使用 CLI 输出到 `~/.openfang/clips/script_packages/`。",
            "",
        ]
    )
    return "\n".join(lines)


def export_samples(output_dir: Path, duration: int = 45) -> dict:
    """Export all committed sample artifacts into the target directory."""
    output_dir.mkdir(parents=True, exist_ok=True)
    cases = []

    for case in CASES:
        case_dir = output_dir / case["id"]
        cases.append(export_case(case, case_dir, duration))

    report = {
        "generated_at": datetime.now().isoformat(timespec="seconds"),
        "output_dir": display_path(output_dir),
        "cases": cases,
    }

    write_json(output_dir / "index.json", report)
    (output_dir / "README.md").write_text(render_index_markdown(report), encoding="utf-8")
    (output_dir / "README_ZH.md").write_text(render_index_markdown_zh(report), encoding="utf-8")
    return report


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Export committed Level 2 sample artifacts")
    parser.add_argument("--output-dir", default="examples/demo/level2_samples", help="Output directory")
    parser.add_argument("--duration", type=int, default=45, help="Target script duration")
    return parser.parse_args()


def main() -> int:
    args = parse_args()
    report = export_samples(REPO_ROOT / args.output_dir, duration=args.duration)
    print("✅ Exported Level 2 sample artifacts")
    print("✅ 已导出 Level 2 样例产物")
    print(f"   Output / 输出目录: {report['output_dir']}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
