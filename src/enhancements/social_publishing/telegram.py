"""
Telegram 自动发布
"""

import os
import logging
from typing import Optional

try:
    from telegram import Bot, InputFile
    from telegram.error import TelegramError
    TELEGRAM_AVAILABLE = True
except ImportError:
    TELEGRAM_AVAILABLE = False

from .base import SocialPublisher, PublishResult, PublishConfig, PlatformNotAvailableError, AuthenticationError

logger = logging.getLogger(__name__)


class TelegramPublisher(SocialPublisher):
    """Telegram 发布器"""

    def __init__(self, bot_token: Optional[str] = None):
        super().__init__(bot_token)
        if not TELEGRAM_AVAILABLE:
            raise PlatformNotAvailableError("python-telegram-bot 库未安装: pip install python-telegram-bot")

        self.bot_token = bot_token or os.getenv("TELEGRAM_BOT_TOKEN")
        if not self.bot_token:
            raise AuthenticationError("TELEGRAM_BOT_TOKEN 未设置")

        try:
            self.bot = Bot(token=self.bot_token)
        except Exception as e:
            raise AuthenticationError(f"Telegram Bot 初始化失败: {e}")

    async def publish_video(
        self,
        video_path: str,
        config: PublishConfig
    ) -> PublishResult:
        """发布视频到 Telegram"""
        try:
            chat_id = config.chat_id or config.channel_id
            if not chat_id:
                return PublishResult(
                    success=False,
                    platform="telegram",
                    error="chat_id 或 channel_id 未设置"
                )

            # 读取视频文件
            with open(video_path, 'rb') as video_file:
                # 发送视频
                message = await self.bot.send_video(
                    chat_id=chat_id,
                    video=video_file,
                    caption=config.caption,
                    disable_notification=config.silent,
                    parse_mode='Markdown'
                )

            # 构建消息链接
            if hasattr(message, 'message_id'):
                url = f"https://t.me/{chat_id.replace('@', '')}/{message.message_id}"
            else:
                url = None

            logger.info(f"视频已发布到 Telegram: {message.message_id}")

            return PublishResult(
                success=True,
                platform="telegram",
                message_id=str(message.message_id),
                url=url
            )

        except TelegramError as e:
            logger.error(f"Telegram 发布失败: {e}")
            return PublishResult(
                success=False,
                platform="telegram",
                error=str(e)
            )

    async def publish_photo(
        self,
        photo_path: str,
        config: PublishConfig
    ) -> PublishResult:
        """发布图片到 Telegram"""
        try:
            chat_id = config.chat_id or config.channel_id
            if not chat_id:
                return PublishResult(
                    success=False,
                    platform="telegram",
                    error="chat_id 或 channel_id 未设置"
                )

            # 读取图片文件
            with open(photo_path, 'rb') as photo_file:
                # 发送图片
                message = await self.bot.send_photo(
                    chat_id=chat_id,
                    photo=photo_file,
                    caption=config.caption,
                    disable_notification=config.silent,
                    parse_mode='Markdown'
                )

            # 构建消息链接
            if hasattr(message, 'message_id'):
                url = f"https://t.me/{chat_id.replace('@', '')}/{message.message_id}"
            else:
                url = None

            logger.info(f"图片已发布到 Telegram: {message.message_id}")

            return PublishResult(
                success=True,
                platform="telegram",
                message_id=str(message.message_id),
                url=url
            )

        except TelegramError as e:
            logger.error(f"Telegram 发布失败: {e}")
            return PublishResult(
                success=False,
                platform="telegram",
                error=str(e)
            )

    async def publish_text(
        self,
        text: str,
        config: PublishConfig
    ) -> PublishResult:
        """发布文本到 Telegram"""
        try:
            chat_id = config.chat_id or config.channel_id
            if not chat_id:
                return PublishResult(
                    success=False,
                    platform="telegram",
                    error="chat_id 或 channel_id 未设置"
                )

            # 发送文本
            message = await self.bot.send_message(
                chat_id=chat_id,
                text=text,
                disable_notification=config.silent,
                disable_web_page_preview=not config.preview,
                parse_mode='Markdown'
            )

            # 构建消息链接
            if hasattr(message, 'message_id'):
                url = f"https://t.me/{chat_id.replace('@', '')}/{message.message_id}"
            else:
                url = None

            logger.info(f"文本已发布到 Telegram: {message.message_id}")

            return PublishResult(
                success=True,
                platform="telegram",
                message_id=str(message.message_id),
                url=url
            )

        except TelegramError as e:
            logger.error(f"Telegram 发布失败: {e}")
            return PublishResult(
                success=False,
                platform="telegram",
                error=str(e)
            )

    def is_available(self) -> bool:
        """检查 Telegram 是否可用"""
        try:
            return bool(self.bot_token)
        except:
            return False

    async def get_me(self) -> Optional[Dict]:
        """获取 Bot 信息"""
        try:
            me = await self.bot.get_me()
            return {
                "id": me.id,
                "name": me.full_name,
                "username": me.username
            }
        except:
            return None


# 便捷函数
async def publish_to_telegram(
    video_path: str,
    chat_id: str,
    caption: Optional[str] = None,
    bot_token: Optional[str] = None,
    silent: bool = False
) -> PublishResult:
    """发布视频到 Telegram（便捷函数）

    Args:
        video_path: 视频文件路径
        chat_id: Telegram 聊天 ID 或频道 ID
        caption: 视频说明
        bot_token: Telegram Bot Token（可选，默认从环境变量读取）
        silent: 是否静默发送

    Returns:
        PublishResult
    """
    publisher = TelegramPublisher(bot_token)
    config = PublishConfig(
        chat_id=chat_id,
        caption=caption,
        silent=silent
    )
    return await publisher.publish_video(video_path, config)
