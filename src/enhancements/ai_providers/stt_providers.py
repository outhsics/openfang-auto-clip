"""
语音识别 (STT) 提供商实现

支持多个 STT 提供商：
- Groq Whisper (快速，部分免费)
- OpenAI Whisper (高质量，付费)
- Deepgram (快速，付费)
- Local Whisper (离线，免费)
"""

import os
import json
import logging
from typing import Optional, List, Dict, Any
from pathlib import Path

try:
    import groq
    GROQ_AVAILABLE = True
except ImportError:
    GROQ_AVAILABLE = False

try:
    import openai
    OPENAI_AVAILABLE = True
except ImportError:
    OPENAI_AVAILABLE = False

try:
    import whisper
    WHISPER_AVAILABLE = True
except ImportError:
    WHISPER_AVAILABLE = False

try:
    from deepgram import DeepgramClient
    DEEPGRAM_AVAILABLE = True
except ImportError:
    DEEPGRAM_AVAILABLE = False

from .base import STTProvider, STTResult, ProviderNotAvailableError, ProviderAuthenticationError

logger = logging.getLogger(__name__)


class GroqWhisperSTT(STTProvider):
    """Groq Whisper 语音识别 - 超快速"""

    def __init__(self, api_key: Optional[str] = None):
        super().__init__(api_key)
        if not GROQ_AVAILABLE:
            raise ProviderNotAvailableError("groq 库未安装: pip install groq")

        self.api_key = api_key or os.getenv("GROQ_API_KEY")
        if not self.api_key:
            raise ProviderAuthenticationError("GROQ_API_KEY 未设置")

        self.client = groq.Groq(api_key=self.api_key)

    def transcribe(
        self,
        audio_path: str,
        language: str = "auto",
        **kwargs
    ) -> STTResult:
        """使用 Groq Whisper 转录音频"""
        try:
            with open(audio_path, "rb") as audio_file:
                transcription = self.client.audio.transcriptions.create(
                    file=audio_file,
                    model="whisper-large-v3",
                    language=None if language == "auto" else language,
                    response_format="verbose_json",
                    **kwargs
                )

            segments = []
            if hasattr(transcription, 'segments'):
                for seg in transcription.segments:
                    segments.append({
                        "start": seg.get('start', 0),
                        "end": seg.get('end', 0),
                        "text": seg.get('text', '')
                    })

            return STTResult(
                text=transcription.text,
                segments=segments,
                language=transcription.language if hasattr(transcription, 'language') else language,
                duration=transcription.duration if hasattr(transcription, 'duration') else 0,
                provider="groq_whisper"
            )

        except Exception as e:
            logger.error(f"Groq Whisper 转录失败: {e}")
            raise

    def is_available(self) -> bool:
        """检查 Groq 是否可用"""
        try:
            # 简单的 API 测试
            return bool(self.api_key)
        except:
            return False


class OpenAIWhisperSTT(STTProvider):
    """OpenAI Whisper 语音识别 - 高质量"""

    def __init__(self, api_key: Optional[str] = None):
        super().__init__(api_key)
        if not OPENAI_AVAILABLE:
            raise ProviderNotAvailableError("openai 库未安装: pip install openai")

        self.api_key = api_key or os.getenv("OPENAI_API_KEY")
        if not self.api_key:
            raise ProviderAuthenticationError("OPENAI_API_KEY 未设置")

        self.client = openai.OpenAI(api_key=self.api_key)

    def transcribe(
        self,
        audio_path: str,
        language: str = "auto",
        model: str = "whisper-1",
        **kwargs
    ) -> STTResult:
        """使用 OpenAI Whisper 转录音频"""
        try:
            with open(audio_path, "rb") as audio_file:
                transcription = self.client.audio.transcriptions.create(
                    model=model,
                    file=audio_file,
                    language=None if language == "auto" else language,
                    response_format="verbose_json",
                    **kwargs
                )

            segments = []
            if hasattr(transcription, 'segments'):
                for seg in transcription.segments:
                    segments.append({
                        "start": seg.get('start', 0),
                        "end": seg.get('end', 0),
                        "text": seg.get('text', '')
                    })

            return STTResult(
                text=transcription.text,
                segments=segments,
                language=transcription.language if hasattr(transcription, 'language') else language,
                duration=transcription.duration if hasattr(transcription, 'duration') else 0,
                provider="openai_whisper"
            )

        except Exception as e:
            logger.error(f"OpenAI Whisper 转录失败: {e}")
            raise

    def is_available(self) -> bool:
        """检查 OpenAI 是否可用"""
        try:
            return bool(self.api_key)
        except:
            return False


class LocalWhisperSTT(STTProvider):
    """本地 Whisper 语音识别 - 完全离线"""

    def __init__(self, model_size: str = "base"):
        super().__init__(None)
        if not WHISPER_AVAILABLE:
            raise ProviderNotAvailableError("whisper 库未安装: pip install openai-whisper")

        self.model_size = model_size
        self.model = None

    def _load_model(self):
        """延迟加载 Whisper 模型"""
        if self.model is None:
            logger.info(f"加载 Whisper 模型: {self.model_size}")
            self.model = whisper.load_model(self.model_size)

    def transcribe(
        self,
        audio_path: str,
        language: str = "auto",
        **kwargs
    ) -> STTResult:
        """使用本地 Whisper 转录音频"""
        try:
            self._load_model()

            result = self.model.transcribe(
                audio_path,
                language=None if language == "auto" else language,
                **kwargs
            )

            segments = []
            for seg in result.get('segments', []):
                segments.append({
                    "start": seg.get('start', 0),
                    "end": seg.get('end', 0),
                    "text": seg.get('text', '')
                })

            return STTResult(
                text=result['text'],
                segments=segments,
                language=result.get('language', language),
                duration=result.get('duration', 0),
                provider=f"local_whisper_{self.model_size}"
            )

        except Exception as e:
            logger.error(f"本地 Whisper 转录失败: {e}")
            raise

    def is_available(self) -> bool:
        """检查本地 Whisper 是否可用"""
        return WHISPER_AVAILABLE

    def get_supported_languages(self) -> List[str]:
        """Whisper 支持更多语言"""
        return [
            "en", "zh", "de", "es", "ru", "ko", "fr", "ja", "pt", "tr",
            "pl", "ca", "nl", "ar", "sv", "it", "id", "hi", "fi", "vi",
            "he", "uk", "el", "ms", "cs", "ro", "da", "hu", "ta", "no",
            "th", "ur", "hr", "bg", "lt", "la", "mi", "ml", "cy", "sk",
            "te", "fa", "lv", "bn", "sr", "az", "sl", "kn", "et", "mk",
            "br", "eu", "is", "hy", "ne", "mn", "bs", "kk", "sq", "sw",
            "gl", "mr", "pa", "si", "km", "sn", "yo", "so", "af", "oc",
            "ka", "be", "tg", "sd", "gu", "am", "yi", "lo", "uz", "fo",
            "ht", "ps", "tk", "nn", "mt", "sa", "lb", "my", "bo", "te",
            "tl", "hmn", "cs", "bg", "mk", "kk"
        ]


class DeepgramSTT(STTProvider):
    """Deepgram 语音识别 - 快速且专业"""

    def __init__(self, api_key: Optional[str] = None):
        super().__init__(api_key)
        if not DEEPGRAM_AVAILABLE:
            raise ProviderNotAvailableError("deepgram 库未安装: pip install deepgram-sdk")

        self.api_key = api_key or os.getenv("DEEPGRAM_API_KEY")
        if not self.api_key:
            raise ProviderAuthenticationError("DEEPGRAM_API_KEY 未设置")

        self.client = DeepgramClient(self.api_key)

    def transcribe(
        self,
        audio_path: str,
        language: str = "auto",
        model: str = "nova-2",
        **kwargs
    ) -> STTResult:
        """使用 Deepgram 转录音频"""
        try:
            with open(audio_path, "rb") as audio_file:
                payload = {"buffer": audio_file}

                options = {
                    "smart_format": True,
                    "model": model,
                }

                if language != "auto":
                    options["language"] = language

                response = self.client.listen.rest.v("1").transcribe_file(
                    payload, options
                )

            result = response.to_json()
            data = json.loads(result)

            # 提取文本和片段
            text = ""
            segments = []

            if 'results' in data and 'channels' in data['results']:
                channel = data['results']['channels'][0]
                if 'alternatives' in channel:
                    alternative = channel['alternatives'][0]
                    text = alternative.get('transcript', '')

                    if 'words' in alternative:
                        for word in alternative['words']:
                            segments.append({
                                "start": word.get('start', 0),
                                "end": word.get('end', 0),
                                "text": word.get('word', '')
                            })

            # 检测语言
            detected_language = language
            if 'metadata' in data:
                detected_language = data['metadata'].get('language_info', {}).get('language', language)

            return STTResult(
                text=text,
                segments=segments,
                language=detected_language,
                duration=data.get('metadata', {}).get('duration', 0),
                provider="deepgram"
            )

        except Exception as e:
            logger.error(f"Deepgram 转录失败: {e}")
            raise

    def is_available(self) -> bool:
        """检查 Deepgram 是否可用"""
        try:
            return bool(self.api_key)
        except:
            return False


# 便捷函数
def get_stt_provider(
    provider_name: str,
    api_key: Optional[str] = None,
    **kwargs
) -> STTProvider:
    """获取 STT 提供商实例

    Args:
        provider_name: 提供商名称
            - "groq_whisper" 或 "groq"
            - "openai_whisper" 或 "openai"
            - "local_whisper" 或 "local"
            - "deepgram"
        api_key: API 密钥（如果需要）
        **kwargs: 其他参数

    Returns:
        STTProvider 实例
    """
    provider_name = provider_name.lower().replace("-", "_")

    if provider_name in ["groq_whisper", "groq"]:
        return GroqWhisperSTT(api_key)
    elif provider_name in ["openai_whisper", "openai"]:
        return OpenAIWhisperSTT(api_key)
    elif provider_name in ["local_whisper", "local"]:
        model_size = kwargs.get("model_size", "base")
        return LocalWhisperSTT(model_size)
    elif provider_name == "deepgram":
        return DeepgramSTT(api_key)
    else:
        raise ValueError(f"未知的 STT 提供商: {provider_name}")


def auto_select_stt() -> STTProvider:
    """自动选择可用的 STT 提供商

    优先级: Groq > OpenAI > Local Whisper
    """
    # 尝试 Groq (最快)
    if GROQ_AVAILABLE and os.getenv("GROQ_API_KEY"):
        try:
            return GroqWhisperSTT()
        except:
            pass

    # 尝试 OpenAI
    if OPENAI_AVAILABLE and os.getenv("OPENAI_API_KEY"):
        try:
            return OpenAIWhisperSTT()
        except:
            pass

    # 回退到本地 Whisper
    if WHISPER_AVAILABLE:
        return LocalWhisperSTT()

    raise ProviderNotAvailableError("没有可用的 STT 提供商")
