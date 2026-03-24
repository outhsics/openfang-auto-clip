"""
AIGC (AI Generated Content) Integration for OpenFang Auto Clip.

Provides AI-powered image and video generation capabilities.
"""

from .providers import AIProvider, get_provider
from .image_generator import ImageGenerator, generate_image
from .video_generator import VideoGenerator, generate_video

__all__ = [
    "AIProvider",
    "get_provider",
    "ImageGenerator",
    "generate_image",
    "VideoGenerator",
    "generate_video",
]
