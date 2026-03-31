"""
AI 提供商基础接口
"""

from abc import ABC, abstractmethod
from typing import Dict, List, Optional, Any
from dataclasses import dataclass


@dataclass
class STTResult:
    """语音识别结果"""
    text: str
    segments: List[Dict[str, Any]]
    language: str
    duration: float
    provider: str


@dataclass
class TTSResult:
    """语音合成结果"""
    audio_path: str
    duration: float
    provider: str
    voice: str


class STTProvider(ABC):
    """语音识别提供商基类"""

    def __init__(self, api_key: Optional[str] = None):
        self.api_key = api_key
        self.provider_name = self.__class__.__name__

    @abstractmethod
    def transcribe(
        self,
        audio_path: str,
        language: str = "auto",
        **kwargs
    ) -> STTResult:
        """转录音频为文本"""
        pass

    @abstractmethod
    def is_available(self) -> bool:
        """检查提供商是否可用"""
        pass

    def get_supported_languages(self) -> List[str]:
        """获取支持的语言列表"""
        return ["en", "zh", "es", "fr", "de", "ja", "ko"]


class TTSProvider(ABC):
    """语音合成提供商基类"""

    def __init__(self, api_key: Optional[str] = None):
        self.api_key = api_key
        self.provider_name = self.__class__.__name__

    @abstractmethod
    def synthesize(
        self,
        text: str,
        voice: str = "default",
        output_path: str = "output.mp3",
        **kwargs
    ) -> TTSResult:
        """合成语音"""
        pass

    @abstractmethod
    def is_available(self) -> bool:
        """检查提供商是否可用"""
        pass

    def get_available_voices(self) -> List[Dict[str, str]]:
        """获取可用的语音列表"""
        return [
            {"id": "default", "name": "Default Voice", "language": "en"}
        ]


class ProviderError(Exception):
    """提供商错误"""
    pass


class ProviderNotAvailableError(ProviderError):
    """提供商不可用"""
    pass


class ProviderAuthenticationError(ProviderError):
    """认证失败"""
    pass
