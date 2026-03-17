#!/usr/bin/env python3
"""Generate a launch kit from a benchmark report."""

from __future__ import annotations

import argparse
import json
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parent.parent
DEFAULT_REPORT = REPO_ROOT / "examples" / "benchmark" / "sample_benchmark_report.json"


def load_report(report_path: Path) -> dict:
    """Load a benchmark report from disk."""
    with report_path.open() as handle:
        return json.load(handle)


def build_launch_markdown(report: dict, language: str = "en") -> str:
    """Build launch-ready markdown copy from the benchmark report."""
    benchmark = report["benchmark"]
    timings = report["timings"]
    artifacts = report["artifacts"]
    transform = report["transform_result"]

    if language == "zh":
        return "\n".join(
            [
                "# OpenFang Auto Clip 发布素材包",
                "",
                "## 一句话定位",
                "OpenFang Auto Clip 是一个本地优先的视频再利用流水线，强调可复现 benchmark、可验证的 Level 1 转换，以及更适合运营和发布流程消费的输出物。",
                "",
                "## 当前可验证信号",
                f"- Synthetic demo 时长：{benchmark['duration_seconds']}s",
                f"- 转换等级：{benchmark['transform_level']}",
                f"- 生成片段数：{artifacts['clip_count']}",
                f"- 总耗时：{timings['total_seconds']}s",
                f"- 转换状态：{transform['status']}",
                "",
                "## 可分享资产",
                f"- Storyboard：`{artifacts.get('storyboard_path')}`",
                f"- Preview：`{artifacts.get('preview_path')}`",
                "- Benchmark report：`benchmark_report.json`",
                "",
                "## 建议中文发布帖",
                "",
                "```text",
                "把 OpenFang Auto Clip 开源出来了，当前版本重点不是“全能 AI 剪辑”，而是一个更可信的本地视频再利用工作流：",
                "",
                "- 可复现 synthetic benchmark",
                "- FFmpeg-based Level 1 视觉转换",
                "- 本地 Web manager + 任务历史",
                "- 带 benchmark 证据的 release bundle",
                "",
                f"最新 benchmark：18 秒 synthetic media，生成 {artifacts['clip_count']} 个 clips，总耗时 {timings['total_seconds']}s。",
                "",
                "Repo: https://github.com/outhsics/openfang-auto-clip",
                "```",
                "",
                "## 建议发布检查清单",
                "- 带上 storyboard 图片",
                "- 附上 benchmark README 链接",
                "- 直接写出本次 benchmark 时长和 clip 数",
                "- 明确说明 Level 2 / Level 3 仍是 roadmap",
                "",
            ]
        )

    return "\n".join(
        [
            "# OpenFang Auto Clip Launch Kit",
            "",
            "## Short Pitch",
            "OpenFang Auto Clip is a local-first pipeline for turning long videos into platform-ready short clips with reproducible transformation and operator-friendly outputs.",
            "",
            "## Proof Points",
            f"- Synthetic demo duration: {benchmark['duration_seconds']}s",
            f"- Transform level: {benchmark['transform_level']}",
            f"- Clips generated: {artifacts['clip_count']}",
            f"- Total benchmark runtime: {timings['total_seconds']}s",
            f"- Transformation status: {transform['status']}",
            "",
            "## Shareable Assets",
            f"- Storyboard: `{artifacts.get('storyboard_path')}`",
            f"- Preview frame: `{artifacts.get('preview_path')}`",
            f"- Benchmark report: `benchmark_report.json`",
            "",
            "## Suggested X / LinkedIn Post",
            "",
            "```text",
            "Open-sourced a local-first video repurposing pipeline:",
            "",
            "- reproducible benchmark demo",
            "- FFmpeg-based Level 1 transform",
            "- local web manager + task history",
            "- automated release workflow",
            "",
            f"Latest benchmark: {artifacts['clip_count']} clips in {timings['total_seconds']}s using synthetic media.",
            "",
            "Repo: https://github.com/outhsics/openfang-auto-clip",
            "```",
            "",
            "## Suggested Release Checklist",
            "- Attach the storyboard image to the release",
            "- Link to the benchmark README",
            "- Mention the exact benchmark runtime",
            "- Keep claims aligned with the current Reality Check table",
            "",
        ]
    )


def write_launch_kit(markdown: str, output_dir: Path, language: str = "en") -> Path:
    """Write the launch kit markdown to disk."""
    output_dir.mkdir(parents=True, exist_ok=True)
    suffix = "" if language == "en" else f"_{language}"
    output_path = output_dir / f"launch_post{suffix}.md"
    output_path.write_text(markdown)
    return output_path


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Generate a launch kit from a benchmark report")
    parser.add_argument(
        "--report",
        default=str(DEFAULT_REPORT),
        help="Path to a benchmark report JSON file",
    )
    parser.add_argument(
        "--output-dir",
        default="dist/launch-kit",
        help="Directory for generated launch materials",
    )
    parser.add_argument(
        "--lang",
        choices=["en", "zh"],
        default="en",
        help="Language for the generated launch kit",
    )
    return parser.parse_args()


def main() -> int:
    args = parse_args()
    report = load_report(Path(args.report))
    markdown = build_launch_markdown(report, language=args.lang)
    output_path = write_launch_kit(markdown, REPO_ROOT / args.output_dir, language=args.lang)
    print("✅ Launch kit generated")
    print(f"   Report: {args.report}")
    print(f"   Output: {output_path}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
