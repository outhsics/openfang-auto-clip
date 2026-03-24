"""
OpenFang Agent Skills System

Compatible with OpenClaw agent framework for video automation tasks.
"""

from .core import Skill, SkillRegistry, SkillContext, SkillResult
from .skills import (
    VideoDownloadSkill,
    VideoTransformSkill,
    BatchProcessSkill,
    AIGCImageSkill,
    AIGCVideoSkill,
    TranscriptGenerateSkill,
    ClipExtractSkill
)
from .executor import SkillExecutor

__all__ = [
    "Skill",
    "SkillRegistry",
    "SkillContext",
    "SkillResult",
    "SkillExecutor",
    "VideoDownloadSkill",
    "VideoTransformSkill",
    "BatchProcessSkill",
    "AIGCImageSkill",
    "AIGCVideoSkill",
    "TranscriptGenerateSkill",
    "ClipExtractSkill",
]
