"""
语音合成 (TTS) 提供商实现

支持多个 TTS 提供商：
- Edge TTS (免费，多语言)
- OpenAI TTS (高质量，付费)
- ElevenLabs (专业级，付费)
"""

import os
import logging
from typing import Optional, List, Dict, Any
from pathlib import Path

try:
    import edge_tts
    EDGE_TTS_AVAILABLE = True
except ImportError:
    EDGE_TTS_AVAILABLE = False

try:
    import openai
    OPENAI_AVAILABLE = True
except ImportError:
    OPENAI_AVAILABLE = False

try:
    import elevenlabs
    ELEVENLABS_AVAILABLE = True
except ImportError:
    ELEVENLABS_AVAILABLE = False

from .base import TTSProvider, TTSResult, ProviderNotAvailableError, ProviderAuthenticationError

logger = logging.getLogger(__name__)


class EdgeTTS(TTSProvider):
    """Microsoft Edge TTS - 完全免费"""

    def __init__(self, api_key: Optional[str] = None):
        super().__init__(None)
        if not EDGE_TTS_AVAILABLE:
            raise ProviderNotAvailableError("edge-tts 库未安装: pip install edge-tts")

        # Edge TTS 不需要 API 密钥
        self.voices = None

    async def _get_voices(self):
        """获取可用语音列表"""
        if self.voices is None:
            self.voices = await edge_tts.list_voices()
        return self.voices

    def synthesize(
        self,
        text: str,
        voice: str = "en-US-AriaNeural",
        output_path: str = "output.mp3",
        **kwargs
    ) -> TTSResult:
        """使用 Edge TTS 合成语音"""
        try:
            import asyncio

            async def _synthesize():
                communicate = edge_tts.Communicate(text, voice)
                await communicate.save(output_path)
                return output_path

            # 运行异步函数
            loop = asyncio.new_event_loop()
            asyncio.set_event_loop(loop)
            audio_path = loop.run_until_complete(_synthesize())
            loop.close()

            # 获取音频时长
            duration = self._get_audio_duration(audio_path)

            return TTSResult(
                audio_path=audio_path,
                duration=duration,
                provider="edge_tts",
                voice=voice
            )

        except Exception as e:
            logger.error(f"Edge TTS 合成失败: {e}")
            raise

    def _get_audio_duration(self, audio_path: str) -> float:
        """获取音频时长"""
        try:
            from pydub import AudioSegment
            audio = AudioSegment.from_file(audio_path)
            return len(audio) / 1000.0  # 转换为秒
        except:
            return 0.0

    def is_available(self) -> bool:
        """检查 Edge TTS 是否可用"""
        return EDGE_TTS_AVAILABLE

    def get_available_voices(self) -> List[Dict[str, str]]:
        """获取可用的语音列表"""
        try:
            import asyncio

            async def _get_voices():
                voices = await edge_tts.list_voices()
                return [
                    {
                        "id": v.get("Name"),
                        "name": v.get("FriendlyName"),
                        "language": v.get("Locale"),
                        "gender": v.get("Gender")
                    }
                    for v in voices
                ]

            loop = asyncio.new_event_loop()
            asyncio.set_event_loop(loop)
            voices = loop.run_until_complete(_get_voices())
            loop.close()

            return voices
        except:
            return []


class OpenAITTS(TTSProvider):
    """OpenAI TTS - 高质量"""

    def __init__(self, api_key: Optional[str] = None):
        super().__init__(api_key)
        if not OPENAI_AVAILABLE:
            raise ProviderNotAvailableError("openai 库未安装: pip install openai")

        self.api_key = api_key or os.getenv("OPENAI_API_KEY")
        if not self.api_key:
            raise ProviderAuthenticationError("OPENAI_API_KEY 未设置")

        self.client = openai.OpenAI(api_key=self.api_key)

        # 可用模型和语音
        self.models = ["tts-1", "tts-1-hd"]
        self.voices = ["alloy", "echo", "fable", "onyx", "nova", "shimmer"]

    def synthesize(
        self,
        text: str,
        voice: str = "alloy",
        model: str = "tts-1",
        output_path: str = "output.mp3",
        **kwargs
    ) -> TTSResult:
        """使用 OpenAI TTS 合成语音"""
        try:
            response = self.client.audio.speech.create(
                model=model,
                voice=voice,
                input=text
            )

            # 保存音频
            response.stream_to_file(output_path)

            # 获取音频时长
            duration = self._get_audio_duration(output_path)

            return TTSResult(
                audio_path=output_path,
                duration=duration,
                provider="openai_tts",
                voice=voice
            )

        except Exception as e:
            logger.error(f"OpenAI TTS 合成失败: {e}")
            raise

    def _get_audio_duration(self, audio_path: str) -> float:
        """获取音频时长"""
        try:
            from pydub import AudioSegment
            audio = AudioSegment.from_file(audio_path)
            return len(audio) / 1000.0
        except:
            return 0.0

    def is_available(self) -> bool:
        """检查 OpenAI TTS 是否可用"""
        try:
            return bool(self.api_key)
        except:
            return False

    def get_available_voices(self) -> List[Dict[str, str]]:
        """获取可用的语音列表"""
        return [
            {"id": voice, "name": voice.capitalize(), "language": "en"}
            for voice in self.voices
        ]


class ElevenLabsTTS(TTSProvider):
    """ElevenLabs TTS - 专业级语音合成"""

    def __init__(self, api_key: Optional[str] = None):
        super().__init__(api_key)
        if not ELEVENLABS_AVAILABLE:
            raise ProviderNotAvailableError("elevenlabs 库未安装: pip install elevenlabs")

        self.api_key = api_key or os.getenv("ELEVENLABS_API_KEY")
        if not self.api_key:
            raise ProviderAuthenticationError("ELEVENLABS_API_KEY 未设置")

        self.client = elevenlabs.ElevenLabs(api_key=self.api_key)

    def synthesize(
        self,
        text: str,
        voice: str = "rachel",
        model: str = "eleven_monolingual_v1",
        output_path: str = "output.mp3",
        **kwargs
    ) -> TTSResult:
        """使用 ElevenLabs 合成语音"""
        try:
            # 生成语音
            audio = self.client.generate(
                text=text,
                voice=voice,
                model=model
            )

            # 保存音频
            with open(output_path, "wb") as f:
                for chunk in audio:
                    f.write(chunk)

            # 获取音频时长
            duration = self._get_audio_duration(output_path)

            return TTSResult(
                audio_path=output_path,
                duration=duration,
                provider="elevenlabs",
                voice=voice
            )

        except Exception as e:
            logger.error(f"ElevenLabs 合成失败: {e}")
            raise

    def _get_audio_duration(self, audio_path: str) -> float:
        """获取音频时长"""
        try:
            from pydub import AudioSegment
            audio = AudioSegment.from_file(audio_path)
            return len(audio) / 1000.0
        except:
            return 0.0

    def is_available(self) -> bool:
        """检查 ElevenLabs 是否可用"""
        try:
            return bool(self.api_key)
        except:
            return False

    def get_available_voices(self) -> List[Dict[str, str]]:
        """获取可用的语音列表"""
        try:
            voices = self.client.voices.get_all()
            return [
                {
                    "id": voice.voice_id,
                    "name": voice.name,
                    "language": voice.labels.get("accent", "unknown")
                }
                for voice in voices
            ]
        except:
            return []


# 便捷函数
def get_tts_provider(
    provider_name: str,
    api_key: Optional[str] = None,
    **kwargs
) -> TTSProvider:
    """获取 TTS 提供商实例

    Args:
        provider_name: 提供商名称
            - "edge_tts" 或 "edge"
            - "openai_tts" 或 "openai"
            - "elevenlabs" 或 "eleven"
        api_key: API 密钥（如果需要）
        **kwargs: 其他参数

    Returns:
        TTSProvider 实例
    """
    provider_name = provider_name.lower().replace("-", "_")

    if provider_name in ["edge_tts", "edge"]:
        return EdgeTTS()
    elif provider_name in ["openai_tts", "openai"]:
        return OpenAITTS(api_key)
    elif provider_name in ["elevenlabs", "eleven"]:
        return ElevenLabsTTS(api_key)
    else:
        raise ValueError(f"未知的 TTS 提供商: {provider_name}")


def auto_select_tts() -> TTSProvider:
    """自动选择可用的 TTS 提供商

    优先级: Edge TTS (免费) > OpenAI > ElevenLabs
    """
    # 优先使用免费的 Edge TTS
    if EDGE_TTS_AVAILABLE:
        return EdgeTTS()

    # 尝试 OpenAI
    if OPENAI_AVAILABLE and os.getenv("OPENAI_API_KEY"):
        try:
            return OpenAITTS()
        except:
            pass

    # 尝试 ElevenLabs
    if ELEVENLABS_AVAILABLE and os.getenv("ELEVENLABS_API_KEY"):
        try:
            return ElevenLabsTTS()
        except:
            pass

    raise ProviderNotAvailableError("没有可用的 TTS 提供商")
