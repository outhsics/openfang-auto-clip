#!/usr/bin/env python3
"""
Level 2 Sample Testing Script

This script automates the testing of Level 2 script generation
across multiple transcript samples.

Usage:
    python scripts/test_level2_samples.py --sample examples/level2_samples/sample.srt
    python scripts/test_level2_samples.py --all
    python scripts/test_level2_samples.py --category educational
"""

import os
import sys
import json
import argparse
from pathlib import Path
from datetime import datetime
from typing import Dict, List, Optional

# Add parent directory to path for imports
sys.path.insert(0, str(Path(__file__).parent.parent))

from auto_clip import (
    build_level2_script_package,
    build_transcript_payload,
    save_level2_script_package,
    build_level2_package_review,
    save_level2_package_review,
    OUTPUT_DIR,
)

# Sample categories
SAMPLE_CATEGORIES = {
    "educational": ["edu_tutorial", "edu_science"],
    "entertainment": ["ent_comedy", "ent_storytelling"],
    "tutorial": ["tut_cooking", "tut_diy"],
    "english": ["lang_en_tech", "lang_en_edu"],
    "chinese": ["lang_zh_business", "lang_zh_lifestyle"],
}

# Test configuration
DEFAULT_CONFIG = {
    "default_duration": 60,
    "min_duration": 30,
    "max_duration": 90,
    "target_platforms": ["tiktok", "shorts", "reels"],
    "auto_caption": True,
    "whisper_model": "base",
    "transform_level": 2,
}


class Level2Tester:
    """Test Level 2 script generation on transcript samples."""

    def __init__(self, samples_dir: Path, output_dir: Path):
        self.samples_dir = samples_dir
        self.output_dir = output_dir
        self.results = []

    def find_samples(self, category: Optional[str] = None) -> List[Path]:
        """Find transcript samples to test."""
        samples = []

        if not self.samples_dir.exists():
            print(f"⚠️  Samples directory not found: {self.samples_dir}")
            return samples

        for ext in [".srt", ".vtt", ".txt", ".md", ".json"]:
            pattern = f"*{ext}"
            if category:
                pattern = f"{category}*{ext}"
            samples.extend(self.samples_dir.glob(pattern))

        return sorted(set(samples))

    def test_sample(self, transcript_path: Path) -> Dict:
        """Test a single transcript sample."""
        print(f"\n🧪 Testing: {transcript_path.name}")
        print("=" * 60)

        result = {
            "sample_name": transcript_path.stem,
            "transcript_path": str(transcript_path),
            "timestamp": datetime.now().isoformat(),
            "success": False,
            "error": None,
            "package_path": None,
            "review_path": None,
            "metrics": {},
        }

        try:
            # Load transcript
            print("📝 Loading transcript...")
            transcript_payload = build_transcript_payload(transcript_path)
            transcript_text = transcript_payload["text"]

            if not transcript_text:
                raise ValueError("Transcript is empty after parsing")

            # Basic metrics
            word_count = len(transcript_text.split())
            segment_count = len(transcript_payload.get("segments", []))
            print(f"   • Words: {word_count}")
            print(f"   • Segments: {segment_count}")

            # Build video info
            video_info = {
                "title": transcript_path.stem,
                "path": str(transcript_path),
                "id": f"test_{transcript_path.stem}",
            }

            # Generate Level 2 package
            print("🎬 Generating Level 2 package...")
            package = build_level2_script_package(
                video_info, transcript_payload, transcript_path, DEFAULT_CONFIG
            )

            # Save package
            print("💾 Saving package...")
            package_dir, saved_files = save_level2_script_package(video_info, package)

            # Generate review
            print("🔍 Generating review...")
            review = build_level2_package_review(package)
            review_files = save_level2_package_review(package_dir, review)

            # Extract metrics
            script_sections = package.get("script_sections", [])
            shot_plan = package.get("shot_plan", [])

            result["success"] = True
            result["package_path"] = str(package_dir)
            result["review_path"] = str(review_files[0]) if review_files else None
            result["metrics"] = {
                "word_count": word_count,
                "segment_count": segment_count,
                "script_section_count": len(script_sections),
                "shot_plan_count": len(shot_plan),
                "total_duration": sum(
                    int(s.get("duration", 0) or 0) for s in script_sections
                ),
                "has_time_anchors": sum(
                    1 for s in script_sections if s.get("source_anchor")
                ),
                "review_score": review.get("overall_score", "N/A"),
            }

            print(f"   ✅ Script sections: {len(script_sections)}")
            print(f"   ✅ Shot plan rows: {len(shot_plan)}")
            print(f"   ✅ Total duration: {result['metrics']['total_duration']}s")
            print(f"   ✅ Time anchors: {result['metrics']['has_time_anchors']}")
            print(f"   ✅ Package: {package_dir}")

        except Exception as e:
            result["error"] = str(e)
            print(f"   ❌ Error: {e}")

        return result

    def test_all(self, category: Optional[str] = None) -> List[Dict]:
        """Test all samples in a category."""
        samples = self.find_samples(category)

        if not samples:
            print(f"⚠️  No samples found")
            if category:
                print(f"   Category: {category}")
            return []

        print(f"\n🎯 Found {len(samples)} sample(s) to test")
        print("=" * 60)

        for sample in samples:
            result = self.test_sample(sample)
            self.results.append(result)

        return self.results

    def generate_report(self) -> Path:
        """Generate a test report."""
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        report_path = self.output_dir / f"level2_test_report_{timestamp}.md"

        # Calculate statistics
        total = len(self.results)
        successful = sum(1 for r in self.results if r["success"])
        failed = total - successful

        # Generate markdown report
        lines = [
            "# Level 2 Test Report",
            "",
            f"**Date:** {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}",
            f"**Total Samples:** {total}",
            f"**Successful:** {successful}",
            f"**Failed:** {failed}",
            f"**Success Rate:** {successful/total*100:.1f}%" if total > 0 else "",
            "",
            "---",
            "",
            "## 📊 Summary / 概述",
            "",
        ]

        if successful > 0:
            successful_results = [r for r in self.results if r["success"]]
            avg_sections = sum(r["metrics"].get("script_section_count", 0) for r in successful_results) / successful_results
            avg_duration = sum(r["metrics"].get("total_duration", 0) for r in successful_results) / successful_results
            avg_anchors = sum(r["metrics"].get("has_time_anchors", 0) for r in successful_results) / successful_results

            lines.extend([
                f"- **Average Script Sections:** {avg_sections:.1f}",
                f"- **Average Duration:** {avg_duration:.1f}s",
                f"- **Average Time Anchors:** {avg_anchors:.1f}",
                "",
            ])

        lines.extend([
            "## 📋 Detailed Results / 详细结果",
            "",
        ])

        for i, result in enumerate(self.results, 1):
            lines.extend([
                f"### {i}. {result['sample_name']}",
                "",
                f"**Status:** {'✅ Success' if result['success'] else '❌ Failed'}",
                "",
            ])

            if result["success"]:
                metrics = result["metrics"]
                lines.extend([
                    f"- **Script Sections:** {metrics.get('script_section_count', 'N/A')}",
                    f"- **Duration:** {metrics.get('total_duration', 'N/A')}s",
                    f"- **Time Anchors:** {metrics.get('has_time_anchors', 'N/A')}",
                    f"- **Package:** `{result['package_path']}`",
                    "",
                ])
            else:
                lines.extend([
                    f"**Error:** {result['error']}",
                    "",
                ])

        lines.extend([
            "---",
            "",
            "## 🎯 Next Steps / 下一步",
            "",
            "1. Review successful packages",
            "2. Fill out quality reports for each sample",
            "3. Identify common issues",
            "4. Implement improvements",
            "",
            "---",
            "",
            f"*Generated by test_level2_samples.py*",
        ])

        # Write report
        report_path.parent.mkdir(parents=True, exist_ok=True)
        report_path.write_text("\n".join(lines), encoding="utf-8")

        print(f"\n📊 Report saved: {report_path}")
        return report_path


def main():
    """Main entry point."""
    parser = argparse.ArgumentParser(
        description="Test Level 2 script generation on transcript samples"
    )
    parser.add_argument(
        "--sample",
        type=str,
        help="Test a specific transcript file",
    )
    parser.add_argument(
        "--all",
        action="store_true",
        help="Test all samples in the samples directory",
    )
    parser.add_argument(
        "--category",
        type=str,
        choices=list(SAMPLE_CATEGORIES.keys()) + ["english", "chinese"],
        help="Test samples from a specific category",
    )
    parser.add_argument(
        "--samples-dir",
        type=str,
        default="examples/level2_samples",
        help="Path to samples directory",
    )
    parser.add_argument(
        "--output-dir",
        type=str,
        default=str(OUTPUT_DIR / "test_reports"),
        help="Path to output directory",
    )

    args = parser.parse_args()

    # Resolve paths
    repo_root = Path(__file__).parent.parent
    samples_dir = repo_root / args.samples_dir
    output_dir = Path(args.output_dir)

    # Create tester
    tester = Level2Tester(samples_dir, output_dir)

    # Run tests
    if args.sample:
        # Test single sample
        sample_path = Path(args.sample)
        if not sample_path.is_absolute():
            sample_path = repo_root / args.sample

        if not sample_path.exists():
            print(f"❌ Sample not found: {sample_path}")
            sys.exit(1)

        result = tester.test_sample(sample_path)
        tester.results = [result]

    elif args.all or args.category:
        # Test all or category
        tester.test_all(args.category)

    else:
        parser.print_help()
        sys.exit(1)

    # Generate report
    if tester.results:
        tester.generate_report()
    else:
        print("⚠️  No results to report")


if __name__ == "__main__":
    main()
