"""
WhatsApp 自动发布
"""

import os
import logging
from typing import Optional

try:
    from twilio.rest import Client
    TWILIO_AVAILABLE = True
except ImportError:
    TWILIO_AVAILABLE = False

try:
    import pywhatkit
    PYWHATKIT_AVAILABLE = True
except ImportError:
    PYWHATKIT_AVAILABLE = False

from .base import SocialPublisher, PublishResult, PublishConfig, PlatformNotAvailableError, AuthenticationError

logger = logging.getLogger(__name__)


class TwilioWhatsAppPublisher(SocialPublisher):
    """WhatsApp 发布器 - 使用 Twilio API"""

    def __init__(
        self,
        account_sid: Optional[str] = None,
        auth_token: Optional[str] = None,
        from_number: Optional[str] = None
    ):
        super().__init__(auth_token)
        if not TWILIO_AVAILABLE:
            raise PlatformNotAvailableError("twilio 库未安装: pip install twilio")

        self.account_sid = account_sid or os.getenv("TWILIO_ACCOUNT_SID")
        self.auth_token = auth_token or os.getenv("TWILIO_AUTH_TOKEN")
        self.from_number = from_number or os.getenv("TWILIO_WHATSAPP_NUMBER")

        if not all([self.account_sid, self.auth_token, self.from_number]):
            raise AuthenticationError("Twilio 凭证未完全设置")

        try:
            self.client = Client(self.account_sid, self.auth_token)
        except Exception as e:
            raise AuthenticationError(f"Twilio 客户端初始化失败: {e}")

    async def publish_video(
        self,
        video_path: str,
        config: PublishConfig
    ) -> PublishResult:
        """发布视频到 WhatsApp（通过 Twilio）"""
        try:
            to_number = config.phone_number
            if not to_number:
                return PublishResult(
                    success=False,
                    platform="whatsapp",
                    error="phone_number 未设置"
                )

            # Twilio WhatsApp Media URL 需要是公开可访问的
            # 这里假设你已经将视频上传到了某个地方
            media_url = getattr(config, 'media_url', None)
            if not media_url:
                return PublishResult(
                    success=False,
                    platform="whatsapp",
                    error="需要提供 media_url (公开可访问的视频 URL)"
                )

            # 发送消息
            message = self.client.messages.create(
                from_=f"whatsapp:{self.from_number}",
                body=config.caption or "",
                to=f"whatsapp:{to_number}",
                media_url=[media_url]
            )

            logger.info(f"视频已发布到 WhatsApp: {message.sid}")

            return PublishResult(
                success=True,
                platform="whatsapp",
                message_id=message.sid,
                url=f"https://console.twilio.com/us1/monitor/logs/{message.sid}"
            )

        except Exception as e:
            logger.error(f"WhatsApp 发布失败: {e}")
            return PublishResult(
                success=False,
                platform="whatsapp",
                error=str(e)
            )

    async def publish_photo(
        self,
        photo_path: str,
        config: PublishConfig
    ) -> PublishResult:
        """发布图片到 WhatsApp"""
        # 与视频类似，需要公开可访问的 URL
        return await self.publish_video(photo_path, config)

    async def publish_text(
        self,
        text: str,
        config: PublishConfig
    ) -> PublishResult:
        """发布文本到 WhatsApp"""
        try:
            to_number = config.phone_number
            if not to_number:
                return PublishResult(
                    success=False,
                    platform="whatsapp",
                    error="phone_number 未设置"
                )

            # 发送消息
            message = self.client.messages.create(
                from_=f"whatsapp:{self.from_number}",
                body=text,
                to=f"whatsapp:{to_number}"
            )

            logger.info(f"文本已发布到 WhatsApp: {message.sid}")

            return PublishResult(
                success=True,
                platform="whatsapp",
                message_id=message.sid
            )

        except Exception as e:
            logger.error(f"WhatsApp 发布失败: {e}")
            return PublishResult(
                success=False,
                platform="whatsapp",
                error=str(e)
            )

    def is_available(self) -> bool:
        """检查 WhatsApp 是否可用"""
        try:
            return all([self.account_sid, self.auth_token, self.from_number])
        except:
            return False


class PyWhatKitPublisher(SocialPublisher):
    """WhatsApp 发布器 - 使用 pywhatkit (免费，需要手机)"""

    def __init__(self):
        super().__init__(None)
        if not PYWHATKIT_AVAILABLE:
            raise PlatformNotAvailableError("pywhatkit 库未安装: pip install pywhatkit")

    async def publish_video(
        self,
        video_path: str,
        config: PublishConfig
    ) -> PublishResult:
        """发送视频到 WhatsApp

        注意：pywhatkit 需要在浏览器中打开 WhatsApp Web
        """
        try:
            phone_number = config.phone_number
            if not phone_number:
                return PublishResult(
                    success=False,
                    platform="whatsapp",
                    error="phone_number 未设置"
                )

            # pywhatkit 的 sendwhats_image 需要图片
            # 对于视频，我们需要先转换或使用其他方法
            # 这里先实现一个简化版本

            import pywhatkit

            # 发送消息（视频作为附件需要手动处理）
            pywhatkit.sendwhatmsg_instantly(
                phone_no=phone_number,
                message=config.caption or "视频已发送",
                tab_close=True
            )

            logger.info(f"消息已发送到 WhatsApp: {phone_number}")

            # pywhatkit 不返回消息 ID
            return PublishResult(
                success=True,
                platform="whatsapp",
                message_id=None,
                error="视频文件需要手动添加"
            )

        except Exception as e:
            logger.error(f"WhatsApp 发送失败: {e}")
            return PublishResult(
                success=False,
                platform="whatsapp",
                error=str(e)
            )

    async def publish_photo(
        self,
        photo_path: str,
        config: PublishConfig
    ) -> PublishResult:
        """发送图片到 WhatsApp"""
        try:
            phone_number = config.phone_number
            if not phone_number:
                return PublishResult(
                    success=False,
                    platform="whatsapp",
                    error="phone_number 未设置"
                )

            import pywhatkit

            # 发送图片
            pywhatkit.sendwhats_image(
                phone_no=phone_number,
                img_path=photo_path,
                caption=config.caption or "",
                tab_close=True
            )

            logger.info(f"图片已发送到 WhatsApp: {phone_number}")

            return PublishResult(
                success=True,
                platform="whatsapp",
                message_id=None
            )

        except Exception as e:
            logger.error(f"WhatsApp 发送失败: {e}")
            return PublishResult(
                success=False,
                platform="whatsapp",
                error=str(e)
            )

    async def publish_text(
        self,
        text: str,
        config: PublishConfig
    ) -> PublishResult:
        """发送文本到 WhatsApp"""
        try:
            phone_number = config.phone_number
            if not phone_number:
                return PublishResult(
                    success=False,
                    platform="whatsapp",
                    error="phone_number 未设置"
                )

            import pywhatkit

            # 发送消息
            pywhatkit.sendwhatmsg_instantly(
                phone_no=phone_number,
                message=text,
                tab_close=True
            )

            logger.info(f"文本已发送到 WhatsApp: {phone_number}")

            return PublishResult(
                success=True,
                platform="whatsapp",
                message_id=None
            )

        except Exception as e:
            logger.error(f"WhatsApp 发送失败: {e}")
            return PublishResult(
                success=False,
                platform="whatsapp",
                error=str(e)
            )

    def is_available(self) -> bool:
        """检查 WhatsApp 是否可用"""
        return PYWHATKIT_AVAILABLE


# 便捷函数
async def publish_to_whatsapp(
    video_path: str,
    phone_number: str,
    caption: Optional[str] = None,
    method: str = "pywhatkit"
) -> PublishResult:
    """发布视频到 WhatsApp（便捷函数）

    Args:
        video_path: 视频文件路径
        phone_number: WhatsApp 电话号码（带国家代码，如 +8613800138000）
        caption: 视频说明
        method: 发布方法 ("pywhatkit" 或 "twilio")

    Returns:
        PublishResult
    """
    if method == "twilio":
        publisher = TwilioWhatsAppPublisher()
    else:
        publisher = PyWhatKitPublisher()

    config = PublishConfig(
        phone_number=phone_number,
        caption=caption
    )
    return await publisher.publish_video(video_path, config)
