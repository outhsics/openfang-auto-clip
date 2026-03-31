"""
社交平台发布模块
"""

from .base import (
    SocialPublisher,
    PublishResult,
    PublishConfig,
    PlatformType
)
from .telegram import TelegramPublisher, publish_to_telegram
from .whatsapp import (
    TwilioWhatsAppPublisher,
    PyWhatKitPublisher,
    publish_to_whatsapp
)

__all__ = [
    # 基础接口
    "SocialPublisher",
    "PublishResult",
    "PublishConfig",
    "PlatformType",

    # 发布器
    "TelegramPublisher",
    "TwilioWhatsAppPublisher",
    "PyWhatKitPublisher",

    # 便捷函数
    "publish_to_telegram",
    "publish_to_whatsapp",
]
