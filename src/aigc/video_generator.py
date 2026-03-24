"""
AI Video Generator for OpenFang Auto Clip.

Provides high-level interface for AI video generation.
"""

import os
import base64
import subprocess
from pathlib import Path
from typing import Dict, List, Optional, Any, Union
from datetime import datetime
from enum import Enum
import tempfile

from .providers import AIProvider, get_provider, load_provider_config


class VideoStyle(Enum):
    """Predefined video generation styles"""

    CINEMATIC = "cinematic"
    ANIME = "anime"
    REALISTIC = "realistic"
    ABSTRACT = "abstract"
    NATURE = "nature"
    SCI_FI = "sci_fi"
    VINTAGE = "vintage"
    SLOW_MOTION = "slow_motion"
    TIMELAPSE = "timelapse"
    LOOP = "loop"


class VideoGenerator:
    """AI Video Generator"""

    def __init__(
        self,
        provider: Optional[AIProvider] = None,
        output_dir: Optional[Path] = None
    ):
        """
        Initialize video generator

        Args:
            provider: AI provider to use (auto-detected if None)
            output_dir: Output directory for generated videos
        """
        if provider is None:
            config = load_provider_config()
            default_provider = config.get("default_provider", "stable_diffusion")
            provider_config = config.get("providers", {}).get(default_provider, {})
            provider = get_provider(
                default_provider,
                api_key=provider_config.get("api_key"),
                base_url=provider_config.get("base_url")
            )

        self.provider = provider
        self.output_dir = output_dir or Path.home() / ".openfang" / "aigc" / "videos"
        self.output_dir.mkdir(parents=True, exist_ok=True)
        self._generation_history: List[Dict] = []

    def generate(
        self,
        prompt: str,
        duration: float = 4.0,
        fps: int = 30,
        width: int = 1024,
        height: int = 1024,
        style: Optional[VideoStyle] = None,
        save_path: Optional[Path] = None,
        **kwargs
    ) -> Dict[str, Any]:
        """
        Generate video from prompt

        Args:
            prompt: Text description of desired video
            duration: Video duration in seconds
            fps: Frames per second
            width: Video width
            height: Video height
            style: Predefined style to apply
            save_path: Where to save the video
            **kwargs: Additional provider-specific parameters

        Returns:
            Dictionary with generation result
        """
        # Apply style if specified
        if style:
            prompt = self._apply_style(prompt, style)

        # Generate video
        result = self.provider.generate_video(
            prompt=prompt,
            duration=duration,
            fps=fps,
            width=width,
            height=height,
            **kwargs
        )

        # Save video if successful
        if result.get("success"):
            save_path = save_path or self._generate_save_path()
            self._save_video(result, save_path)
            result["save_path"] = str(save_path)

            # Record in history
            self._generation_history.append({
                "timestamp": datetime.now().isoformat(),
                "prompt": prompt,
                "duration": duration,
                "fps": fps,
                "width": width,
                "height": height,
                "style": style.value if style else None,
                "save_path": str(save_path),
                "provider": self.provider.provider_type.value,
                "success": True
            })

        return result

    def image_to_video(
        self,
        image_path: Path,
        motion_prompt: str,
        duration: float = 4.0,
        fps: int = 30,
        motion_strength: float = 0.5,
        **kwargs
    ) -> Dict[str, Any]:
        """
        Animate a static image to create video

        Args:
            image_path: Path to input image
            motion_prompt: Description of desired motion/animation
            duration: Video duration
            fps: Frames per second
            motion_strength: How much motion to apply (0.0-1.0)
            **kwargs: Additional parameters

        Returns:
            Generation result
        """
        # This requires img2video support (e.g., Stable Video Diffusion)
        prompt = f"Animate this image with {motion_prompt}. Motion strength: {motion_strength}"

        result = self.provider.generate_video(
            prompt=prompt,
            duration=duration,
            fps=fps,
            **kwargs
        )

        if result.get("success"):
            save_path = self._generate_save_path(prefix="animated_")
            self._save_video(result, save_path)
            result["save_path"] = str(save_path)

        return result

    def text_to_video(
        self,
        script: str,
        scene_descriptions: List[str],
        output_path: Optional[Path] = None,
        transition: str = "fade",
        **kwargs
    ) -> Dict[str, Any]:
        """
        Generate video from text script with multiple scenes

        Args:
            script: Full script text
            scene_descriptions: List of visual descriptions for each scene
            output_path: Final output video path
            transition: Transition between scenes (fade, cut, dissolve)
            **kwargs: Additional parameters

        Returns:
            Generation result with combined video
        """
        scene_videos = []

        # Generate each scene
        for i, scene_desc in enumerate(scene_descriptions):
            print(f"Generating scene {i+1}/{len(scene_descriptions)}...")

            result = self.generate(
                prompt=scene_desc,
                **kwargs
            )

            if result.get("success"):
                scene_videos.append(Path(result["save_path"]))
            else:
                return {
                    "success": False,
                    "error": f"Failed to generate scene {i+1}: {result.get('error')}"
                }

        # Combine scenes
        if not output_path:
            output_path = self._generate_save_path(prefix="combined_")

        combine_result = self._combine_videos(
            scene_videos,
            output_path,
            transition=transition
        )

        return {
            "success": combine_result["success"],
            "save_path": str(output_path) if combine_result["success"] else None,
            "scenes": scene_videos,
            "error": combine_result.get("error")
        }

    def generate_loop(
        self,
        prompt: str,
        duration: float = 4.0,
        **kwargs
    ) -> Dict[str, Any]:
        """
        Generate a seamlessly looping video

        Args:
            prompt: Description of desired video
            duration: Duration of loop
            **kwargs: Additional parameters

        Returns:
            Generation result
        """
        loop_prompt = f"{prompt}, seamlessly looping, smooth transition from end to start"

        result = self.generate(
            prompt=loop_prompt,
            duration=duration,
            style=VideoStyle.LOOP,
            **kwargs
        )

        return result

    def extend_video(
        self,
        input_video: Path,
        extension_prompt: str,
        additional_duration: float = 2.0,
        **kwargs
    ) -> Dict[str, Any]:
        """
        Extend an existing video

        Args:
            input_video: Path to input video
            extension_prompt: Description of how to extend
            additional_duration: How much to add
            **kwargs: Additional parameters

        Returns:
            Generation result
        """
        return {
            "success": False,
            "error": "Video extension requires provider-specific implementation",
            "note": "Use RunwayML Gen-2 or Pika Labs for video extension"
        }

    def _apply_style(self, prompt: str, style: VideoStyle) -> str:
        """Apply style to prompt"""
        style_suffixes = {
            VideoStyle.CINEMATIC: "cinematic, movie-quality, dramatic lighting, professional cinematography",
            VideoStyle.ANIME: "anime style, vibrant colors, smooth animation",
            VideoStyle.REALISTIC: "photorealistic, highly detailed, natural motion",
            VideoStyle.ABSTRACT: "abstract, artistic, creative interpretation",
            VideoStyle.NATURE: "nature documentary style, natural, organic",
            VideoStyle.SCI_FI: "sci-fi, futuristic, high-tech, digital effects",
            VideoStyle.VINTAGE: "vintage, film grain, nostalgic, classic",
            VideoStyle.SLOW_MOTION: "slow motion, smooth, detailed",
            VideoStyle.TIMELAPSE: "timelapse, accelerated, time passing",
            VideoStyle.LOOP: "seamlessly looping, repetitive, smooth cycle",
        }

        suffix = style_suffixes.get(style, "")
        return f"{prompt}, {suffix}" if suffix else prompt

    def _generate_save_path(self, prefix: str = "") -> Path:
        """Generate unique save path for video"""
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        filename = f"{prefix}generated_{timestamp}.mp4"
        return self.output_dir / filename

    def _save_video(self, result: Dict[str, Any], save_path: Path):
        """Save video from result to disk"""
        if "video_base64" in result:
            # Decode base64 and save
            video_data = base64.b64decode(result["video_base64"])
            with open(save_path, "wb") as f:
                f.write(video_data)

        elif "video_url" in result:
            # Download from URL
            import requests
            response = requests.get(result["video_url"], timeout=300)
            response.raise_for_status()
            with open(save_path, "wb") as f:
                f.write(response.content)

    def _combine_videos(
        self,
        video_paths: List[Path],
        output_path: Path,
        transition: str = "fade"
    ) -> Dict[str, Any]:
        """
        Combine multiple videos into one

        Args:
            video_paths: List of video files to combine
            output_path: Output file path
            transition: Transition type

        Returns:
            Result dictionary
        """
        try:
            # Create filter complex for concatenation
            inputs = []
            filter_complex = []

            for i, video_path in enumerate(video_paths):
                inputs.extend(["-i", str(video_path)])

            # Simple concatenation (same format videos)
            filter_complex = f"[0:v][0:a][1:v][1:a]concat=n={len(video_paths)}:v=1:a=1[outv][outa]"

            cmd = [
                "ffmpeg",
                *inputs,
                "-filter_complex", filter_complex,
                "-map", "[outv]",
                "-map", "[outa]",
                "-c:v", "libx264",
                "-preset", "fast",
                "-c:a", "aac",
                "-y",
                str(output_path)
            ]

            result = subprocess.run(
                cmd,
                capture_output=True,
                text=True,
                timeout=600
            )

            if result.returncode == 0:
                return {"success": True}
            else:
                return {
                    "success": False,
                    "error": result.stderr[:500]
                }

        except Exception as e:
            return {
                "success": False,
                "error": str(e)
            }

    def get_history(self, limit: int = 10) -> List[Dict]:
        """Get recent generation history"""
        return self._generation_history[-limit:]

    def clear_history(self):
        """Clear generation history"""
        self._generation_history.clear()


def generate_video(
    prompt: str,
    provider: str = "stable_diffusion",
    duration: float = 4.0,
    **kwargs
) -> Dict[str, Any]:
    """
    Convenience function to generate a video

    Args:
        prompt: Text description
        provider: AI provider to use
        duration: Video duration in seconds
        **kwargs: Additional parameters

    Returns:
        Generation result
    """
    # Create generator
    generator = VideoGenerator(provider=get_provider(provider))

    # Generate
    return generator.generate(prompt, duration=duration, **kwargs)


# Preset configurations for common video types
VIDEO_PRESETS = {
    "social_short": {
        "duration": 15.0,
        "fps": 30,
        "width": 1080,
        "height": 1920,  # Vertical 9:16
        "style": "cinematic"
    },
    "youtube_intro": {
        "duration": 5.0,
        "fps": 30,
        "width": 1920,
        "height": 1080,
        "style": "cinematic"
    },
    "background_loop": {
        "duration": 10.0,
        "fps": 30,
        "width": 1920,
        "height": 1080,
        "style": "loop"
    },
    "product_showcase": {
        "duration": 8.0,
        "fps": 30,
        "width": 1080,
        "height": 1080,
        "style": "realistic"
    },
}


def generate_preset_video(preset_name: str, prompt: str, **kwargs) -> Dict[str, Any]:
    """
    Generate video using preset configuration

    Args:
        preset_name: Name of preset
        prompt: Video description
        **kwargs: Additional customizations

    Returns:
        Generation result
    """
    if preset_name not in VIDEO_PRESETS:
        return {
            "success": False,
            "error": f"Unknown preset: {preset_name}",
            "available_presets": list(VIDEO_PRESETS.keys())
        }

    preset = VIDEO_PRESETS[preset_name].copy()
    preset.update(kwargs)
    preset["prompt"] = prompt

    # Convert style string to enum
    if "style" in preset:
        try:
            preset["style"] = VideoStyle(preset["style"])
        except ValueError:
            preset["style"] = None

    return generate_video(**preset)


if __name__ == "__main__":
    # Test video generation
    print("Testing AI Video Generator...")

    # Test with Stable Diffusion (if available)
    try:
        result = generate_video(
            prompt="A peaceful mountain landscape with clouds moving",
            provider="stable_diffusion",
            duration=4.0,
            fps=30
        )

        if result.get("success"):
            print(f"✅ Video generated: {result.get('save_path')}")
        else:
            print(f"❌ Generation failed: {result.get('error')}")

    except Exception as e:
        print(f"❌ Error: {e}")
        print("💡 Make sure Stable Diffusion Video or Deforum is available")
