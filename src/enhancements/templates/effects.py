"""
视频效果库

提供常用的视频处理效果
"""

from typing import Dict, List, Optional, Any
from dataclasses import dataclass


@dataclass
class VideoEffect:
    """视频效果"""
    name: str
    description: str
    category: str  # color, speed, transform, artistic
    ffmpeg_filter: str
    parameters: Optional[Dict[str, Any]] = None


# 效果库
EFFECTS: Dict[str, VideoEffect] = {
    # 颜色效果
    "brightness_up": VideoEffect(
        name="增加亮度",
        description="提高视频亮度",
        category="color",
        ffmpeg_filter="eq=brightness=0.1",
        parameters={"amount": 0.1}
    ),

    "brightness_down": VideoEffect(
        name="降低亮度",
        description="降低视频亮度",
        category="color",
        ffmpeg_filter="eq=brightness=-0.1",
        parameters={"amount": -0.1}
    ),

    "contrast_up": VideoEffect(
        name="增加对比度",
        description="提高视频对比度",
        category="color",
        ffmpeg_filter="eq=contrast=1.2",
        parameters={"amount": 1.2}
    ),

    "saturation_up": VideoEffect(
        name="增加饱和度",
        description="使颜色更鲜艳",
        category="color",
        ffmpeg_filter="eq=saturation=1.3",
        parameters={"amount": 1.3}
    ),

    "saturation_down": VideoEffect(
        name="降低饱和度",
        description="使颜色更柔和",
        category="color",
        ffmpeg_filter="eq=saturation=0.7",
        parameters={"amount": 0.7}
    ),

    "vintage": VideoEffect(
        name="复古效果",
        description="添加复古滤镜",
        category="artistic",
        ffmpeg_filter="curves=all='0/0 0.2/0.1 0.5/0.6 1/1':eq=saturation=0.8"
    ),

    "sepia": VideoEffect(
        name="棕褐色",
        description="添加棕褐色调",
        category="artistic",
        ffmpeg_filter="colorchannelmixer=.393:.769:.189:0:.349:.686:.168:0:.272:.534:.131"
    ),

    "grayscale": VideoEffect(
        name="黑白",
        description="转换为黑白",
        category="color",
        ffmpeg_filter="format=gray"
    ),

    "warm": VideoEffect(
        name="暖色调",
        description="添加暖色调",
        category="color",
        ffmpeg_filter="eq=contrast=1.05:brightness=0.05:saturation=1.1"
    ),

    "cool": VideoEffect(
        name="冷色调",
        description="添加冷色调",
        category="color",
        ffmpeg_filter="eq=contrast=1.05:brightness=0.05:saturation=0.9"
    ),

    # 速度效果
    "speed_1.5x": VideoEffect(
        name="1.5倍速",
        description="加速到1.5倍",
        category="speed",
        ffmpeg_filter="setpts=0.667*PTS",
        parameters={"speed": 1.5}
    ),

    "speed_2x": VideoEffect(
        name="2倍速",
        description="加速到2倍",
        category="speed",
        ffmpeg_filter="setpts=0.5*PTS",
        parameters={"speed": 2.0}
    ),

    "speed_0.75x": VideoEffect(
        name="0.75倍速",
        description="减速到0.75倍",
        category="speed",
        ffmpeg_filter="setpts=1.333*PTS",
        parameters={"speed": 0.75}
    ),

    "speed_0.5x": VideoEffect(
        name="0.5倍速",
        description="减速到0.5倍",
        category="speed",
        ffmpeg_filter="setpts=2.0*PTS",
        parameters={"speed": 0.5}
    ),

    # 变换效果
    "flip_horizontal": VideoEffect(
        name="水平翻转",
        description="左右翻转视频",
        category="transform",
        ffmpeg_filter="hflip"
    ),

    "flip_vertical": VideoEffect(
        name="垂直翻转",
        description="上下翻转视频",
        category="transform",
        ffmpeg_filter="vflip"
    ),

    "rotate_90": VideoEffect(
        name="旋转90度",
        description="顺时针旋转90度",
        category="transform",
        ffmpeg_filter="transpose=1"
    ),

    "rotate_180": VideoEffect(
        name="旋转180度",
        description="旋转180度",
        category="transform",
        ffmpeg_filter="transpose=1,transpose=1"
    ),

    "rotate_270": VideoEffect(
        name="旋转270度",
        description="顺时针旋转270度",
        category="transform",
        ffmpeg_filter="transpose=2"
    ),

    # 艺术效果
    "blur": VideoEffect(
        name="模糊",
        description="添加模糊效果",
        category="artistic",
        ffmpeg_filter="gblur=sigma=2",
        parameters={"sigma": 2}
    ),

    "sharpen": VideoEffect(
        name="锐化",
        description="锐化视频",
        category="artistic",
        ffmpeg_filter="unsharp=3:3:0.5"
    ),

    "vignette": VideoEffect(
        name="暗角",
        description="添加暗角效果",
        category="artistic",
        ffmpeg_filter="vignette"
    ),

    "film_grain": VideoEffect(
        name="胶片颗粒",
        description="添加胶片颗粒效果",
        category="artistic",
        ffmpeg_filter="noise=alls=10:allf=t"
    ),

    # 特殊效果
    "fade_in": VideoEffect(
        name="淡入",
        description="淡入效果（1秒）",
        category="transform",
        ffmpeg_filter="fade=t=in:st=0:d=1"
    ),

    "fade_out": VideoEffect(
        name="淡出",
        description="淡出效果（1秒）",
        category="transform",
        ffmpeg_filter="fade=t=out:st=-1:d=1"
    ),

    "zoom_in": VideoEffect(
        name="缓慢放大",
        description="缓慢放大效果",
        category="transform",
        ffmpeg_filter="zoompan=z='min(zoom+0.0015,1.5)':d=700",
        parameters={"duration": 700}
    )
}


def get_effect(name: str) -> Optional[VideoEffect]:
    """获取效果"""
    return EFFECTS.get(name)


def list_effects(category: Optional[str] = None) -> List[VideoEffect]:
    """列出效果"""
    effects = list(EFFECTS.values())

    if category:
        effects = [e for e in effects if e.category == category]

    return sorted(effects, key=lambda e: e.name)


def apply_effect(
    effect: VideoEffect,
    input_path: str,
    output_path: str
) -> bool:
    """应用效果到视频"""
    import subprocess
    import logging

    logger = logging.getLogger(__name__)

    # 构建 FFmpeg 命令
    cmd = [
        "ffmpeg",
        "-i", input_path,
        "-vf", effect.ffmpeg_filter,
        "-c:a", "copy",  # 保持音频不变
        output_path
    ]

    try:
        logger.info(f"应用效果: {effect.name}")
        result = subprocess.run(cmd, capture_output=True, text=True)

        if result.returncode == 0:
            logger.info(f"效果应用成功: {output_path}")
            return True
        else:
            logger.error(f"FFmpeg 错误: {result.stderr}")
            return False

    except Exception as e:
        logger.error(f"应用效果失败: {e}")
        return False


def combine_effects(effects: List[VideoEffect]) -> str:
    """组合多个效果为一个 FFmpeg 过滤器链"""
    filters = [e.ffmpeg_filter for e in effects]
    return ",".join(filters)


def apply_multiple_effects(
    effects: List[VideoEffect],
    input_path: str,
    output_path: str
) -> bool:
    """应用多个效果"""
    import subprocess
    import logging

    logger = logging.getLogger(__name__)

    # 组合过滤器
    combined_filter = combine_effects(effects)

    # 构建 FFmpeg 命令
    cmd = [
        "ffmpeg",
        "-i", input_path,
        "-vf", combined_filter,
        "-c:a", "copy",
        output_path
    ]

    try:
        effect_names = ", ".join([e.name for e in effects])
        logger.info(f"应用效果: {effect_names}")
        result = subprocess.run(cmd, capture_output=True, text=True)

        if result.returncode == 0:
            logger.info(f"效果应用成功: {output_path}")
            return True
        else:
            logger.error(f"FFmpeg 错误: {result.stderr}")
            return False

    except Exception as e:
        logger.error(f"应用效果失败: {e}")
        return False
