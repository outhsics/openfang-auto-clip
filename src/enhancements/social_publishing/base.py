"""
社交平台发布基础接口
"""

from abc import ABC, abstractmethod
from typing import Dict, List, Optional
from dataclasses import dataclass
from enum import Enum


class PlatformType(Enum):
    """社交平台类型"""
    TELEGRAM = "telegram"
    WHATSAPP = "whatsapp"
    DISCORD = "discord"
    SLACK = "slack"


@dataclass
class PublishResult:
    """发布结果"""
    success: bool
    platform: str
    message_id: Optional[str] = None
    error: Optional[str] = None
    url: Optional[str] = None


@dataclass
class PublishConfig:
    """发布配置"""
    # 目标
    chat_id: Optional[str] = None  # Telegram/WhatsApp
    channel_id: Optional[str] = None  # Telegram Channel
    phone_number: Optional[str] = None  # WhatsApp

    # 内容
    caption: Optional[str] = None
    title: Optional[str] = None
    description: Optional[str] = None

    # 选项
    silent: bool = False  # 无声发送（Telegram）
    preview: bool = True  # 显示链接预览
    schedule: Optional[str] = None  # 定时发送


class SocialPublisher(ABC):
    """社交平台发布器基类"""

    def __init__(self, api_key: Optional[str] = None):
        self.api_key = api_key
        self.platform_name = self.__class__.__name__

    @abstractmethod
    def publish_video(
        self,
        video_path: str,
        config: PublishConfig
    ) -> PublishResult:
        """发布视频"""
        pass

    @abstractmethod
    def publish_photo(
        self,
        photo_path: str,
        config: PublishConfig
    ) -> PublishResult:
        """发布图片"""
        pass

    @abstractmethod
    def publish_text(
        self,
        text: str,
        config: PublishConfig
    ) -> PublishResult:
        """发布文本"""
        pass

    @abstractmethod
    def is_available(self) -> bool:
        """检查平台是否可用"""
        pass

    def validate_config(self, config: PublishConfig) -> bool:
        """验证配置"""
        return True


class PublishError(Exception):
    """发布错误"""
    pass


class PlatformNotAvailableError(PublishError):
    """平台不可用"""
    pass


class AuthenticationError(PublishError):
    """认证失败"""
    pass


class RateLimitError(PublishError):
    """速率限制"""
    pass
