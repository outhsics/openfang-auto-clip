#!/usr/bin/env python3
"""
Complete Level 2 Testing and Validation Script

This script runs the complete improved Level 2 pipeline with validation:
1. Generate improved script package
2. Run comprehensive validation
3. Generate quality report
4. Save all artifacts

Usage:
    python scripts/test_level2_complete.py --transcript <path>
    python scripts/test_level2_complete.py --demo
"""

import os
import sys
import json
from pathlib import Path
from datetime import datetime

# Add parent directory to path
sys.path.insert(0, str(Path(__file__).parent.parent))

from auto_clip import (
    build_transcript_payload,
    OUTPUT_DIR,
)

from scripts.level2_improved import (
    build_improved_level2_package,
    render_improved_script_markdown,
)

from scripts.level2_validation import (
    generate_validation_report,
    save_validation_report,
)


def run_complete_test(transcript_path: Path):
    """
    Run complete Level 2 test with validation.

    Args:
        transcript_path: Path to transcript file
    """
    print("=" * 70)
    print("🔬 Complete Level 2 Testing with Validation")
    print("🔬 完整的 Level 2 测试和验证")
    print("=" * 70)

    # Load transcript
    print(f"\n📝 Transcript: {transcript_path.name}")
    transcript_payload = build_transcript_payload(transcript_path)
    original_text = transcript_payload["text"]

    print(f"   • Words: {len(original_text.split())}")
    print(f"   • Segments: {len(transcript_payload.get('segments', []))}")

    # Setup video info
    video_info = {
        "title": transcript_path.stem,
        "path": str(transcript_path),
        "id": "test_complete",
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

    # Generate improved package
    print("\n✨ Generating improved Level 2 package...")
    try:
        package = build_improved_level2_package(
            video_info,
            transcript_payload,
            transcript_path,
            config
        )
        print(f"   ✅ Generated {len(package['script_sections'])} sections")
    except Exception as e:
        print(f"   ❌ Error: {e}")
        return None

    # Save package
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    source_title = package["source"]["title"].replace(" ", "_")[:30]
    package_dir = OUTPUT_DIR / "script_packages_validated" / f"{timestamp}_{source_title}"
    package_dir.mkdir(parents=True, exist_ok=True)

    # Save package JSON
    package_json = package_dir / "script_package.json"
    with open(package_json, "w", encoding="utf-8") as f:
        json.dump(package, f, ensure_ascii=False, indent=2)

    # Save script markdown
    script_md = package_dir / "script_draft.md"
    script_md.write_text(render_improved_script_markdown(package), encoding="utf-8")

    print(f"   💾 Package saved: {package_dir}")

    # Run validation
    print("\n🔍 Running comprehensive validation...")
    try:
        validation_report = generate_validation_report(
            package,
            original_text,
            transcript_path
        )

        # Save validation report
        report_path = save_validation_report(package_dir, validation_report)

        print(f"   ✅ Validation complete")
        print(f"   💾 Report saved: {report_path}")

        # Display results
        display_validation_summary(validation_report)

    except Exception as e:
        print(f"   ❌ Validation error: {e}")
        import traceback
        traceback.print_exc()
        validation_report = None

    # Generate summary
    print("\n" + "=" * 70)
    print("✅ Complete Test Finished!")
    print("✅ 完整测试完成！")
    print("=" * 70)

    print(f"\n📁 Output files:")
    print(f"   • Package: {package_dir}")
    print(f"   • Script: {script_md}")
    if validation_report:
        print(f"   • Validation: {report_path}")

    return {
        "package_dir": str(package_dir),
        "package": package,
        "validation": validation_report,
    }


def display_validation_summary(report: dict):
    """Display validation summary."""
    print("\n📊 Validation Summary:")

    # Quality scores
    scores = report["quality_scores"]
    print(f"\n   Quality Scores:")
    print(f"   • Coherence: {scores['scores']['coherence']}/10")
    print(f"   • Actionability: {scores['scores']['actionability']}/10")
    print(f"   • Originality: {scores['scores']['originality']}/10")
    print(f"   • Value Retention: {scores['scores']['value_retention']}/10")
    print(f"   • Overall: {scores['overall']}/10 ({scores['grade']})")

    # Copyright
    copyright = report["copyright_assessment"]
    print(f"\n   Copyright Risk:")
    print(f"   • Level: {copyright['risk_level'].upper()}")
    print(f"   • Score: {copyright['total_risk_score']}")
    print(f"   • Safe: {'✅ Yes' if copyright['safe_for_commercial_use'] else '❌ No'}")

    # Overall
    overall = report["overall_assessment"]
    print(f"\n   Overall Assessment:")
    print(f"   • Status: {overall['status'].upper()}")
    print(f"   • Recommendation: {overall['recommendation']}")
    print(f"   • Confidence: {overall['confidence'].title()}")


def main():
    """Main entry point."""
    import argparse

    parser = argparse.ArgumentParser(
        description="Run complete Level 2 test with validation"
    )
    parser.add_argument(
        "--transcript",
        type=str,
        help="Path to transcript file",
    )
    parser.add_argument(
        "--demo",
        action="store_true",
        help="Use demo transcript",
    )

    args = parser.parse_args()

    # Determine transcript path
    if args.demo:
        repo_root = Path(__file__).parent.parent
        transcript_path = repo_root / "examples" / "demo" / "sample_level2_transcript.srt"
    elif args.transcript:
        transcript_path = Path(args.transcript)
    else:
        parser.print_help()
        sys.exit(1)

    if not transcript_path.exists():
        print(f"❌ Transcript not found: {transcript_path}")
        sys.exit(1)

    # Run test
    result = run_complete_test(transcript_path)

    if result:
        print(f"\n🎯 Next steps:")
        print(f"   1. Review the script package")
        print(f"   2. Check validation report")
        print(f"   3. Make improvements if needed")
        print(f"   4. Use for production if approved")


if __name__ == "__main__":
    main()
