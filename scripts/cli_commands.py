"""
Enhanced CLI Commands

Improved command-line interface with better UX.
"""

import sys
import argparse
from pathlib import Path
from typing import Optional, List, Dict
import logging

from .cli_utils import (
    print_success,
    print_error,
    print_warning,
    print_info,
    print_header,
    print_table,
    ProgressBar,
    confirm_action,
    format_duration,
    format_file_size
)

logger = logging.getLogger(__name__)


def cmd_init(args):
    """
    Initialize OpenFang configuration (setup wizard).

    Args:
        args: Parsed command-line arguments
    """
    print_header("🚀 OpenFang Auto Clip - Setup Wizard")

    config_file = Path.home() / ".openfang" / "auto_clip_config.json"
    config_dir = config_file.parent
    output_dir = Path.home() / ".openfang" / "clips"

    print_info(f"Configuration directory: {config_dir}")
    print_info(f"Output directory: {output_dir}")

    # Create directories
    print_info("\n📁 Creating directories...")
    try:
        config_dir.mkdir(parents=True, exist_ok=True)
        output_dir.mkdir(parents=True, exist_ok=True)
        print_success("Directories created")
    except Exception as e:
        print_error(f"Failed to create directories: {e}")
        return 1

    # Check dependencies
    print_info("\n🔍 Checking dependencies...")
    dependencies = {
        "ffmpeg": "Video processing",
        "yt-dlp": "Video downloading",
        "whisper": "Audio transcription"
    }

    missing = []
    for cmd, purpose in dependencies.items():
        import shutil
        if shutil.which(cmd):
            print_success(f"✓ {cmd} - {purpose}")
        else:
            print_warning(f"✗ {cmd} - Not found ({purpose})")
            missing.append(cmd)

    if missing:
        print_warning(f"\n⚠️  Missing dependencies: {', '.join(missing)}")
        print_info("Install them with:")
        if "ffmpeg" in missing:
            print_info("  - macOS: brew install ffmpeg")
            print_info("  - Ubuntu: sudo apt install ffmpeg")
        if "yt-dlp" in missing:
            print_info("  - pip install yt-dlp")
        if "whisper" in missing:
            print_info("  - pip install openai-whisper")

    # Create default config
    print_info("\n⚙️  Creating default configuration...")

    default_config = {
        "default_duration": 60,
        "min_duration": 30,
        "max_duration": 90,
        "target_platforms": ["tiktok", "shorts", "reels"],
        "auto_caption": True,
        "whisper_model": "base",
        "transform_level": 2,  # Default to Level 2
        "openfang_api": "http://127.0.0.1:4200"
    }

    import json
    with open(config_file, 'w') as f:
        json.dump(default_config, f, indent=2)

    print_success(f"Configuration saved to {config_file}")

    # Ask about demo
    print_info("\n📝 Would you like to run the demo now?")
    if confirm_action("Run demo?", default=True):
        print_info("You can run the demo later with: auto_clip demo")

    print_header("✅ Setup Complete!")
    print_info("OpenFang Auto Clip is ready to use!")
    print_info("\nNext steps:")
    print_info("  - Process a video: auto_clip process <video_url>")
    print_info("  - Run demo: auto_clip demo")
    print_info("  - Get help: auto_clip --help")

    return 0


def cmd_process(args):
    """
    Process a video/transcript with improved UX.

    Args:
        args: Parsed command-line arguments
    """
    print_header(f"🎬 Processing: {args.input}")

    # Load transcript if it's a file
    from auto_clip import build_transcript_payload, OUTPUT_DIR

    input_path = Path(args.input)
    if input_path.is_file():
        print_info(f"📄 Loading transcript from {input_path.name}...")

        try:
            transcript = build_transcript_payload(input_path)
            print_success(f"Loaded {len(transcript.get('text', ''))} characters")
        except Exception as e:
            print_error(f"Failed to load transcript: {e}")
            return 1

    # Process with Level 2
    if args.level >= 2:
        print_info("\n✍️  Generating Level 2 package...")

        try:
            from scripts.level2_improved import build_improved_level2_package

            video_info = {
                "title": input_path.stem,
                "path": str(input_path)
            }

            config = {
                "default_duration": args.duration,
                "content_type": "auto"
            }

            # Show progress
            if not args.quiet:
                print_info("   - Analyzing content...")
                print_info("   - Detecting content type...")
                print_info("   - Generating script...")

            package = build_improved_level2_package(
                video_info,
                transcript,
                input_path,
                config
            )

            # Save package
            output_file = OUTPUT_DIR / f"{input_path.stem}_level2.json"
            import json
            with open(output_file, 'w', encoding='utf-8') as f:
                json.dump(package, f, ensure_ascii=False, indent=2)

            print_success(f"Package saved to {output_file}")

            # Validate if requested
            if args.validate:
                print_info("\n🔍 Validating package...")

                from scripts.level2_validation import calculate_quality_scores

                scores = calculate_quality_scores(package, transcript.get('text', ''))

                print_table(
                    ["Dimension", "Score", "Rating"],
                    [
                        ["Coherence", f"{scores['scores']['coherence']:.1f}/10", "⭐" * int(scores['scores']['coherence'] / 2)],
                        ["Actionability", f"{scores['scores']['actionability']:.1f}/10", "⭐" * int(scores['scores']['actionability'] / 2)],
                        ["Originality", f"{scores['scores']['originality']:.1f}/10", "⭐" * int(scores['scores']['originality'] / 2)],
                        ["Value Retention", f"{scores['scores']['value_retention']:.1f}/10", "⭐" * int(scores['scores']['value_retention'] / 2)],
                        ["Overall", f"{scores['overall']:.1f}/10", f"Grade: {scores['grade']}"]
                    ],
                    title="Quality Scores"
                )

                if scores['overall'] >= 8.0:
                    print_success(f"Quality: {scores['overall']:.1f}/10 ({scores['grade']}) - Production ready!")
                elif scores['overall'] >= 6.0:
                    print_warning(f"Quality: {scores['overall']:.1f}/10 ({scores['grade']}) - Good, with improvements")
                else:
                    print_error(f"Quality: {scores['overall']:.1f}/10 ({scores['grade']}) - Needs improvement")

        except Exception as e:
            print_error(f"Level 2 generation failed: {e}")
            logger.error("Level 2 generation failed", exc_info=True)
            return 1

    print_success("\n✅ Processing complete!")
    return 0


def cmd_jobs(args):
    """
    List and manage jobs with improved display.

    Args:
        args: Parsed command-line arguments
    """
    print_header("📋 Jobs")

    try:
        from openfang_sdk import Client

        client = Client()

        # List jobs
        jobs = client.list_jobs(status=args.status, limit=args.limit)

        if not jobs:
            print_info("No jobs found")
            return 0

        # Format as table
        rows = []
        for job in jobs:
            rows.append([
                job['id'][:8] + "...",
                job['status'],
                job.get('level', '-'),
                f"{job.get('progress', 0):.1f}%",
                job.get('created_at', '-')[:19]
            ])

        print_table(
            ["Job ID", "Status", "Level", "Progress", "Created"],
            rows,
            title=f"Jobs (showing {len(jobs)} most recent)"
        )

        # Show details if requested
        if args.details and jobs:
            print_info("\n📊 Job Details:")
            for job in jobs[:3]:  # Show first 3
                print(f"\nJob: {job['id']}")
                print(f"  Status: {job['status']}")
                print(f"  Progress: {job.get('progress', 0):.1f}%")

                if job.get('result'):
                    print(f"  Output: {job['result'].get('output_path', 'N/A')}")
                if job.get('error'):
                    print(f"  Error: {job['error']}")

    except Exception as e:
        print_error(f"Failed to list jobs: {e}")
        logger.error("Failed to list jobs", exc_info=True)
        return 1

    return 0


def cmd_validate(args):
    """
    Validate package with improved display.

    Args:
        args: Parsed command-line arguments
    """
    print_header(f"🔍 Validating: {args.package}")

    try:
        from openfang_sdk import Client

        client = Client()

        # Load package for quick info
        import json
        from pathlib import Path

        package_path = Path(args.package)
        if not package_path.exists():
            print_error(f"Package not found: {args.package}")
            return 1

        with open(package_path, 'r') as f:
            package = json.load(f)

        print_info(f"📦 Package: {package_path.name}")
        print_info(f"   Size: {format_file_size(package_path.stat().st_size)}")
        print_info(f"   Sections: {len(package.get('script_sections', []))}")

        # Validate
        result = client.validate_package(str(package_path), args.transcript)

        # Display results
        print("\n" + "=" * 70)
        print("📊 Validation Results")
        print("=" * 70)

        # Overall score
        score_color = Color.GREEN if result['overall_score'] >= 8 else Color.YELLOW if result['overall_score'] >= 6 else Color.RED
        print(f"\n📈 Overall Score: {score_color.value}{result['overall_score']:.1f}/10 ({result['grade']}){Color.RESET.value}")

        # Production ready
        if result['production_ready']:
            print_success("Production Ready: ✅ Yes")
        else:
            print_warning("Production Ready: ⚠️  Needs improvement")

        # Quality scores
        print("\n📊 Quality Scores:")
        for dimension, score in result['scores'].items():
            stars = "⭐" * int(score / 2)
            print(f"   {dimension.capitalize():20} {score:5.1f}/10  {stars}")

        # Copyright risk
        copyright = result['copyright_risk']
        print(f"\n🛡️  Copyright Risk:")
        print(f"   Risk Level: {copyright['risk_level']}")
        print(f"   Semantic Similarity: {copyright['semantic_similarity']*100:.1f}%")
        print(f"   Word Overlap: {copyright['word_overlap']*100:.1f}%")

        # Issues
        if result['issues']:
            print(f"\n⚠️  Issues ({len(result['issues'])}):")
            for issue in result['issues']:
                print(f"   • {issue}")

        # Recommendations
        if result['recommendations']:
            print(f"\n💡 Recommendations ({len(result['recommendations'])}):")
            for rec in result['recommendations']:
                print(f"   • {rec}")

        print("\n" + "=" * 70)

        if result['production_ready']:
            print_success("✅ Package is production ready!")
        else:
            print_warning("⚠️  Package needs improvement before production use")

    except Exception as e:
        print_error(f"Validation failed: {e}")
        logger.error("Validation failed", exc_info=True)
        return 1

    return 0


def cmd_status(args):
    """
    Show system status with improved display.

    Args:
        args: Parsed command-line arguments
    """
    print_header("📊 OpenFang Auto Clip Status")

    # System checks
    print_info("\n🔧 System Status:")

    checks = [
        ("Python", sys.version.split()[0], True),
        ("Platform", sys.platform, True),
        ("Working Directory", Path.cwd(), True)
    ]

    for name, value, required in checks:
        print(f"   {name}: {value}")

    # Dependencies
    print_info("\n📦 Dependencies:")

    dependencies = [
        ("ffmpeg", "Video processing"),
        ("yt-dlp", "Video downloading"),
        ("whisper", "Audio transcription"),
        ("openfang", "OpenFang API")
    ]

    import shutil
    missing = []

    for cmd, purpose in dependencies:
        path = shutil.which(cmd)
        if path:
            print_success(f"   ✓ {cmd:10} - {purpose}")
        else:
            status = "warn" if cmd == "openfang" else "error"
            if status == "warn":
                print_warning(f"   ⚠ {cmd:10} - {purpose} (optional)")
            else:
                print_error(f"   ✗ {cmd:10} - {purpose} (missing)")
                if cmd != "openfang":
                    missing.append(cmd)

    # Configuration
    print_info("\n⚙️  Configuration:")

    from auto_clip import CONFIG_FILE
    if CONFIG_FILE.exists():
        print_success(f"   ✓ Config file exists: {CONFIG_FILE}")

        import json
        with open(CONFIG_FILE) as f:
            config = json.load(f)

        print(f"   Default Level: {config.get('transform_level', 'Not set')}")
        print(f"   Default Duration: {config.get('default_duration', 'Not set')}s")
    else:
        print_warning(f"   ✗ Config file not found (run 'auto_clip init')")

    # Output directory
    from auto_clip import OUTPUT_DIR
    print_info(f"\n📁 Output Directory:")
    print(f"   {OUTPUT_DIR}")

    if OUTPUT_DIR.exists():
        # Count files
        files = list(OUTPUT_DIR.glob("*"))
        print_success(f"   ✓ Directory exists ({len(files)} items)")
    else:
        print_warning(f"   ✗ Directory does not exist")

    # Summary
    print("\n" + "=" * 70)
    if not missing:
        print_success("✅ All dependencies installed!")
    else:
        print_error(f"❌ Missing dependencies: {', '.join(missing)}")
        print_info("\nInstall missing dependencies:")
        print_info("  - FFmpeg: https://ffmpeg.org/download.html")
        print_info("  - yt-dlp: pip install yt-dlp")
        print_info("  - whisper: pip install openai-whisper")

    return 0 if not missing else 1


def add_enhanced_commands(subparsers):
    """
    Add enhanced CLI commands to subparsers.

    Args:
        subparsers: ArgumentParser subparsers object
    """
    # Init command
    init_parser = subparsers.add_parser('init', help='Initialize configuration')
    init_parser.set_defaults(func=cmd_init)

    # Process command
    process_parser = subparsers.add_parser('process', help='Process video/transcript')
    process_parser.add_argument('input', help='Input file or video URL')
    process_parser.add_argument('-l', '--level', type=int, choices=[1, 2, 3], default=2,
                            help='Transformation level (default: 2)')
    process_parser.add_argument('-d', '--duration', type=int, default=60,
                            help='Target duration in seconds (default: 60)')
    process_parser.add_argument('--validate', action='store_true',
                            help='Validate output package')
    process_parser.add_argument('-q', '--quiet', action='store_true',
                            help='Quiet mode')
    process_parser.set_defaults(func=cmd_process)

    # Jobs command
    jobs_parser = subparsers.add_parser('jobs', help='List and manage jobs')
    jobs_parser.add_argument('-s', '--status', choices=['pending', 'processing', 'completed', 'failed'],
                         help='Filter by status')
    jobs_parser.add_argument('-l', '--limit', type=int, default=20,
                         help='Maximum jobs to show (default: 20)')
    jobs_parser.add_argument('-d', '--details', action='store_true',
                         help='Show detailed job information')
    jobs_parser.set_defaults(func=cmd_jobs)

    # Validate command
    validate_parser = subparsers.add_parser('validate', help='Validate Level 2 package')
    validate_parser.add_argument('package', help='Path to package JSON file')
    validate_parser.add_argument('-t', '--transcript', help='Original transcript for copyright check')
    validate_parser.set_defaults(func=cmd_validate)

    # Status command
    status_parser = subparsers.add_parser('status', help='Show system status')
    status_parser.set_defaults(func=cmd_status)
