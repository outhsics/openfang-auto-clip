"""
社交平台发布使用示例

演示如何自动发布到 Telegram 和 WhatsApp
"""

import sys
import os
import asyncio
from pathlib import Path

# 添加项目根目录到路径
project_root = Path(__file__).parent.parent
sys.path.insert(0, str(project_root))

from src.enhancements.social_publishing import (
    TelegramPublisher,
    publish_to_telegram,
    publish_to_whatsapp,
    PyWhatKitPublisher,
    PublishConfig
)


async def example_telegram_video():
    """示例 1: 发布视频到 Telegram"""
    print("\n📱 示例 1: 发布视频到 Telegram")

    try:
        # 方法 1: 使用便捷函数
        result = await publish_to_telegram(
            video_path="path/to/video.mp4",
            chat_id="@your_channel",  # 或 chat_id
            caption="🎬 新视频发布了！\n\n#shorts #viral",
            silent=False
        )

        if result.success:
            print(f"✅ 发布成功!")
            print(f"消息 ID: {result.message_id}")
            print(f"链接: {result.url}")
        else:
            print(f"❌ 发布失败: {result.error}")

    except Exception as e:
        print(f"❌ 错误: {e}")
        print("💡 提示: 请设置 TELEGRAM_BOT_TOKEN 环境变量")


async def example_telegram_photo():
    """示例 2: 发布图片到 Telegram"""
    print("\n📸 示例 2: 发布图片到 Telegram")

    try:
        publisher = TelegramPublisher()

        config = PublishConfig(
            chat_id="@your_channel",
            caption="✨ 新内容！",
            silent=False
        )

        result = await publisher.publish_photo(
            photo_path="path/to/photo.jpg",
            config=config
        )

        if result.success:
            print(f"✅ 发布成功!")
            print(f"链接: {result.url}")

    except Exception as e:
        print(f"❌ 错误: {e}")


async def example_telegram_text():
    """示例 3: 发布文本到 Telegram"""
    print("\n💬 示例 3: 发布文本到 Telegram")

    try:
        result = await publish_to_telegram(
            video_path="",  # 文本消息不需要视频
            chat_id="@your_channel",
            caption="📢 重要通知！\n\n这是一条测试消息。"
        )

        if result.success:
            print(f"✅ 发布成功!")

    except Exception as e:
        print(f"❌ 错误: {e}")


async def example_whatsapp_pywhatkit():
    """示例 4: 使用 pywhatkit 发布到 WhatsApp（免费）"""
    print("\n💬 示例 4: WhatsApp - pywhatkit（免费）")

    try:
        from src.enhancements.social_publishing import PyWhatKitPublisher

        publisher = PyWhatKitPublisher()

        config = PublishConfig(
            phone_number="+8613800138000",  # 带国家代码
            caption="🎬 新视频！"
        )

        # 注意：pywhatkit 需要在浏览器中打开 WhatsApp Web
        result = await publisher.publish_video(
            video_path="path/to/video.mp4",
            config=config
        )

        if result.success:
            print(f"✅ 发送成功!")
            print("💡 请在浏览器中完成发送")

    except Exception as e:
        print(f"❌ 错误: {e}")


async def example_whatsapp_twilio():
    """示例 5: 使用 Twilio 发布到 WhatsApp（付费）"""
    print("\n💬 示例 5: WhatsApp - Twilio API（付费）")

    try:
        from src.enhancements.social_publishing import TwilioWhatsAppPublisher

        publisher = TwilioWhatsAppPublisher()

        # 注意：视频需要先上传到公开可访问的 URL
        config = PublishConfig(
            phone_number="+8613800138000",
            caption="🎬 新视频！",
            media_url="https://example.com/video.mp4"  # 公开 URL
        )

        result = await publisher.publish_video(
            video_path="",  # Twilio 使用 media_url
            config=config
        )

        if result.success:
            print(f"✅ 发送成功!")
            print(f"消息 ID: {result.message_id}")

    except Exception as e:
        print(f"❌ 错误: {e}")
        print("💡 提示: 请设置 Twilio 环境变量")


async def example_batch_publish():
    """示例 6: 批量发布到多个平台"""
    print("\n📤 示例 6: 批量发布到多个平台")

    video_path = "path/to/video.mp4"
    caption = "🎬 新视频发布了！\n\n#shorts #viral"

    results = []

    # 发布到 Telegram
    try:
        result = await publish_to_telegram(
            video_path=video_path,
            chat_id="@your_channel",
            caption=caption
        )
        results.append(("Telegram", result))
    except Exception as e:
        results.append(("Telegram", e))

    # 发布到 WhatsApp
    try:
        result = await publish_to_whatsapp(
            video_path=video_path,
            phone_number="+8613800138000",
            caption=caption
        )
        results.append(("WhatsApp", result))
    except Exception as e:
        results.append(("WhatsApp", e))

    # 打印结果
    print("\n批量发布结果:")
    for platform, result in results:
        if isinstance(result, Exception):
            print(f"{platform}: ❌ {result}")
        elif result.success:
            print(f"{platform}: ✅ 成功")
        else:
            print(f"{platform}: ❌ {result.error}")


async def example_scheduled_publish():
    """示例 7: 定时发布（Telegram）"""
    print("\n⏰ 示例 7: 定时发布到 Telegram")

    try:
        publisher = TelegramPublisher()

        config = PublishConfig(
            chat_id="@your_channel",
            caption="⏰ 定时发布的内容",
            schedule="2024-01-01 12:00:00"  # UTC 时间
        )

        # 注意：定时发送需要服务器端支持
        # 这里只是示例，实际实现可能不同

        print("💡 定时发送功能需要额外的服务器支持")
        print("建议使用 cron 任务或 Telegram 的内置调度功能")

    except Exception as e:
        print(f"❌ 错误: {e}")


def example_get_telegram_bot_info():
    """示例 8: 获取 Telegram Bot 信息"""
    print("\n🤖 示例 8: 获取 Telegram Bot 信息")

    async def get_bot_info():
        try:
            publisher = TelegramPublisher()
            me = await publisher.get_me()

            if me:
                print(f"✅ Bot 信息:")
                print(f"  ID: {me['id']}")
                print(f"  名称: {me['name']}")
                print(f"  用户名: @{me['username']}")
            else:
                print("❌ 无法获取 Bot 信息")

        except Exception as e:
            print(f"❌ 错误: {e}")

    asyncio.run(get_bot_info())


def main():
    """运行所有示例"""
    print("="*60)
    print("📱 社交平台发布示例")
    print("="*60)

    # 运行单个示例
    # asyncio.run(example_telegram_video())
    # asyncio.run(example_whatsapp_pywhatkit())
    # asyncio.run(example_batch_publish())

    # 获取 Bot 信息
    example_get_telegram_bot_info()


if __name__ == "__main__":
    main()
