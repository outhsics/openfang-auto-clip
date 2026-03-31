"""
视频预设模板

提供热门短视频格式的预设配置
"""

from typing import Dict, List, Optional, Any
from dataclasses import dataclass
from enum import Enum


class Platform(Enum):
    """目标平台"""
    TIKTOK = "tiktok"
    INSTAGRAM_REELS = "instagram_reels"
    YOUTUBE_SHORTS = "youtube_shorts"
    GENERIC = "generic"


@dataclass
class VideoPreset:
    """视频预设"""
    name: str
    description: str
    platform: Platform

    # 视频参数
    aspect_ratio: str  # 9:16, 1:1, 16:9
    resolution: str  # 1080x1920, 1080x1080, etc.
    fps: int  # 30, 60
    duration_range: tuple  # (min_seconds, max_seconds)

    # 处理参数
    transform_level: int  # 0-3
    add_captions: bool
    add_music: bool
    auto_crop: bool

    # FFmpeg 参数
    video_codec: str = "libx264"
    audio_codec: str = "aac"
    crf: int = 23  # 质量控制
    preset: str = "medium"  # 编码速度

    # 其他选项
    extra_params: Optional[Dict[str, Any]] = None


# 预设库
PRESETS: Dict[str, VideoPreset] = {
    # TikTok 预设
    "tiktok_viral": VideoPreset(
        name="TikTok 热门",
        description="适合 TikTok 的热门短视频格式",
        platform=Platform.TIKTOK,
        aspect_ratio="9:16",
        resolution="1080x1920",
        fps=30,
        duration_range=(15, 60),
        transform_level=1,
        add_captions=True,
        add_music=True,
        auto_crop=True,
        video_codec="libx264",
        audio_codec="aac",
        crf=23,
        preset="medium",
        extra_params={
            "filters": [
                "scale=1080:1920:force_original_aspect_ratio=decrease",
                "crop=1080:1920",
                "fps=30"
            ]
        }
    ),

    "tiktok_fast": VideoPreset(
        name="TikTok 快节奏",
        description="快节奏 TikTok 短视频",
        platform=Platform.TIKTOK,
        aspect_ratio="9:16",
        resolution="1080x1920",
        fps=60,
        duration_range=(7, 15),
        transform_level=1,
        add_captions=True,
        add_music=False,
        auto_crop=True,
        video_codec="libx264",
        audio_codec="aac",
        crf=20,
        preset="fast",
        extra_params={
            "filters": [
                "scale=1080:1920:force_original_aspect_ratio=decrease",
                "crop=1080:1920",
                "fps=60",
                "setpts=0.75*PTS"  # 加速 25%
            ]
        }
    ),

    # Instagram Reels 预设
    "instagram_reel": VideoPreset(
        name="Instagram Reels",
        description="Instagram Reels 标准格式",
        platform=Platform.INSTAGRAM_REELS,
        aspect_ratio="9:16",
        resolution="1080x1920",
        fps=30,
        duration_range=(15, 90),
        transform_level=1,
        add_captions=True,
        add_music=True,
        auto_crop=True,
        video_codec="libx264",
        audio_codec="aac",
        crf=23,
        preset="medium",
        extra_params={
            "filters": [
                "scale=1080:1920:force_original_aspect_ratio=decrease",
                "crop=1080:1920"
            ]
        }
    ),

    # YouTube Shorts 预设
    "youtube_short": VideoPreset(
        name="YouTube Shorts",
        description="YouTube Shorts 标准格式",
        platform=Platform.YOUTUBE_SHORTS,
        aspect_ratio="9:16",
        resolution="1080x1920",
        fps=30,
        duration_range=(15, 60),
        transform_level=1,
        add_captions=True,
        add_music=False,
        auto_crop=True,
        video_codec="libx264",
        audio_codec="aac",
        crf=23,
        preset="medium",
        extra_params={
            "filters": [
                "scale=1080:1920:force_original_aspect_ratio=decrease",
                "crop=1080:1920"
            ]
        }
    ),

    # 通用预设
    "square": VideoPreset(
        name="方形视频",
        description="1:1 方形视频，适合多平台",
        platform=Platform.GENERIC,
        aspect_ratio="1:1",
        resolution="1080x1080",
        fps=30,
        duration_range=(30, 60),
        transform_level=0,
        add_captions=True,
        add_music=False,
        auto_crop=True,
        video_codec="libx264",
        audio_codec="aac",
        crf=23,
        preset="medium",
        extra_params={
            "filters": [
                "scale=1080:1080:force_original_aspect_ratio=decrease",
                "crop=1080:1080"
            ]
        }
    ),

    "landscape": VideoPreset(
        name="横屏视频",
        description="16:9 横屏视频",
        platform=Platform.GENERIC,
        aspect_ratio="16:9",
        resolution="1920x1080",
        fps=30,
        duration_range=(30, 120),
        transform_level=0,
        add_captions=True,
        add_music=False,
        auto_crop=False,
        video_codec="libx264",
        audio_codec="aac",
        crf=23,
        preset="medium",
        extra_params={
            "filters": [
                "scale=1920:1080"
            ]
        }
    ),

    # 特殊效果预设
    "cinematic": VideoPreset(
        name="电影风格",
        description="电影感处理",
        platform=Platform.GENERIC,
        aspect_ratio="16:9",
        resolution="1920x1080",
        fps=24,
        duration_range=(30, 120),
        transform_level=0,
        add_captions=False,
        add_music=False,
        auto_crop=False,
        video_codec="libx264",
        audio_codec="aac",
        crf=18,
        preset="slow",
        extra_params={
            "filters": [
                "scale=1920:1080",
                "eq=contrast=1.1:brightness=0.05:saturation=1.1"
            ]
        }
    ),

    "vintage": VideoPreset(
        name="复古风格",
        description="复古滤镜效果",
        platform=Platform.GENERIC,
        aspect_ratio="9:16",
        resolution="1080x1920",
        fps=24,
        duration_range=(15, 60),
        transform_level=1,
        add_captions=True,
        add_music=False,
        auto_crop=True,
        video_codec="libx264",
        audio_codec="aac",
        crf=23,
        preset="medium",
        extra_params={
            "filters": [
                "scale=1080:1920:force_original_aspect_ratio=decrease",
                "crop=1080:1920",
                "eq=contrast=1.2:saturation=0.8",
                "curves=all='0/0 0.2/0.1 0.5/0.6 1/1'"
            ]
        }
    )
}


def get_preset(name: str) -> Optional[VideoPreset]:
    """获取预设"""
    return PRESETS.get(name)


def list_presets(platform: Optional[Platform] = None) -> List[VideoPreset]:
    """列出预设"""
    presets = list(PRESETS.values())

    if platform:
        presets = [p for p in presets if p.platform == platform]

    return sorted(presets, key=lambda p: p.name)


def apply_preset(
    preset: VideoPreset,
    input_path: str,
    output_path: str
) -> bool:
    """应用预设到视频

    注意：这需要使用 FFmpeg
    """
    import subprocess
    import logging

    logger = logging.getLogger(__name__)

    # 构建 FFmpeg 命令
    cmd = ["ffmpeg", "-i", input_path]

    # 添加视频过滤器
    if preset.extra_params and "filters" in preset.extra_params:
        filter_complex = ",".join(preset.extra_params["filters"])
        cmd.extend(["-vf", filter_complex])

    # 添加编码参数
    cmd.extend([
        "-c:v", preset.video_codec,
        "-c:a", preset.audio_codec,
        "-crf", str(preset.crf),
        "-preset", preset.preset,
        "-r", str(preset.fps)
    ])

    # 输出文件
    cmd.append(output_path)

    try:
        logger.info(f"应用预设: {preset.name}")
        result = subprocess.run(cmd, capture_output=True, text=True)

        if result.returncode == 0:
            logger.info(f"预设应用成功: {output_path}")
            return True
        else:
            logger.error(f"FFmpeg 错误: {result.stderr}")
            return False

    except Exception as e:
        logger.error(f"应用预设失败: {e}")
        return False


def create_custom_preset(
    name: str,
    platform: Platform,
    aspect_ratio: str = "9:16",
    resolution: str = "1080x1920",
    **kwargs
) -> VideoPreset:
    """创建自定义预设"""
    return VideoPreset(
        name=name,
        description=f"Custom preset: {name}",
        platform=platform,
        aspect_ratio=aspect_ratio,
        resolution=resolution,
        **kwargs
    )


def get_preset_for_platform(platform: str) -> Optional[VideoPreset]:
    """根据平台获取推荐预设"""
    platform_map = {
        "tiktok": "tiktok_viral",
        "instagram": "instagram_reel",
        "youtube": "youtube_short",
        "shorts": "youtube_short",
        "reels": "instagram_reel"
    }

    preset_name = platform_map.get(platform.lower())
    if preset_name:
        return get_preset(preset_name)

    return None
