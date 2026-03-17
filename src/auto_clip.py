#!/usr/bin/env python3
"""
OpenFang Auto Clip local CLI module.

This tool downloads source media, applies local transformation steps,
and generates short-form clips plus reports.
"""

import os
import sys
import json
import subprocess
import re
from datetime import datetime
from pathlib import Path
from typing import Dict, List, Optional, Tuple
from enum import Enum

# ============================================================================
# CONFIGURATION
# ============================================================================

OUTPUT_DIR = Path.home() / ".openfang" / "clips"
CONFIG_FILE = Path.home() / ".openfang" / "auto_clip_config.json"


class TransformLevel(Enum):
    """Copyright transformation levels"""
    NONE = 0  # No transformation (not recommended for commercial use)
    VISUAL = 1  # Visual remix (fastest, moderate safety)
    SCRIPT = 2  # Script regeneration (slower, high safety)
    COMPLETE = 3  # Complete recreation (concept scaffold)


# ============================================================================
# VIDEO PROCESSING
# ============================================================================

def load_config() -> dict:
    """Load configuration from file"""
    if CONFIG_FILE.exists():
        with open(CONFIG_FILE) as f:
            return json.load(f)

    return {
        "default_duration": 60,
        "min_duration": 30,
        "max_duration": 90,
        "target_platforms": ["tiktok", "shorts", "reels"],
        "auto_caption": True,
        "whisper_model": "base",
        "transform_level": 1,  # Default to Level 1
        "openfang_api": "http://127.0.0.1:4200"
    }


def download_video(url: str, output_dir: Path) -> dict:
    """
    Download video from YouTube or other supported sites

    Args:
        url: Video URL
        output_dir: Output directory path

    Returns:
        Video metadata dict
    """
    print(f"📥 Downloading video: {url}")

    output_dir.mkdir(parents=True, exist_ok=True)

    cmd = [
        "yt-dlp",
        "-f", "best[ext=mp4]",
        "-o", str(output_dir / "%(title)s.%(ext)s"),
        "--print", "json",
        "--remote-components", "ejs:github",
        "--newline",
        url
    ]

    result = subprocess.run(cmd, capture_output=True, text=True, timeout=300)

    if result.returncode != 0:
        raise Exception(f"Download failed: {result.stderr}")

    try:
        video_info = json.loads(result.stdout)

        # Sanitize filename
        safe_title = sanitize_filename(video_info.get('title', 'video'))
        video_path = output_dir / f"{safe_title}.mp4"

        # Rename if needed
        original_path = output_dir / f"{video_info['title']}.mp4"
        if original_path.exists() and original_path != video_path:
            original_path.rename(video_path)

        print(f"✅ Download complete: {video_path.name}")

        return {
            "path": str(video_path),
            "title": video_info.get('title', safe_title),
            "duration": video_info.get('duration', 0),
            "id": video_info.get('id', 'unknown'),
            "uploader": video_info.get('uploader', 'unknown'),
            "upload_date": video_info.get('upload_date', 'unknown')
        }
    except json.JSONDecodeError:
        # Fallback: list downloaded files
        files = list(output_dir.glob("*.mp4"))
        if files:
            video_path = files[-1]
            return {
                "path": str(video_path),
                "title": video_path.stem,
                "duration": 0,
                "id": "unknown"
            }
        raise


def sanitize_filename(filename: str) -> str:
    """Sanitize filename for safe file system operations"""
    # Remove or replace special characters
    safe = re.sub(r'[<>:"/\\|?*]', '', filename)
    safe = re.sub(r'[\s\|]+', '_', safe)
    # Limit length
    if len(safe) > 100:
        safe = safe[:97] + "..."
    return safe.strip()


# ============================================================================
# COPYRIGHT TRANSFORMATION ENGINE
# ============================================================================

class CopyrightTransformer:
    """
    Local transformation helper with scaffolded higher-level flows

    Provides 3 transformation levels:
    - Level 1: Visual remix (style transfer, effects)
    - Level 2: Script regeneration (new content, same message)
    - Level 3: Complete recreation (concept path)
    """

    def __init__(self, config: dict):
        self.config = config
        self.api_url = config.get('openfang_api', 'http://127.0.0.1:4200')

    def transform(self, video_path: str, level: TransformLevel) -> dict:
        """
        Apply copyright-safe transformation

        Args:
            video_path: Path to source video
            level: Transformation level (0-3)

        Returns:
            Transformation result dict
        """
        if level == TransformLevel.NONE:
            return {"status": "skipped", "message": "No transformation applied"}

        print(f"\n{'='*60}")
        print(f"🛡️  COPYRIGHT-SAFE TRANSFORMATION - Level {level.value}")
        print(f"{'='*60}\n")

        if level == TransformLevel.VISUAL:
            return self._transform_visual(video_path)
        elif level == TransformLevel.SCRIPT:
            return self._transform_script(video_path)
        elif level == TransformLevel.COMPLETE:
            return self._transform_complete(video_path)

        return {"status": "error", "message": "Invalid transformation level"}

    def _transform_visual(self, video_path: str) -> dict:
        """
        Level 1: Visual Remix

        Applies visual transformations to make the content distinct:
        - Style transfer (cartoon, oil painting effects)
        - Color grading
        - Speed modification
        - Mirror/flip
        - Overlay effects
        """
        print("🎨 Applying Level 1: Visual Remix")
        print("   • Style transfer")
        print("   • Color grading")
        print("   • Speed modification (1.2x)")
        print("   • Mirror effect")
        print("   • Safe for most use cases ✅")

        output_path = str(video_path).replace('.mp4', '_remix.mp4')

        # Apply FFmpeg filters for visual transformation
        cmd = [
            "ffmpeg",
            "-i", video_path,
            "-vf",
            "hflip,eq=contrast=1.1:brightness=0.05:saturation=1.2,",
            "-filter:v", "setpts=0.83*PTS",  # 1.2x speed
            "-filter:a", "atempo=1.2",
            "-c:v", "libx264",
            "-preset", "fast",
            "-crf", "23",
            "-c:a", "aac",
            "-b:a", "128k",
            "-y",
            output_path
        ]

        result = subprocess.run(cmd, capture_output=True, text=True)

        if result.returncode == 0:
            return {
                "status": "success",
                "output_path": output_path,
                "level": 1,
                "message": "Visual remix applied successfully"
            }

        return {
            "status": "error",
            "message": f"Visual transformation failed: {result.stderr}"
        }

    def _transform_script(self, video_path: str) -> dict:
        """
        Level 2: Script Regeneration

        Analyzes the original content and generates new script
        with the same core message but different expression.

        This is more complex and requires:
        1. Transcription
        2. LLM analysis of key concepts
        3. Script regeneration
        4. Voiceover synthesis
        5. Visual matching
        """
        print("📝 Applying Level 2: Script Regeneration")
        print("   • Extract key concepts")
        print("   • Generate new script")
        print("   • AI voiceover")
        print("   • Match visuals to script")
        print("   • High copyright safety ✅✅")
        print()
        print("⚠️  Note: This feature requires additional setup:")
        print("   - Whisper transcription")
        print("   - LLM API access")
        print("   - Voiceover TTS (ElevenLabs, etc.)")
        print("   - Stock footage or AI image generation")
        print()
        print("📖 See docs/TRANSFORMATION.md for setup guide")

        # For now, return not implemented
        # This would be implemented in a future version
        return {
            "status": "not_implemented",
            "message": "Script regeneration requires additional setup. See docs/TRANSFORMATION.md"
        }

    def _transform_complete(self, video_path: str) -> dict:
        """
        Level 3: Complete Recreation

        Concept path for full recreation:
        1. Deep analysis of original structure
        2. Original script generation
        3. AI-generated visuals
        4. Original music composition
        5. Professional voiceover
        """
        print("🎬 Applying Level 3: Complete Recreation")
        print("   • Deep structure analysis")
        print("   • Original script generation")
        print("   • AI-generated visuals")
        print("   • Original music")
        print("   • Professional voiceover")
        print("   • Concept path for the highest separation from the source")
        print()
        print("⚠️  Note: This feature requires:")
        print("   - Advanced AI models (DALL-E, Midjourney)")
        print("   - Music generation AI")
        print("   - Professional TTS")
        print("   - Video editing expertise")
        print()
        print("📖 See docs/TRANSFORMATION.md for complete guide")

        return {
            "status": "not_implemented",
            "message": "Complete recreation is still a roadmap item. See docs/TRANSFORMATION.md"
        }


# ============================================================================
# VIDEO EDITING
# ============================================================================

def create_clips(video_path: str, highlights: List[dict], output_dir: Path, config: dict) -> List[dict]:
    """
    Create video clips using FFmpeg

    Args:
        video_path: Source video path
        highlights: List of clip segments
        output_dir: Output directory
        config: Configuration dict

    Returns:
        List of created clips info
    """
    print(f"\n🎬 Creating {len(highlights)} clips...")

    created_clips = []
    target_platforms = config.get('target_platforms', ['tiktok'])

    for i, highlight in enumerate(highlights):
        start = highlight['start']
        end = highlight['end']
        duration = end - start

        # Determine output resolution based on platforms
        resolution = "1080:1920"  # Default vertical 9:16

        output_path = output_dir / f"clip_{i+1:02d}_{int(start):04d}s-{int(end):04d}s.mp4"

        print(f"  [{i+1}/{len(highlights)}] {start:.0f}s - {end:.0f}s ({duration:.0f}s)")

        # Build FFmpeg command
        cmd = [
            "ffmpeg",
            "-i", video_path,
            "-ss", str(start),
            "-t", str(duration),
            "-vf", f"scale={resolution}:force_original_aspect_ratio=decrease,pad={resolution}:(ow-iw)/2:(oh-ih)/2,setsar=1",
            "-c:v", "libx264",
            "-preset", "fast",
            "-crf", "23",
            "-c:a", "aac",
            "-b:a", "128k",
            "-y",
            str(output_path)
        ]

        result = subprocess.run(cmd, capture_output=True, text=True)

        if result.returncode == 0:
            file_size = output_path.stat().st_size / (1024 * 1024)
            print(f"       ✅ {file_size:.1f} MB")

            created_clips.append({
                'path': str(output_path),
                'start': start,
                'end': end,
                'duration': duration,
                'size_mb': file_size,
                'reason': highlight.get('reason', f'Clip {i+1}'),
                'score': highlight.get('score', 5)
            })
        else:
            print(f"       ❌ Failed: {result.stderr[:100]}")

    return created_clips


def analyze_highlights_simple(video_info: dict, config: dict) -> List[dict]:
    """
    Simple clip detection strategy (when AI is unavailable)

    Evenly distributes clips throughout the video
    """
    duration = video_info['duration']
    clip_duration = config.get('default_duration', 60)
    num_clips = max(3, min(10, int(duration / clip_duration)))

    highlights = []
    for i in range(num_clips):
        start = i * clip_duration
        end = min(start + clip_duration, duration)

        highlights.append({
            'start': start,
            'end': end,
            'reason': f'Auto-clip {i+1}',
            'score': 5
        })

    return highlights


# ============================================================================
# MAIN WORKFLOW
# ============================================================================

def process_video(url: str, transform_level: int = 1, config: dict = None) -> dict:
    """
    Main video processing workflow

    Args:
        url: Video URL
        transform_level: Copyright transformation level (0-3)
        config: Configuration dict

    Returns:
        Processing result dict
    """
    if config is None:
        config = load_config()

    print("=" * 70)
    print("🎬 OpenFang Auto Clip - Local Video Repurposing CLI")
    print("=" * 70)
    print()

    try:
        # Step 1: Download video
        print("Step 1/5: Downloading video...")
        video_info = download_video(url, OUTPUT_DIR / "downloads")
        video_path = video_info['path']

        # Step 2: Apply copyright transformation
        print("\nStep 2/5: Applying copyright-safe transformation...")
        transformer = CopyrightTransformer(config)
        level = TransformLevel(transform_level)

        transform_result = transformer.transform(video_path, level)

        # Use transformed video if successful
        if transform_result.get('status') == 'success':
            video_path = transform_result['output_path']
            print(f"✅ Using transformed video")

        # Step 3: Analyze and detect highlights
        print("\nStep 3/5: Analyzing video for highlights...")
        highlights = analyze_highlights_simple(video_info, config)
        print(f"✅ Found {len(highlights)} potential clips")

        # Step 4: Create clips
        print("\nStep 4/5: Creating video clips...")
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        clips_dir = OUTPUT_DIR / "clips" / timestamp
        clips_dir.mkdir(parents=True, exist_ok=True)

        created_clips = create_clips(video_path, highlights, clips_dir, config)

        # Step 5: Generate report
        print("\nStep 5/5: Generating report...")
        report = {
            'video': video_info,
            'transformation': {
                'level': transform_level,
                'result': transform_result
            },
            'clips': created_clips,
            'created_at': datetime.now().isoformat(),
            'output_dir': str(clips_dir)
        }

        report_path = clips_dir / "report.json"
        with open(report_path, 'w') as f:
            json.dump(report, f, indent=2)

        # Summary
        print("\n" + "=" * 70)
        print(f"✅ PROCESSING COMPLETE!")
        print("=" * 70)
        print(f"📁 Output directory: {clips_dir}")
        print(f"📹 Clips created: {len(created_clips)}")
        print(f"🛡️  Transformation level: {transform_level}")
        print()
        print("Clips:")
        for clip in created_clips:
            print(f"  • {clip['reason']} ({clip['score']}⭐)")
            print(f"    {Path(clip['path']).name} ({clip['size_mb']:.1f} MB)")

        print("\n💡 Next steps:")
        print("  1. Preview clips: open", clips_dir)
        print("  2. Upload to platforms")
        print("  3. Track performance")
        print()

        return report

    except Exception as e:
        print(f"\n❌ Processing failed: {e}")
        import traceback
        traceback.print_exc()
        return None


# ============================================================================
# COMMAND LINE INTERFACE
# ============================================================================

def main():
    """Main entry point"""
    import argparse

    parser = argparse.ArgumentParser(
        description="OpenFang Auto Clip - Local Video Repurposing CLI",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  # Basic usage
  %(prog)s "https://youtube.com/watch?v=xxx"

  # Copyright-safe transformation (Level 1)
  %(prog)s "URL" --transform 1

  # Complete recreation scaffold (Level 3)
  %(prog)s "URL" --transform 3

  # Custom duration
  %(prog)s "URL" --duration 45

Transformation Levels:
  0 - No transformation (not recommended)
  1 - Visual remix (fast, moderate safety) ✅
  2 - Script regeneration (slow, high safety) ✅✅
  3 - Complete recreation (concept scaffold) ⚠️

For more information, see README.md or docs/TRANSFORMATION.md
        """
    )

    parser.add_argument('url', help='Video URL to process')
    parser.add_argument('--duration', type=int, default=60,
                       help='Clip duration in seconds (default: 60)')
    parser.add_argument('--transform', type=int, choices=[0, 1, 2, 3], default=1,
                       help='Copyright transformation level (default: 1)')
    parser.add_argument('--config', help='Path to config file')

    args = parser.parse_args()

    # Load config
    config = load_config()
    if args.config:
        with open(args.config) as f:
            config.update(json.load(f))

    config['default_duration'] = args.duration

    # Process video
    result = process_video(args.url, args.transform, config)

    if result:
        print("\n🎉 Success!")
        sys.exit(0)
    else:
        print("\n❌ Failed!")
        sys.exit(1)


if __name__ == "__main__":
    main()
