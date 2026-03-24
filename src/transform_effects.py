"""
Transform effect presets for OpenFang Auto Clip.

Provides various visual transformation presets for different styles.
"""

from typing import Dict, List, Optional
from enum import Enum


class EffectPreset(Enum):
    """Available effect presets"""

    # Basic presets
    DEFAULT = "default"
    MILD = "mild"
    STRONG = "strong"

    # Style presets
    CINEMATIC = "cinematic"
    RETRO = "retro"
    CYBERPUNK = "cyberpunk"
    VINTAGE = "vintage"
    NOIR = "noir"

    # Social media presets
    TIKTOK = "tiktok"
    INSTAGRAM = "instagram"
    YOUTUBE = "youtube"

    # Mood presets
    DRAMATIC = "dramatic"
    DREAMY = "dreamy"
    INTENSE = "intense"


# Effect preset definitions
EFFECT_PRESETS: Dict[str, Dict] = {
    # ============================================================================
    # BASIC PRESETS
    # ============================================================================

    EffectPreset.DEFAULT.value: {
        "name": "Default",
        "description": "Balanced copyright protection with good visual quality",
        "video_filter": (
            "scale=1920:1080:flags=bicubic,"
            "crop=1920:1080:0:0,"
            "hflip,"
            "rotate=1.5*PI/180:fillcolor=black,"
            "eq=contrast=1.15:brightness=0.08:saturation=1.25:gamma=0.95,"
            "curves=all='0/0 0.25/0.2 0.5/0.55 0.75/0.85 1/1',"
            "vignette=angle=PI/4:dither=1,"
            "setpts=0.87*PTS"
        ),
        "audio_filter": "atempo=1.15,asetrate=44100*0.97",
        "speed_factor": 1.15,
        "protection_level": "high"
    },

    EffectPreset.MILD.value: {
        "name": "Mild",
        "description": "Subtle changes, maintains original look",
        "video_filter": (
            "scale=1920:1080:flags=bicubic,"
            "hflip,"
            "eq=contrast=1.08:brightness=0.05:saturation=1.1,"
            "setpts=0.95*PTS"
        ),
        "audio_filter": "atempo=1.05",
        "speed_factor": 1.05,
        "protection_level": "low"
    },

    EffectPreset.STRONG.value: {
        "name": "Strong",
        "description": "Maximum copyright protection",
        "video_filter": (
            "scale=1920:1080:flags=bicubic,"
            "crop=1920:1080:0:0,"
            "hflip,"
            "rotate=3*PI/180:fillcolor=black,"
            "eq=contrast=1.25:brightness=0.1:saturation=1.4:gamma=0.9,"
            "curves=all='0/0 0.2/0.1 0.4/0.4 0.6/0.7 0.8/0.9 1/1',"
            "vignette=angle=PI/3:dither=1,"
            "noise=alls=10:allf=t,"
            "setpts=0.80*PTS"
        ),
        "audio_filter": "atempo=1.25,asetrate=44100*0.95",
        "speed_factor": 1.25,
        "protection_level": "very_high"
    },

    # ============================================================================
    # STYLE PRESETS
    # ============================================================================

    EffectPreset.CINEMATIC.value: {
        "name": "Cinematic",
        "description": "Movie-like color grading",
        "video_filter": (
            "scale=1920:1080:flags=bicubic,"
            "hflip,"
            "rotate=1.5*PI/180:fillcolor=black,"
            "eq=contrast=1.2:brightness=-0.05:saturation=0.9:gamma=0.85,"
            "curves=all='0/0 0.2/0.15 0.4/0.35 0.6/0.6 0.8/0.85 1/1',"
            "vignette=angle=PI/5:dither=1,"
            "setpts=0.87*PTS"
        ),
        "audio_filter": "atempo=1.15,asetrate=44100*0.97",
        "speed_factor": 1.15,
        "protection_level": "high"
    },

    EffectPreset.RETRO.value: {
        "name": "Retro",
        "description": "90s VHS style",
        "video_filter": (
            "scale=1920:1080:flags=bicubic,"
            "hflip,"
            "eq=contrast=1.1:brightness=0.05:saturation=1.3:gamma=1.1,"
            "curves=all='0/0.1 0.2/0.25 0.4/0.5 0.6/0.7 0.8/0.9 1/1',"
            "vignette=angle=PI/3.5:dither=1,"
            "noise=alls=20:allf=t,"
            "setpts=0.87*PTS"
        ),
        "audio_filter": "atempo=1.15,aformat=sample_rates=44100:channel_layouts=stereo,asetrate=44100*0.97",
        "speed_factor": 1.15,
        "protection_level": "high"
    },

    EffectPreset.CYBERPUNK.value: {
        "name": "Cyberpunk",
        "description": "Neon, futuristic look",
        "video_filter": (
            "scale=1920:1080:flags=bicubic,"
            "hflip,"
            "rotate=2*PI/180:fillcolor=black,"
            "eq=contrast=1.3:brightness=0.05:saturation=1.8:gamma=0.8,"
            "curves=all='0/0 0.2/0.1 0.5/0.4 0.8/0.9 1/1',"
            "vignette=angle=PI/6:dither=1,"
            "setpts=0.87*PTS"
        ),
        "audio_filter": "atempo=1.15,asetrate=44100*0.97",
        "speed_factor": 1.15,
        "protection_level": "high"
    },

    EffectPreset.VINTAGE.value: {
        "name": "Vintage",
        "description": "Old film, sepia tone",
        "video_filter": (
            "scale=1920:1080:flags=bicubic,"
            "hflip,"
            "eq=contrast=1.15:brightness=0.1:saturation=0.6:gamma=1.05,"
            "curves=all='0/0.1 0.3/0.4 0.5/0.6 0.7/0.8 1/0.95',"
            "vignette=angle=PI/3:dither=1,"
            "noise=alls=15:allf=t,"
            "setpts=0.87*PTS"
        ),
        "audio_filter": "atempo=1.15,asetrate=44100*0.97",
        "speed_factor": 1.15,
        "protection_level": "high"
    },

    EffectPreset.NOIR.value: {
        "name": "Noir",
        "description": "Black and white, film noir style",
        "video_filter": (
            "scale=1920:1080:flags=bicubic,"
            "hflip,"
            "rotate=1.5*PI/180:fillcolor=black,"
            "eq=contrast=1.3:brightness=0.05:saturation=0:gamma=0.9,"
            "curves=all='0/0.1 0.3/0.3 0.5/0.5 0.7/0.7 1/0.9',"
            "vignette=angle=PI/4:dither=1,"
            "setpts=0.87*PTS"
        ),
        "audio_filter": "atempo=1.15,asetrate=44100*0.97",
        "speed_factor": 1.15,
        "protection_level": "high"
    },

    # ============================================================================
    # SOCIAL MEDIA PRESETS
    # ============================================================================

    EffectPreset.TIKTOK.value: {
        "name": "TikTok",
        "description": "Optimized for TikTok (fast-paced, vibrant)",
        "video_filter": (
            "scale=1080:1920:flags=bicubic,"
            "crop=1080:1920:0:0,"
            "hflip,"
            "eq=contrast=1.15:brightness=0.08:saturation=1.4:gamma=0.92,"
            "curves=all='0/0 0.25/0.2 0.5/0.55 0.75/0.85 1/1',"
            "vignette=angle=PI/5:dither=1,"
            "setpts=0.75*PTS"
        ),
        "audio_filter": "atempo=1.25,asetrate=44100*0.96",
        "speed_factor": 1.25,
        "protection_level": "high"
    },

    EffectPreset.INSTAGRAM.value: {
        "name": "Instagram",
        "description": "Clean, aesthetic for Reels",
        "video_filter": (
            "scale=1080:1920:flags=bicubic,"
            "crop=1080:1920:0:0,"
            "hflip,"
            "eq=contrast=1.12:brightness=0.06:saturation=1.2:gamma=0.94,"
            "curves=all='0/0 0.25/0.22 0.5/0.58 0.75/0.82 1/1',"
            "vignette=angle=PI/4.5:dither=1,"
            "setpts=0.87*PTS"
        ),
        "audio_filter": "atempo=1.15,asetrate=44100*0.97",
        "speed_factor": 1.15,
        "protection_level": "high"
    },

    EffectPreset.YOUTUBE.value: {
        "name": "YouTube",
        "description": "Balanced for YouTube Shorts",
        "video_filter": (
            "scale=1080:1920:flags=bicubic,"
            "crop=1080:1920:0:0,"
            "hflip,"
            "rotate=1.2*PI/180:fillcolor=black,"
            "eq=contrast=1.1:brightness=0.05:saturation=1.15:gamma=0.95,"
            "curves=all='0/0 0.25/0.2 0.5/0.55 0.75/0.85 1/1',"
            "vignette=angle=PI/4:dither=1,"
            "setpts=0.87*PTS"
        ),
        "audio_filter": "atempo=1.15,asetrate=44100*0.97",
        "speed_factor": 1.15,
        "protection_level": "high"
    },

    # ============================================================================
    # MOOD PRESETS
    # ============================================================================

    EffectPreset.DRAMATIC.value: {
        "name": "Dramatic",
        "description": "High contrast, intense mood",
        "video_filter": (
            "scale=1920:1080:flags=bicubic,"
            "hflip,"
            "rotate=2*PI/180:fillcolor=black,"
            "eq=contrast=1.35:brightness=-0.02:saturation=1.1:gamma=0.85,"
            "curves=all='0/0 0.15/0.05 0.35/0.25 0.6/0.55 0.85/0.9 1/1',"
            "vignette=angle=PI/3.5:dither=1,"
            "setpts=0.87*PTS"
        ),
        "audio_filter": "atempo=1.15,asetrate=44100*0.97",
        "speed_factor": 1.15,
        "protection_level": "high"
    },

    EffectPreset.DREAMY.value: {
        "name": "Dreamy",
        "description": "Soft, ethereal look",
        "video_filter": (
            "scale=1920:1080:flags=bicubic,"
            "hflip,"
            "eq=contrast=0.95:brightness=0.1:saturation=0.85:gamma=1.05,"
            "curves=all='0/0.05 0.25/0.25 0.5/0.55 0.75/0.8 1/0.95',"
            "vignette=angle=PI/6:dither=1,"
            "setpts=0.87*PTS"
        ),
        "audio_filter": "atempo=1.15,asetrate=44100*0.97",
        "speed_factor": 1.15,
        "protection_level": "medium"
    },

    EffectPreset.INTENSE.value: {
        "name": "Intense",
        "description": "Bold, attention-grabbing",
        "video_filter": (
            "scale=1920:1080:flags=bicubic,"
            "crop=1920:1080:0:0,"
            "hflip,"
            "rotate=2.5*PI/180:fillcolor=black,"
            "eq=contrast=1.4:brightness=0.08:saturation=1.6:gamma=0.82,"
            "curves=all='0/0 0.2/0.1 0.4/0.3 0.6/0.6 0.8/0.9 1/1',"
            "vignette=angle=PI/3.2:dither=1,"
            "setpts=0.80*PTS"
        ),
        "audio_filter": "atempo=1.25,asetrate=44100*0.95",
        "speed_factor": 1.25,
        "protection_level": "very_high"
    },
}


def get_preset(preset_name: str) -> Optional[Dict]:
    """
    Get effect preset by name

    Args:
        preset_name: Name of the preset

    Returns:
        Preset configuration dict or None if not found
    """
    return EFFECT_PRESETS.get(preset_name.lower())


def list_presets(category: Optional[str] = None) -> List[Dict]:
    """
    List available effect presets

    Args:
        category: Optional category filter (basic, style, social, mood)

    Returns:
        List of preset information dicts
    """
    presets = []

    for key, preset in EFFECT_PRESETS.items():
        if category:
            # Categorize presets
            if category == "basic" and key in ["default", "mild", "strong"]:
                presets.append({"name": key, **preset})
            elif category == "style" and key in ["cinematic", "retro", "cyberpunk", "vintage", "noir"]:
                presets.append({"name": key, **preset})
            elif category == "social" and key in ["tiktok", "instagram", "youtube"]:
                presets.append({"name": key, **preset})
            elif category == "mood" and key in ["dramatic", "dreamy", "intense"]:
                presets.append({"name": key, **preset})
        else:
            presets.append({"name": key, **preset})

    return presets


def apply_preset(
    input_path: str,
    output_path: str,
    preset_name: str = "default",
    resolution: str = "1920:1080"
) -> bool:
    """
    Apply effect preset to video

    Args:
        input_path: Input video path
        output_path: Output video path
        preset_name: Name of the preset to apply
        resolution: Output resolution (WIDTH:HEIGHT)

    Returns:
        True if successful, False otherwise
    """
    import subprocess

    preset = get_preset(preset_name)
    if not preset:
        print(f"❌ Preset '{preset_name}' not found")
        return False

    # Replace resolution in video filter
    video_filter = preset["video_filter"].replace("1920:1080", resolution)

    # Build FFmpeg command
    cmd = [
        "ffmpeg",
        "-i", input_path,
        "-vf", video_filter,
        "-af", preset["audio_filter"],
        "-c:v", "libx264",
        "-preset", "fast",
        "-crf", "22",
        "-pix_fmt", "yuv420p",
        "-movflags", "+faststart",
        "-c:a", "aac",
        "-b:a", "128k",
        "-y",
        output_path
    ]

    print(f"🎨 Applying preset: {preset['name']}")
    print(f"📝 Description: {preset['description']}")

    try:
        result = subprocess.run(cmd, capture_output=True, text=True, timeout=600)
        if result.returncode == 0:
            print(f"✅ Preset applied successfully")
            return True
        else:
            print(f"❌ Failed to apply preset: {result.stderr[:200]}")
            return False
    except Exception as e:
        print(f"❌ Error: {e}")
        return False


def create_custom_preset(
    name: str,
    video_filter: str,
    audio_filter: str,
    speed_factor: float = 1.0,
    protection_level: str = "medium"
) -> Dict:
    """
    Create a custom effect preset

    Args:
        name: Preset name
        video_filter: FFmpeg video filter string
        audio_filter: FFmpeg audio filter string
        speed_factor: Speed adjustment factor
        protection_level: Protection level (low, medium, high, very_high)

    Returns:
        Custom preset configuration
    """
    return {
        "name": name,
        "description": "Custom preset",
        "video_filter": video_filter,
        "audio_filter": audio_filter,
        "speed_factor": speed_factor,
        "protection_level": protection_level
    }


if __name__ == "__main__":
    # Example usage
    print("Available presets:")
    for category in ["basic", "style", "social", "mood"]:
        print(f"\n{category.upper()}:")
        presets = list_presets(category)
        for preset in presets:
            print(f"  • {preset['name']}: {preset['description']}")
