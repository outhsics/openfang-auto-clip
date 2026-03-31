#!/usr/bin/env python3
"""
OpenFang Auto Clip - 增强功能配置向导

帮助用户快速配置增强功能
"""

import os
import sys
import json
from pathlib import Path


def print_header(text):
    """打印标题"""
    print("\n" + "="*60)
    print(text)
    print("="*60)


def print_step(step, text):
    """打印步骤"""
    print(f"\n{step}. {text}")


def ask_yes_no(question, default=True):
    """询问是/否问题"""
    default_str = "Y/n" if default else "y/N"
    response = input(f"{question} [{default_str}]: ").strip().lower()

    if not response:
        return default

    return response in ['y', 'yes', '是', '好的']


def ask_input(question, default=None, required=False):
    """询问输入"""
    default_str = f" [{default}]:" if default else ": "
    response = input(f"{question}{default_str} ").strip()

    if not response:
        if required and not default:
            print("❌ 此项为必填")
            return ask_input(question, default, required)
        return default

    return response


def setup_stt_providers():
    """配置 STT 提供商"""
    print_header("🎤 配置语音识别 (STT) 提供商")

    providers = {
        "groq": {
            "name": "Groq Whisper",
            "description": "⚡ 超快速，部分免费",
            "env_key": "GROQ_API_KEY",
            "install": "pip install groq"
        },
        "openai": {
            "name": "OpenAI Whisper",
            "description": "🎵 高质量，付费",
            "env_key": "OPENAI_API_KEY",
            "install": "pip install openai"
        },
        "deepgram": {
            "name": "Deepgram",
            "description": "🎤 专业级，付费",
            "env_key": "DEEPGRAM_API_KEY",
            "install": "pip install deepgram-sdk"
        }
    }

    print("\n可用的 STT 提供商:")
    for key, provider in providers.items():
        print(f"  {key}: {provider['name']} - {provider['description']}")

    print("\n  local: Local Whisper - 🏠 完全离线，免费 (pip install openai-whisper)")

    choice = ask_input("\n选择默认 STT 提供商", "local").lower()

    if choice == "local":
        print("\n✅ Local Whisper 无需 API 密钥")
        print("💡 安装: pip install openai-whisper")
    elif choice in providers:
        provider = providers[choice]
        api_key = ask_input(f"输入 {provider['name']} API 密钥", required=True)

        # 设置环境变量
        os.environ[provider['env_key']] = api_key

        # 保存到 .env
        save_to_env(provider['env_key'], api_key)

        print(f"\n✅ {provider['name']} 已配置")
        print(f"💡 安装: {provider['install']}")
    else:
        print("❌ 无效选择，将使用 Local Whisper")

    return choice


def setup_tts_providers():
    """配置 TTS 提供商"""
    print_header("🔊 配置语音合成 (TTS) 提供商")

    providers = {
        "openai": {
            "name": "OpenAI TTS",
            "description": "🎵 高质量，付费",
            "env_key": "OPENAI_API_KEY",
            "install": "pip install openai"
        },
        "elevenlabs": {
            "name": "ElevenLabs",
            "description": "🎤 专业级，付费",
            "env_key": "ELEVENLABS_API_KEY",
            "install": "pip install elevenlabs"
        }
    }

    print("\n可用的 TTS 提供商:")
    for key, provider in providers.items():
        print(f"  {key}: {provider['name']} - {provider['description']}")

    print("\n  edge: Edge TTS - 💰 完全免费 (pip install edge-tts)")

    choice = ask_input("\n选择默认 TTS 提供商", "edge").lower()

    if choice == "edge":
        print("\n✅ Edge TTS 无需 API 密钥")
        print("💡 安装: pip install edge-tts")
    elif choice in providers:
        provider = providers[choice]
        api_key = ask_input(f"输入 {provider['name']} API 密钥", required=True)

        # 设置环境变量
        os.environ[provider['env_key']] = api_key

        # 保存到 .env
        save_to_env(provider['env_key'], api_key)

        print(f"\n✅ {provider['name']} 已配置")
        print(f"💡 安装: {provider['install']}")
    else:
        print("❌ 无效选择，将使用 Edge TTS")

    return choice


def setup_telegram():
    """配置 Telegram"""
    print_header("📱 配置 Telegram 发布")

    if not ask_yes_no("是否配置 Telegram 自动发布？", default=False):
        return None

    bot_token = ask_input("输入 Telegram Bot Token", required=True)
    chat_id = ask_input("输入默认频道/群组 ID", required=False)

    # 保存到环境变量
    os.environ["TELEGRAM_BOT_TOKEN"] = bot_token
    save_to_env("TELEGRAM_BOT_TOKEN", bot_token)

    if chat_id:
        os.environ["TELEGRAM_CHAT_ID"] = chat_id
        save_to_env("TELEGRAM_CHAT_ID", chat_id)

    print("\n✅ Telegram 已配置")
    print("💡 安装: pip install python-telegram-bot")

    return {
        "bot_token": bot_token,
        "chat_id": chat_id
    }


def setup_whatsapp():
    """配置 WhatsApp"""
    print_header("💬 配置 WhatsApp 发布")

    if not ask_yes_no("是否配置 WhatsApp 自动发布？", default=False):
        return None

    print("\n选择 WhatsApp 发布方式:")
    print("  1. pywhatkit (免费，需要手机)")
    print("  2. twilio (付费，API)")

    choice = ask_input("选择方式", "1")

    if choice == "1":
        print("\n✅ pywhatkit 无需 API 配置")
        print("💡 安装: pip install pywhatkit")
        return {"method": "pywhatkit"}
    else:
        account_sid = ask_input("输入 Twilio Account SID", required=True)
        auth_token = ask_input("输入 Twilio Auth Token", required=True)
        from_number = ask_input("输入 Twilio WhatsApp 号码", required=True)

        # 保存到环境变量
        os.environ["TWILIO_ACCOUNT_SID"] = account_sid
        os.environ["TWILIO_AUTH_TOKEN"] = auth_token
        os.environ["TWILIO_WHATSAPP_NUMBER"] = from_number

        save_to_env("TWILIO_ACCOUNT_SID", account_sid)
        save_to_env("TWILIO_AUTH_TOKEN", auth_token)
        save_to_env("TWILIO_WHATSAPP_NUMBER", from_number)

        print("\n✅ Twilio WhatsApp 已配置")
        print("💡 安装: pip install twilio")

        return {
            "method": "twilio",
            "account_sid": account_sid
        }


def save_to_env(key, value):
    """保存到 .env 文件"""
    env_file = Path.cwd() / ".env"

    # 追加到 .env
    with open(env_file, "a") as f:
        f.write(f"\n{key}={value}")


def save_config(config):
    """保存配置到文件"""
    config_dir = Path.home() / ".openfang"
    config_dir.mkdir(parents=True, exist_ok=True)

    config_file = config_dir / "enhancements_config.json"

    with open(config_file, "w") as f:
        json.dump(config, f, indent=2)

    print(f"\n✅ 配置已保存到: {config_file}")


def print_installation_commands(config):
    """打印安装命令"""
    print_header("📦 安装依赖")

    commands = []

    # 基础依赖
    commands.append("# 基础依赖")
    commands.append("pip install -r requirements.txt")

    # STT
    stt = config.get("stt_provider", "local")
    if stt == "groq":
        commands.append("\n# Groq Whisper")
        commands.append("pip install groq")
    elif stt == "openai":
        commands.append("\n# OpenAI Whisper")
        commands.append("pip install openai")
    elif stt == "deepgram":
        commands.append("\n# Deepgram")
        commands.append("pip install deepgram-sdk")
    elif stt == "local":
        commands.append("\n# Local Whisper")
        commands.append("pip install openai-whisper")

    # TTS
    tts = config.get("tts_provider", "edge")
    if tts == "openai":
        commands.append("\n# OpenAI TTS")
        commands.append("pip install openai")
    elif tts == "elevenlabs":
        commands.append("\n# ElevenLabs")
        commands.append("pip install elevenlabs")
    else:
        commands.append("\n# Edge TTS")
        commands.append("pip install edge-tts")

    # 社交平台
    if config.get("telegram"):
        commands.append("\n# Telegram")
        commands.append("pip install python-telegram-bot")

    if config.get("whatsapp"):
        method = config["whatsapp"].get("method", "pywhatkit")
        if method == "twilio":
            commands.append("\n# Twilio WhatsApp")
            commands.append("pip install twilio")
        else:
            commands.append("\n# pywhatkit")
            commands.append("pip install pywhatkit")

    print("\n".join(commands))


def print_next_steps(config):
    """打印后续步骤"""
    print_header("🎯 后续步骤")

    print("\n1. 测试配置:")
    print("   python3 -m enhancements.data_management.analytics")

    print("\n2. 处理第一个视频:")
    stt = config.get("stt_provider", "local")
    print(f"   ./auto_clip.sh \"VIDEO_URL\" --stt {stt}")

    if config.get("telegram"):
        print("\n3. 发布到 Telegram:")
        print("   ./auto_clip.sh \"VIDEO_URL\" --publish-telegram")

    print("\n4. 查看更多示例:")
    print("   ls examples/enhancements/")

    print("\n5. 阅读文档:")
    print("   cat docs/enhancements/README.md")


def main():
    """主函数"""
    print_header("🚀 OpenFang Auto Clip - 增强功能配置向导")

    print("\n此向导将帮助您配置以下功能:")
    print("  🎤 多种 AI 提供商 (STT/TTS)")
    print("  📱 社交平台自动发布")
    print("  💾 本地数据管理")
    print("  🎨 视频模板和效果")

    if not ask_yes_no("\n是否继续？"):
        print("\n❌ 配置已取消")
        return

    # 配置 STT
    stt_provider = setup_stt_providers()

    # 配置 TTS
    tts_provider = setup_tts_providers()

    # 配置社交平台
    telegram = setup_telegram()
    whatsapp = setup_whatsapp()

    # 保存配置
    config = {
        "version": "0.5.0",
        "stt_provider": stt_provider,
        "tts_provider": tts_provider,
        "telegram": telegram,
        "whatsapp": whatsapp
    }

    save_config(config)

    # 打印安装命令
    print_installation_commands(config)

    # 打印后续步骤
    print_next_steps(config)

    print_header("✅ 配置完成！")
    print("\n💡 提示: API 密钥已保存到 .env 文件，请勿提交到 Git")


if __name__ == "__main__":
    try:
        main()
    except KeyboardInterrupt:
        print("\n\n❌ 配置已取消")
        sys.exit(0)
    except Exception as e:
        print(f"\n❌ 错误: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)
