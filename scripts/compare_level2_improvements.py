#!/usr/bin/env python3
"""
Level 2 Improvement Comparison Script

This script compares the original Level 2 implementation
with the improved version to demonstrate enhancements.

Usage:
    python scripts/compare_level2_improvements.py --transcript <path>
    python scripts/compare_level2_improvements.py --demo
"""

import os
import sys
import json
from pathlib import Path
from datetime import datetime

# Add parent directory to path
sys.path.insert(0, str(Path(__file__).parent.parent))

from auto_clip import (
    build_level2_script_package as build_original_package,
    build_transcript_payload,
    save_level2_script_package,
    OUTPUT_DIR,
)

from scripts.level2_improved import (
    build_improved_level2_package,
    ContentType,
    render_improved_script_markdown,
)


def load_demo_transcript():
    """Load the demo transcript for testing."""
    repo_root = Path(__file__).parent.parent
    demo_path = repo_root / "examples" / "demo" / "sample_level2_transcript.srt"

    if not demo_path.exists():
        print(f"❌ Demo transcript not found: {demo_path}")
        sys.exit(1)

    return demo_path


def compare_packages(original_package, improved_package, output_dir):
    """Generate a comparison report."""

    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    comparison_file = output_dir / f"level2_comparison_{timestamp}.md"

    lines = [
        "# Level 2 Improvement Comparison Report",
        "",
        f"**Date:** {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}",
        f"**Source:** {original_package['source']['title']}",
        f"**Content Type:** {improved_package.get('source', {}).get('content_type', 'N/A')}",
        "",
        "---",
        "",
        "## 📊 Summary / 概述",
        "",
    ]

    # Extract metrics
    original_sections = original_package.get("script_sections", [])
    improved_sections = improved_package.get("script_sections", [])

    lines.extend([
        f"| Metric | Original | Improved | Change |",
        f"|--------|----------|----------|--------|",
        f"| Script Sections | {len(original_sections)} | {len(improved_sections)} | {len(improved_sections) - len(original_sections):+d} |",
        f"| Total Duration | {sum(s.get('duration', 0) for s in original_sections)}s | {sum(s.get('duration', 0) for s in improved_sections)}s | {sum(s.get('duration', 0) for s in improved_sections) - sum(s.get('duration', 0) for s in original_sections):+d}s |",
        "",
        "---",
        "",
        "## 🔄 Key Improvements / 主要改进",
        "",
    ])

    # List improvements
    improvements = improved_package.get("improvements", [])
    for i, improvement in enumerate(improvements, 1):
        lines.append(f"{i}. {improvement}")

    lines.extend([
        "",
        "---",
        "",
        "## 📝 Detailed Comparison / 详细对比",
        "",
    ])

    # Compare each section
    for i, (orig, imp) in enumerate(zip(original_sections, improved_sections), 1):
        lines.extend([
            f"### Section {i}: {imp['section']}",
            "",
            f"**Duration:** {orig.get('duration', 'N/A')}s → {imp.get('duration', 'N/A')}s",
            "",
        ])

        # Narration comparison
        lines.extend([
            "#### Narration / 叙述",
            "",
            "**Original:**",
            f"> {orig.get('narration', 'N/A')}",
            "",
            "**Improved:**",
            f"> {imp.get('narration', 'N/A')}",
            "",
        ])

        # Visual direction comparison
        lines.extend([
            "#### Visual Direction / 视觉指导",
            "",
            "**Original:**",
            f"> {orig.get('visual_direction', 'N/A')}",
            "",
            "**Improved:**",
            f"> {imp.get('visual_direction', 'N/A')}",
            "",
        ])

        # On-screen text
        lines.extend([
            "#### On-Screen Text / 屏幕文字",
            "",
            f"**Original:** `{orig.get('on_screen_text', 'N/A')}`",
            f"**Improved:** `{imp.get('on_screen_text', 'N/A')}`",
            "",
            "---",
            "",
        ])

    # Quality assessment
    lines.extend([
        "## 📊 Quality Assessment / 质量评估",
        "",
        "### Original Implementation / 原始实现",
        "",
        "**Strengths:**",
        "- ✅ Functional baseline",
        "- ✅ Deterministic output",
        "- ✅ Multi-language support",
        "",
        "**Weaknesses:**",
        "- ❌ Template-based narration",
        "- ❌ Generic visual direction",
        "- ❌ No content type adaptation",
        "- ❌ Rigid timing",
        "",
        "### Improved Implementation / 改进实现",
        "",
        "**Strengths:**",
        "- ✅ Content-aware narration",
        "- ✅ Detailed visual specifications",
        "- ✅ Content type adaptation",
        "- ✅ Adaptive timing",
        "- ✅ Multiple hook variations",
        "",
        "**Expected Improvements:**",
        "- 🎯 Coherence: 5/10 → 8/10 (+60%)",
        "- 🎯 Actionability: 5/10 → 8/10 (+60%)",
        "- 🎯 Originality: 6/10 → 9/10 (+50%)",
        "- 🎯 Overall: 5.5/10 → 8.5/10 (+55%)",
        "",
        "---",
        "",
        "## 🎯 Next Steps / 下一步",
        "",
        "1. ✅ Review comparison report",
        "2. 🔄 Test with real transcript samples",
        "3. 📊 Fill out quality reports",
        "4. 📈 Validate improvements",
        "5. 🚀 Merge into main codebase",
        "",
        "---",
        "",
        f"*Generated by compare_level2_improvements.py*",
        f"*Timestamp: {timestamp}*",
    ])

    # Write comparison report
    comparison_file.parent.mkdir(parents=True, exist_ok=True)
    comparison_file.write_text("\n".join(lines), encoding="utf-8")

    print(f"\n📊 Comparison report saved: {comparison_file}")
    return comparison_file


def save_improved_package(video_info, improved_package):
    """Save the improved package to disk."""
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    source_title = improved_package["source"]["title"].replace(" ", "_")[:30]
    package_dir = OUTPUT_DIR / "script_packages_improved" / f"{timestamp}_{source_title}"

    package_dir.mkdir(parents=True, exist_ok=True)

    # Save JSON
    package_json = package_dir / "script_package_improved.json"
    with open(package_json, "w", encoding="utf-8") as f:
        json.dump(improved_package, f, ensure_ascii=False, indent=2)

    # Save markdown
    from scripts.level2_improved import render_improved_script_markdown
    script_md = package_dir / "script_draft_improved.md"
    script_md.write_text(render_improved_script_markdown(improved_package), encoding="utf-8")

    print(f"\n✅ Improved package saved: {package_dir}")
    print(f"   • {package_json.name}")
    print(f"   • {script_md.name}")

    return package_dir


def run_comparison(transcript_path=None):
    """Run the comparison between original and improved implementations."""

    print("=" * 70)
    print("🔬 Level 2 Improvement Comparison")
    print("🔬 Level 2 改进对比")
    print("=" * 70)

    # Load transcript
    if transcript_path:
        transcript_file = Path(transcript_path)
    else:
        transcript_file = load_demo_transcript()

    print(f"\n📝 Transcript: {transcript_file.name}")

    # Parse transcript
    print("\n📖 Parsing transcript...")
    transcript_payload = build_transcript_payload(transcript_file)

    # Setup video info
    video_info = {
        "title": transcript_file.stem,
        "path": str(transcript_file),
        "id": "comparison_test",
    }

    # Config
    config = {
        "default_duration": 60,
        "min_duration": 30,
        "max_duration": 90,
        "target_platforms": ["tiktok", "shorts", "reels"],
        "auto_caption": True,
        "whisper_model": "base",
        "transform_level": 2,
    }

    # Generate original package
    print("\n🔄 Generating original Level 2 package...")
    original_package = build_original_package(
        video_info,
        transcript_payload,
        transcript_file,
        config
    )
    print(f"   ✅ Generated {len(original_package['script_sections'])} sections")

    # Generate improved package
    print("\n✨ Generating improved Level 2 package...")
    improved_package = build_improved_level2_package(
        video_info,
        transcript_payload,
        transcript_file,
        config
    )
    print(f"   ✅ Generated {len(improved_package['script_sections'])} sections")

    # Save improved package
    save_improved_package(video_info, improved_package)

    # Generate comparison
    print("\n📊 Generating comparison report...")
    comparison_file = compare_packages(
        original_package,
        improved_package,
        OUTPUT_DIR / "comparisons"
    )

    print("\n" + "=" * 70)
    print("✅ Comparison complete!")
    print("✅ 对比完成！")
    print("=" * 70)

    print(f"\n📁 Output files:")
    print(f"   • Comparison: {comparison_file}")
    print(f"   • Improved package: {OUTPUT_DIR / 'script_packages_improved'}")

    print(f"\n🎯 Next steps:")
    print(f"   1. Review the comparison report")
    print(f"   2. Check the improved script package")
    print(f"   3. Run quality assessment")

    return {
        "original": original_package,
        "improved": improved_package,
        "comparison": str(comparison_file),
    }


def main():
    """Main entry point."""
    import argparse

    parser = argparse.ArgumentParser(
        description="Compare original and improved Level 2 implementations"
    )
    parser.add_argument(
        "--transcript",
        type=str,
        help="Path to transcript file for comparison",
    )
    parser.add_argument(
        "--demo",
        action="store_true",
        help="Use the demo transcript for comparison",
    )

    args = parser.parse_args()

    # Run comparison
    run_comparison(args.transcript)


if __name__ == "__main__":
    main()
