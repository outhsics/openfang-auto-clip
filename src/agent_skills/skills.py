"""
OpenFang Agent Skills

Concrete skill implementations for video automation tasks.
"""

import os
import sys
import json
import subprocess
from pathlib import Path
from typing import Dict, Any, Optional, List
from datetime import datetime

# Add parent directory to path for imports
sys.path.insert(0, str(Path(__file__).parent.parent.parent))

from .core import Skill, SkillContext, SkillResult, SkillStatus, register_skill


@register_skill
class VideoDownloadSkill(Skill):
    """Download video from URL"""

    name = "video_download"
    description = "Download video from various sources (YouTube, Bilibili, local files)"
    version = "1.0.0"
    author = "OpenFang"

    parameters = {
        "url": {
            "type": str,
            "description": "Video URL or local file path",
            "required": True
        },
        "output_dir": {
            "type": str,
            "description": "Output directory for downloaded video",
            "required": False
        },
        "quality": {
            "type": str,
            "description": "Video quality (best, good, worst)",
            "required": False
        }
    }

    def execute(self, context: SkillContext, **kwargs) -> SkillResult:
        """Download video from URL"""
        from src.video_sources import get_video_source

        url = kwargs.get("url")
        output_dir = kwargs.get("output_dir", str(context.workspace / "downloads"))
        quality = kwargs.get("quality", "best")

        try:
            # Get appropriate video source
            source = get_video_source(url)

            # Download
            output_path = source.download(
                output_dir=output_dir,
                quality=quality
            )

            return SkillResult(
                success=True,
                status=SkillStatus.COMPLETED,
                data={
                    "video_path": str(output_path),
                    "source": source.__class__.__name__,
                    "url": url
                }
            )

        except Exception as e:
            return SkillResult(
                success=False,
                status=SkillStatus.FAILED,
                error=str(e)
            )


@register_skill
class VideoTransformSkill(Skill):
    """Transform video with copyright protection"""

    name = "video_transform"
    description = "Apply Level 1 visual transformation for copyright protection"
    version = "1.0.0"
    author = "OpenFang"

    parameters = {
        "input_path": {
            "type": str,
            "description": "Path to input video",
            "required": True
        },
        "output_path": {
            "type": str,
            "description": "Path to output video",
            "required": False
        },
        "transform_level": {
            "type": int,
            "description": "Transform level (0-3)",
            "required": False
        },
        "preset": {
            "type": str,
            "description": "Transform preset name",
            "required": False
        }
    }

    def execute(self, context: SkillContext, **kwargs) -> SkillResult:
        """Transform video"""
        input_path = Path(kwargs.get("input_path"))
        output_path = kwargs.get("output_path")
        transform_level = kwargs.get("transform_level", 1)
        preset = kwargs.get("preset", "default")

        if not input_path.exists():
            return SkillResult(
                success=False,
                status=SkillStatus.FAILED,
                error=f"Input video not found: {input_path}"
            )

        try:
            from src.transform_effects import apply_preset

            # Generate output path if not provided
            if not output_path:
                timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
                output_path = context.workspace / "transformed" / f"transformed_{timestamp}.mp4"
                output_path.parent.mkdir(parents=True, exist_ok=True)
            else:
                output_path = Path(output_path)

            # Apply transform
            success = apply_preset(
                input_path=str(input_path),
                output_path=str(output_path),
                preset_name=preset
            )

            if success:
                return SkillResult(
                    success=True,
                    status=SkillStatus.COMPLETED,
                    data={
                        "output_path": str(output_path),
                        "transform_level": transform_level,
                        "preset": preset
                    }
                )
            else:
                return SkillResult(
                    success=False,
                    status=SkillStatus.FAILED,
                    error="Transform application failed"
                )

        except Exception as e:
            return SkillResult(
                success=False,
                status=SkillStatus.FAILED,
                error=str(e)
            )


@register_skill
class BatchProcessSkill(Skill):
    """Process multiple videos in batch"""

    name = "batch_process"
    description = "Process multiple videos in parallel"
    version = "1.0.0"
    author = "OpenFang"

    parameters = {
        "urls": {
            "type": list,
            "description": "List of video URLs or paths",
            "required": True
        },
        "transform_level": {
            "type": int,
            "description": "Transform level for all videos",
            "required": False
        },
        "parallel": {
            "type": int,
            "description": "Number of parallel workers",
            "required": False
        }
    }

    def execute(self, context: SkillContext, **kwargs) -> SkillResult:
        """Process batch of videos"""
        urls = kwargs.get("urls", [])
        transform_level = kwargs.get("transform_level", 1)
        parallel = kwargs.get("parallel", 1)

        try:
            from auto_clip import load_batch_file, process_batch

            # Create temporary batch file
            import tempfile
            with tempfile.NamedTemporaryFile(mode="w", suffix=".txt", delete=False) as f:
                for url in urls:
                    f.write(f"{url}\n")
                batch_file = f.name

            # Load and process
            tasks = load_batch_file(batch_file)
            for task in tasks:
                task["transform_level"] = transform_level

            config = context.get_config("auto_clip", {})
            result = process_batch(
                tasks=tasks,
                config=config,
                parallel=parallel
            )

            # Clean up temp file
            os.unlink(batch_file)

            return SkillResult(
                success=True,
                status=SkillStatus.COMPLETED,
                data={
                    "summary": result["summary"],
                    "results": result.get("results", [])
                }
            )

        except Exception as e:
            return SkillResult(
                success=False,
                status=SkillStatus.FAILED,
                error=str(e)
            )


@register_skill
class AIGCImageSkill(Skill):
    """Generate AI image"""

    name = "aigc_image"
    description = "Generate image using AI (Stable Diffusion, DALL-E, etc.)"
    version = "1.0.0"
    author = "OpenFang"

    parameters = {
        "prompt": {
            "type": str,
            "description": "Text prompt for image generation",
            "required": True
        },
        "provider": {
            "type": str,
            "description": "AI provider to use",
            "required": False
        },
        "style": {
            "type": str,
            "description": "Style preset",
            "required": False
        },
        "width": {
            "type": int,
            "description": "Image width",
            "required": False
        },
        "height": {
            "type": int,
            "description": "Image height",
            "required": False
        },
        "variations": {
            "type": int,
            "description": "Number of variations to generate",
            "required": False
        }
    }

    def execute(self, context: SkillContext, **kwargs) -> SkillResult:
        """Generate AI image"""
        from src.aigc import ImageGenerator, get_provider, ImageStyle

        prompt = kwargs.get("prompt")
        provider = kwargs.get("provider", "stable_diffusion")
        style = kwargs.get("style")
        width = kwargs.get("width", 1024)
        height = kwargs.get("height", 1024)
        variations = kwargs.get("variations", 1)

        try:
            ai_provider = get_provider(provider)
            generator = ImageGenerator(provider=ai_provider)

            # Convert style
            image_style = None
            if style:
                try:
                    image_style = ImageStyle(style)
                except ValueError:
                    pass

            if variations > 1:
                results = generator.generate_variations(
                    base_prompt=prompt,
                    num_variations=variations,
                    width=width,
                    height=height,
                    style=image_style
                )

                successful = [r for r in results if r.get("success")]
                return SkillResult(
                    success=len(successful) > 0,
                    status=SkillStatus.COMPLETED,
                    data={
                        "generated": len(successful),
                        "total": variations,
                        "paths": [r.get("save_path") for r in successful]
                    }
                )
            else:
                result = generator.generate(
                    prompt=prompt,
                    style=image_style,
                    width=width,
                    height=height
                )

                return SkillResult(
                    success=result.get("success", False),
                    status=SkillStatus.COMPLETED if result.get("success") else SkillStatus.FAILED,
                    data={
                        "path": result.get("save_path")
                    },
                    error=result.get("error")
                )

        except Exception as e:
            return SkillResult(
                success=False,
                status=SkillStatus.FAILED,
                error=str(e)
            )


@register_skill
class AIGCVideoSkill(Skill):
    """Generate AI video"""

    name = "aigc_video"
    description = "Generate video using AI"
    version = "1.0.0"
    author = "OpenFang"

    parameters = {
        "prompt": {
            "type": str,
            "description": "Text prompt for video generation",
            "required": True
        },
        "provider": {
            "type": str,
            "description": "AI provider to use",
            "required": False
        },
        "duration": {
            "type": float,
            "description": "Video duration in seconds",
            "required": False
        },
        "width": {
            "type": int,
            "description": "Video width",
            "required": False
        },
        "height": {
            "type": int,
            "description": "Video height",
            "required": False
        }
    }

    def execute(self, context: SkillContext, **kwargs) -> SkillResult:
        """Generate AI video"""
        from src.aigc import VideoGenerator, get_provider

        prompt = kwargs.get("prompt")
        provider = kwargs.get("provider", "stable_diffusion")
        duration = kwargs.get("duration", 4.0)
        width = kwargs.get("width", 1024)
        height = kwargs.get("height", 1024)

        try:
            ai_provider = get_provider(provider)
            generator = VideoGenerator(provider=ai_provider)

            result = generator.generate(
                prompt=prompt,
                duration=duration,
                width=width,
                height=height
            )

            return SkillResult(
                success=result.get("success", False),
                status=SkillStatus.COMPLETED if result.get("success") else SkillStatus.FAILED,
                data={
                    "path": result.get("save_path"),
                    "duration": duration
                },
                error=result.get("error")
            )

        except Exception as e:
            return SkillResult(
                success=False,
                status=SkillStatus.FAILED,
                error=str(e)
            )


@register_skill
class TranscriptGenerateSkill(Skill):
    """Generate transcript from video"""

    name = "transcript_generate"
    description = "Generate transcript using Whisper"
    version = "1.0.0"
    author = "OpenFang"

    parameters = {
        "video_path": {
            "type": str,
            "description": "Path to video file",
            "required": True
        },
        "model": {
            "type": str,
            "description": "Whisper model size",
            "required": False
        },
        "output_format": {
            "type": str,
            "description": "Output format (srt, vtt, txt, json)",
            "required": False
        }
    }

    def execute(self, context: SkillContext, **kwargs) -> SkillResult:
        """Generate transcript"""
        video_path = Path(kwargs.get("video_path"))
        model = kwargs.get("model", "base")
        output_format = kwargs.get("output_format", "srt")

        if not video_path.exists():
            return SkillResult(
                success=False,
                status=SkillStatus.FAILED,
                error=f"Video not found: {video_path}"
            )

        try:
            import whisper

            # Load model
            whisper_model = whisper.load_model(model)

            # Transcribe
            result = whisper_model.transcribe(str(video_path))

            # Save transcript
            output_dir = context.workspace / "transcripts"
            output_dir.mkdir(parents=True, exist_ok=True)

            output_path = output_dir / f"{video_path.stem}.{output_format}"

            if output_format == "srt":
                # Write SRT format
                with open(output_path, "w") as f:
                    for i, segment in enumerate(result["segments"]):
                        start_time = segment["start"]
                        end_time = segment["end"]
                        text = segment["text"]

                        # Convert to SRT time format
                        start_srt = self._seconds_to_srt(start_time)
                        end_srt = self._seconds_to_srt(end_time)

                        f.write(f"{i + 1}\n{start_srt} --> {end_srt}\n{text}\n\n")

            elif output_format == "txt":
                with open(output_path, "w") as f:
                    f.write(result["text"])

            elif output_format == "json":
                with open(output_path, "w") as f:
                    json.dump(result, f, indent=2)

            return SkillResult(
                success=True,
                status=SkillStatus.COMPLETED,
                data={
                    "transcript_path": str(output_path),
                    "language": result.get("language"),
                    "duration": result.get("segments", [{}])[-1].get("end", 0) if result.get("segments") else 0
                }
            )

        except Exception as e:
            return SkillResult(
                success=False,
                status=SkillStatus.FAILED,
                error=str(e)
            )

    def _seconds_to_srt(self, seconds: float) -> str:
        """Convert seconds to SRT time format"""
        hours = int(seconds // 3600)
        minutes = int((seconds % 3600) // 60)
        secs = int(seconds % 60)
        millis = int((seconds % 1) * 1000)
        return f"{hours:02d}:{minutes:02d}:{secs:02d},{millis:03d}"


@register_skill
class ClipExtractSkill(Skill):
    """Extract clips from video"""

    name = "clip_extract"
    description = "Extract multiple clips from a video"
    version = "1.0.0"
    author = "OpenFang"

    parameters = {
        "input_path": {
            "type": str,
            "description": "Path to input video",
            "required": True
        },
        "segments": {
            "type": list,
            "description": "List of (start, end) time segments in seconds",
            "required": True
        },
        "output_dir": {
            "type": str,
            "description": "Output directory for clips",
            "required": False
        }
    }

    def execute(self, context: SkillContext, **kwargs) -> SkillResult:
        """Extract clips from video"""
        input_path = Path(kwargs.get("input_path"))
        segments = kwargs.get("segments", [])
        output_dir = kwargs.get("output_dir", str(context.workspace / "clips"))

        if not input_path.exists():
            return SkillResult(
                success=False,
                status=SkillStatus.FAILED,
                error=f"Input video not found: {input_path}"
            )

        try:
            output_dir = Path(output_dir)
            output_dir.mkdir(parents=True, exist_ok=True)

            extracted_clips = []

            for i, (start, end) in enumerate(segments):
                output_path = output_dir / f"clip_{i+1}.mp4"

                # FFmpeg command to extract clip
                cmd = [
                    "ffmpeg",
                    "-i", str(input_path),
                    "-ss", str(start),
                    "-t", str(end - start),
                    "-c", "copy",
                    "-y",
                    str(output_path)
                ]

                result = subprocess.run(
                    cmd,
                    capture_output=True,
                    text=True,
                    timeout=300
                )

                if result.returncode == 0:
                    extracted_clips.append(str(output_path))
                else:
                    return SkillResult(
                        success=False,
                        status=SkillStatus.FAILED,
                        error=f"Failed to extract clip {i+1}: {result.stderr[:200]}"
                    )

            return SkillResult(
                success=True,
                status=SkillStatus.COMPLETED,
                data={
                    "clips": extracted_clips,
                    "count": len(extracted_clips)
                }
            )

        except Exception as e:
            return SkillResult(
                success=False,
                status=SkillStatus.FAILED,
                error=str(e)
            )


# Export all skills
__all__ = [
    "VideoDownloadSkill",
    "VideoTransformSkill",
    "BatchProcessSkill",
    "AIGCImageSkill",
    "AIGCVideoSkill",
    "TranscriptGenerateSkill",
    "ClipExtractSkill",
]
