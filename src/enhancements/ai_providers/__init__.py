"""
AI 提供商模块
"""

from .base import STTProvider, TTSProvider, STTResult, TTSResult
from .stt_providers import (
    GroqWhisperSTT,
    OpenAIWhisperSTT,
    LocalWhisperSTT,
    DeepgramSTT,
    get_stt_provider,
    auto_select_stt
)
from .tts_providers import (
    EdgeTTS,
    OpenAITTS,
    ElevenLabsTTS,
    get_tts_provider,
    auto_select_tts
)

__all__ = [
    # 基础接口
    "STTProvider",
    "TTSProvider",
    "STTResult",
    "TTSResult",

    # STT 提供商
    "GroqWhisperSTT",
    "OpenAIWhisperSTT",
    "LocalWhisperSTT",
    "DeepgramSTT",
    "get_stt_provider",
    "auto_select_stt",

    # TTS 提供商
    "EdgeTTS",
    "OpenAITTS",
    "ElevenLabsTTS",
    "get_tts_provider",
    "auto_select_tts",
]
