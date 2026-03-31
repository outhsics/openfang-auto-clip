"""
视频模板和效果模块

提供预设的视频处理模板和特效
"""

from .presets import (
    VideoPreset,
    get_preset,
    list_presets,
    apply_preset
)
from .effects import (
    VideoEffect,
    get_effect,
    list_effects,
    apply_effect
)

__all__ = [
    # 预设
    "VideoPreset",
    "get_preset",
    "list_presets",
    "apply_preset",

    # 特效
    "VideoEffect",
    "get_effect",
    "list_effects",
    "apply_effect",
]
