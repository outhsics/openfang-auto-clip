# 🚀 OpenFang Auto Clip - 个人创作者增强版

## 📋 增强功能总览

本目录包含面向个人创作者的增强功能，所有功能都遵循 **Local-First** 原则。

### 🎯 设计原则

1. **Local-First** - 所有数据存储在本地，不上传云端
2. **简单易用** - 保持现有 CLI 和 Web UI 的简洁性
3. **可选增强** - 所有增强功能都是可选的，不影响核心功能
4. **隐私优先** - 用户数据完全掌控
5. **免费开源** - MIT 许可证，无隐藏费用

### 📁 目录结构

```
enhancements/
├── README.md                    # 本文档
├── ai_providers/               # AI 服务提供商集成
│   ├── __init__.py
│   ├── stt_providers.py       # 语音识别（STT）提供商
│   ├── tts_providers.py       # 语音合成（TTS）提供商
│   └── base.py                # 基础接口
├── social_publishing/          # 社交平台自动发布
│   ├── __init__.py
│   ├── telegram.py            # Telegram 发布
│   ├── whatsapp.py            # WhatsApp 发布
│   └── base.py                # 基础接口
├── data_management/           # 本地数据管理
│   ├── __init__.py
│   ├── database.py            # SQLite 数据库
│   ├── cache.py               # 本地缓存
│   └── analytics.py           # 使用统计
└── templates/                 # 视频模板和效果
    ├── __init__.py
    ├── presets.py             # 预设模板
    └── effects.py             # 特效库
```

### 🚀 快速开始

#### 1. 安装增强功能

```bash
# 基础安装（无额外依赖）
pip install -e .

# 完整安装（包含所有增强功能）
pip install -e .[ai,social,analytics]
```

#### 2. 配置 AI 提供商

```bash
# 复制配置模板
cp config/example_config.json ~/.openfang/enhancements_config.json

# 编辑配置，添加 API 密钥
# 所有密钥都存储在本地，不会上传
```

#### 3. 使用增强功能

```bash
# 使用多种 STT 选项
./auto_clip.sh "VIDEO_URL" --stt groq_whisper
./auto_clip.sh "VIDEO_URL" --stt openai_whisper
./auto_clip.sh "VIDEO_URL" --stt local_whisper

# 自动发布到社交平台
./auto_clip.sh "VIDEO_URL" --publish-telegram --publish-whatsapp

# 查看使用统计
python3 -m enhancements.data_management.analytics
```

### 🎤 AI 提供商

#### 语音识别 (STT)

| 提供商 | 费用 | 速度 | 质量 | 离线 |
|--------|------|------|------|------|
| Groq Whisper | 免费（有限） | ⚡ 最快 | ✅ 优秀 | ❌ |
| OpenAI Whisper | 💰 付费 | 🚀 快 | ✅ 优秀 | ❌ |
| Deepgram | 💰 付费 | ⚡ 快 | ✅ 优秀 | ❌ |
| Local Whisper | 免费 | 🐢 慢 | ✅ 良好 | ✅ |

#### 语音合成 (TTS)

| 提供商 | 费用 | 音质 | 语言 | 情感 |
|--------|------|------|------|------|
| Edge TTS | 免费 | ✅ 良好 | 🌍 多语言 | ❌ |
| OpenAI TTS | 💰 付费 | 🎵 优秀 | 🌍 多语言 | ✅ |
| ElevenLabs | 💰 付费 | 🎵 专业 | 🌍 多语言 | ✅ |

### 📱 社交平台发布

支持的平台：
- **Telegram** - 自动发送到频道/群组
- **WhatsApp** - 发送到个人/群组
- **更多平台开发中...**

### 💾 本地数据管理

- **SQLite 数据库** - 存储任务历史和元数据
- **本地缓存** - 加速重复处理
- **使用统计** - 查看处理历史和性能指标

### 🎨 视频模板

预设热门短视频格式：
- TikTok 热门效果
- Instagram Reels 模板
- YouTube Shorts 格式
- 自定义模板

### 🔒 隐私和安全

- ✅ 所有数据存储在本地
- ✅ API 密钥不会上传
- ✅ 可离线使用（本地模式）
- ✅ 无数据追踪
- ✅ 开源透明

### 📚 更多文档

- [AI 提供商配置指南](ai_providers/README.md)
- [社交平台发布教程](social_publishing/README.md)
- [数据管理说明](data_management/README.md)
- [视频模板库](templates/README.md)

### 🤝 贡献

欢迎提交 Issue 和 Pull Request！

### 📄 许可证

MIT License - 与主项目保持一致
