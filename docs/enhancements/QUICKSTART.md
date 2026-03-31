# 🚀 增强功能快速开始指南

欢迎使用 OpenFang Auto Clip 增强功能！本指南将帮助您在 5 分钟内开始使用。

## 📋 前置要求

- Python 3.9+
- 已安装 OpenFang Auto Clip
- （可选）API 密钥（用于云服务提供商）

## ⚡ 3 步快速开始

### 1️⃣ 运行配置向导

```bash
python3 scripts/setup_enhancements.py
```

向导将引导您配置：
- AI 提供商（STT/TTS）
- 社交平台发布
- 本地数据管理

### 2️⃣ 安装依赖

根据您的配置，向导会输出安装命令。例如：

```bash
# 基础依赖
pip install -r requirements.txt

# Local Whisper（免费，离线）
pip install openai-whisper

# Edge TTS（免费）
pip install edge-tts
```

### 3️⃣ 开始使用

```bash
# 处理视频（使用本地 Whisper）
./auto_clip.sh "https://www.youtube.com/watch?v=VIDEO_ID" --stt local_whisper

# 使用 Groq Whisper（超快）
./auto_clip.sh "VIDEO_URL" --stt groq_whisper

# 自动发布到 Telegram
./auto_clip.sh "VIDEO_URL" --publish-telegram
```

## 🎤 AI 提供商配置

### 语音识别 (STT)

#### Local Whisper（推荐新手）

**优点**: 完全免费、离线使用、隐私安全
**缺点**: 速度较慢

```bash
# 安装
pip install openai-whisper

# 使用
./auto_clip.sh "VIDEO_URL" --stt local_whisper
```

#### Groq Whisper（推荐）

**优点**: 超快速、部分免费
**缺点**: 需要 API 密钥

```bash
# 安装
pip install groq

# 设置 API 密钥
export GROQ_API_KEY="your_api_key_here"

# 使用
./auto_clip.sh "VIDEO_URL" --stt groq_whisper
```

获取 API 密钥: https://console.groq.com/

#### OpenAI Whisper

**优点**: 高质量、准确
**缺点**: 付费

```bash
# 安装
pip install openai

# 设置 API 密钥
export OPENAI_API_KEY="your_api_key_here"

# 使用
./auto_clip.sh "VIDEO_URL" --stt openai_whisper
```

### 语音合成 (TTS)

#### Edge TTS（推荐）

**优点**: 完全免费、多语言
**缺点**: 音质一般

```bash
# 安装
pip install edge-tts

# 使用
./auto_clip.sh "VIDEO_URL" --tts edge_tts
```

#### OpenAI TTS

**优点**: 高质量、自然
**缺点**: 付费

```bash
# 设置 API 密钥（如果已设置 STT 则无需重复）
export OPENAI_API_KEY="your_api_key_here"

# 使用
./auto_clip.sh "VIDEO_URL" --tts openai_tts
```

## 📱 社交平台配置

### Telegram

#### 步骤 1: 创建 Bot

1. 在 Telegram 中搜索 [@BotFather](https://t.me/BotFather)
2. 发送 `/newbot` 命令
3. 按提示设置 bot 名称和用户名
4. 保存 API Token

#### 步骤 2: 安装依赖

```bash
pip install python-telegram-bot
```

#### 步骤 3: 配置

```bash
# 设置环境变量
export TELEGRAM_BOT_TOKEN="your_bot_token_here"
export TELEGRAM_CHAT_ID="@your_channel"
```

#### 步骤 4: 使用

```bash
# 发布到 Telegram
./auto_clip.sh "VIDEO_URL" --publish-telegram
```

### WhatsApp

#### 方法 1: pywhatkit（免费）

```bash
# 安装
pip install pywhatkit

# 使用（需要在浏览器中完成发送）
./auto_clip.sh "VIDEO_URL" --publish-whatsapp
```

#### 方法 2: Twilio（付费）

1. 注册 Twilio 账户: https://www.twilio.com/
2. 获取 WhatsApp Sandbox 凭证
3. 安装依赖:

```bash
pip install twilio
```

4. 配置:

```bash
export TWILIO_ACCOUNT_SID="your_account_sid"
export TWILIO_AUTH_TOKEN="your_auth_token"
export TWILIO_WHATSAPP_NUMBER="+1234567890"
```

## 💾 数据管理

### 查看使用统计

```bash
python3 -m enhancements.data_management.analytics
```

### 导出分析报告

```bash
python3 -c "
from enhancements.data_management import UsageAnalytics
analytics = UsageAnalytics()
analytics.export_report()
"
```

## 🎨 视频模板

### 使用预设模板

```bash
# TikTok 热门格式
./auto_clip.sh "VIDEO_URL" --preset tiktok_viral

# Instagram Reels
./auto_clip.sh "VIDEO_URL" --preset instagram_reel

# YouTube Shorts
./auto_clip.sh "VIDEO_URL" --preset youtube_short
```

### 添加视频效果

```bash
# 复古效果
./auto_clip.sh "VIDEO_URL" --effect vintage

# 加速 2 倍
./auto_clip.sh "VIDEO_URL" --effect speed_2x

# 黑白
./auto_clip.sh "VIDEO_URL" --effect grayscale
```

## 🔧 配置文件

创建 `~/.openfang/enhancements_config.json`:

```json
{
  "ai_providers": {
    "stt": {
      "default": "local_whisper",
      "groq_whisper": {
        "api_key_env": "GROQ_API_KEY"
      }
    },
    "tts": {
      "default": "edge_tts"
    }
  },
  "social_publishing": {
    "telegram": {
      "enabled": true,
      "bot_token_env": "TELEGRAM_BOT_TOKEN",
      "default_chat_id": "@your_channel"
    }
  }
}
```

## 📚 更多示例

查看 `examples/enhancements/` 目录中的示例代码：

```bash
# STT 示例
python3 examples/enhancements/stt_examples.py

# 社交发布示例
python3 examples/enhancements/social_publishing_examples.py

# 数据管理示例
python3 examples/enhancements/data_management_examples.py
```

## ❓ 常见问题

### Q: 如何选择 STT 提供商？

**A**:
- **本地使用/隐私优先**: Local Whisper
- **速度优先**: Groq Whisper
- **质量优先**: OpenAI Whisper

### Q: 免费使用？

**A**: 是的！以下组合完全免费：
- Local Whisper + Edge TTS
- 所有数据存储在本地
- 无需 API 密钥

### Q: 离线使用？

**A**: 使用以下组合：
- Local Whisper（STT）
- 本地 FFmpeg 处理
- 不启用社交发布

### Q: 如何获取 API 密钥？

**A**:
- Groq: https://console.groq.com/
- OpenAI: https://platform.openai.com/api-keys
- Deepgram: https://console.deepgram.com/
- ElevenLabs: https://elevenlabs.io/app/settings/api-keys

## 🆘 需要帮助？

- 查看故障排除指南: `docs/enhancements/TROUBLESHOOTING.md`
- 查看完整文档: `docs/enhancements/README.md`
- 提交 Issue: https://github.com/outhsics/openfang-auto-clip/issues

## 🎉 开始创作！

现在您已经准备好使用增强功能了！

```bash
# 处理您的第一个视频
./auto_clip.sh "https://www.youtube.com/watch?v=dQw4w9WgXcQ" \
  --stt groq_whisper \
  --preset tiktok_viral \
  --publish-telegram
```

祝您创作愉快！ 🎬
