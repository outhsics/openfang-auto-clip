#!/usr/bin/env python3
"""Generate a repository social preview asset from a benchmark report."""

from __future__ import annotations

import argparse
import json
from pathlib import Path
from xml.sax.saxutils import escape

REPO_ROOT = Path(__file__).resolve().parent.parent
DEFAULT_REPORT = REPO_ROOT / "examples" / "benchmark" / "sample_benchmark_report.json"


def load_report(report_path: Path) -> dict:
    """Load a benchmark report from disk."""
    with report_path.open() as handle:
        return json.load(handle)


def metric_rows(report: dict, language: str) -> list[tuple[str, str]]:
    """Build the metrics shown on the preview image."""
    benchmark = report["benchmark"]
    timings = report["timings"]
    artifacts = report["artifacts"]

    if language == "zh":
        return [
            ("演示时长", f"{benchmark['duration_seconds']}s synthetic"),
            ("转换级别", f"Level {benchmark['transform_level']}"),
            ("生成片段", str(artifacts["clip_count"])),
            ("总耗时", f"{timings['total_seconds']}s"),
        ]

    return [
        ("Demo duration", f"{benchmark['duration_seconds']}s synthetic"),
        ("Transform", f"Level {benchmark['transform_level']}"),
        ("Clips", str(artifacts["clip_count"])),
        ("Runtime", f"{timings['total_seconds']}s"),
    ]


def build_copy(language: str) -> dict[str, str | list[str]]:
    """Return localized copy blocks."""
    if language == "zh":
        return {
            "eyebrow": "OPENFANG AUTO CLIP",
            "title": "本地优先的视频切条与再分发流水线",
            "subtitle": "可复现 benchmark、storyboard 产物、launch kit 与 release automation，方便评估、传播和开源增长。",
            "proof_title": "当前可验证信号",
            "proof_points": [
                "CLI 与 Level 1 已可用",
                "benchmark 可本地重复运行",
                "storyboard 可直接作为发布素材",
                "tag release 自动化已接通",
            ],
            "footer": "Repo: github.com/outhsics/openfang-auto-clip",
        }

    return {
        "eyebrow": "OPENFANG AUTO CLIP",
        "title": "Local-first video repurposing pipeline",
        "subtitle": "Reproducible benchmark, storyboard output, launch-kit generation, and release automation for a repo people can evaluate and share.",
        "proof_title": "Current proof signals",
        "proof_points": [
            "Working CLI and Level 1 transform",
            "Reproducible local benchmark run",
            "Storyboard output for launch assets",
            "Tagged release automation in repo",
        ],
        "footer": "Repo: github.com/outhsics/openfang-auto-clip",
    }


def build_social_preview_svg(report: dict, language: str = "en") -> str:
    """Build a shareable SVG social preview asset."""
    copy = build_copy(language)
    rows = metric_rows(report, language)

    row_markup = []
    x_positions = [70, 355, 640, 925]
    if len(rows) != len(x_positions):
        raise ValueError("Expected metric rows to match preview layout slots")

    for (label, value), x in zip(rows, x_positions):
        row_markup.append(
            "\n".join(
                [
                    f'<g transform="translate({x}, 392)">',
                    '  <rect width="240" height="120" rx="22" fill="rgba(255,255,255,0.08)" stroke="rgba(255,255,255,0.16)"/>',
                    f'  <text x="24" y="42" fill="#9fb5c7" font-size="20" font-family="Arial, Helvetica, sans-serif">{escape(label)}</text>',
                    f'  <text x="24" y="82" fill="#f5f8fb" font-size="34" font-weight="700" font-family="Arial, Helvetica, sans-serif">{escape(value)}</text>',
                    "</g>",
                ]
            )
        )

    bullet_markup = []
    for index, point in enumerate(copy["proof_points"]):
        y = 264 + index * 34
        bullet_markup.append(
            f'<text x="760" y="{y}" fill="#d7e2ec" font-size="22" font-family="Arial, Helvetica, sans-serif">• {escape(point)}</text>'
        )

    return f"""<svg xmlns="http://www.w3.org/2000/svg" width="1280" height="640" viewBox="0 0 1280 640" role="img" aria-label="{escape(str(copy['title']))}">
  <defs>
    <linearGradient id="bg" x1="0%" y1="0%" x2="100%" y2="100%">
      <stop offset="0%" stop-color="#0d1b2a"/>
      <stop offset="55%" stop-color="#102b3f"/>
      <stop offset="100%" stop-color="#184e5e"/>
    </linearGradient>
    <linearGradient id="panel" x1="0%" y1="0%" x2="100%" y2="100%">
      <stop offset="0%" stop-color="rgba(255,255,255,0.14)"/>
      <stop offset="100%" stop-color="rgba(255,255,255,0.04)"/>
    </linearGradient>
  </defs>
  <rect width="1280" height="640" fill="url(#bg)"/>
  <circle cx="1090" cy="114" r="168" fill="rgba(255,255,255,0.07)"/>
  <circle cx="1180" cy="70" r="92" fill="rgba(255,255,255,0.08)"/>
  <circle cx="96" cy="544" r="180" fill="rgba(255,255,255,0.05)"/>
  <rect x="48" y="42" width="1184" height="556" rx="32" fill="url(#panel)" stroke="rgba(255,255,255,0.12)"/>

  <text x="70" y="96" fill="#7dd3c7" font-size="22" font-weight="700" letter-spacing="2" font-family="Arial, Helvetica, sans-serif">{escape(str(copy['eyebrow']))}</text>
  <text x="70" y="166" fill="#f5f8fb" font-size="56" font-weight="800" font-family="Arial, Helvetica, sans-serif">{escape(str(copy['title']))}</text>
  <text x="70" y="214" fill="#c7d4df" font-size="24" font-family="Arial, Helvetica, sans-serif">{escape(str(copy['subtitle']))}</text>

  <rect x="760" y="118" width="406" height="176" rx="24" fill="rgba(7, 19, 28, 0.34)" stroke="rgba(255,255,255,0.14)"/>
  <text x="790" y="160" fill="#f5f8fb" font-size="28" font-weight="700" font-family="Arial, Helvetica, sans-serif">{escape(str(copy['proof_title']))}</text>
  {''.join(bullet_markup)}

  {''.join(row_markup)}

  <rect x="70" y="554" width="1140" height="1" fill="rgba(255,255,255,0.12)"/>
  <text x="70" y="590" fill="#d0dae2" font-size="22" font-family="Arial, Helvetica, sans-serif">{escape(str(copy['footer']))}</text>
</svg>
"""


def write_social_preview(svg: str, output_dir: Path, language: str) -> Path:
    """Write the generated social preview asset to disk."""
    output_dir.mkdir(parents=True, exist_ok=True)
    suffix = "" if language == "en" else f"_{language}"
    output_path = output_dir / f"github_social_preview{suffix}.svg"
    output_path.write_text(svg)
    return output_path


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Generate a GitHub social preview asset")
    parser.add_argument(
        "--report",
        default=str(DEFAULT_REPORT),
        help="Path to a benchmark report JSON file",
    )
    parser.add_argument(
        "--output-dir",
        default="dist/social-preview",
        help="Directory for generated social preview assets",
    )
    parser.add_argument(
        "--lang",
        choices=["en", "zh"],
        default="en",
        help="Language for the generated asset",
    )
    return parser.parse_args()


def main() -> int:
    args = parse_args()
    report = load_report(Path(args.report))
    svg = build_social_preview_svg(report, language=args.lang)
    output_path = write_social_preview(svg, REPO_ROOT / args.output_dir, args.lang)
    print("✅ Social preview generated")
    print(f"   Report: {args.report}")
    print(f"   Output: {output_path}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
