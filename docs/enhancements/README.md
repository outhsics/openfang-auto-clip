# 📚 增强功能文档

欢迎来到 OpenFang Auto Clip 增强功能文档！

## 🎯 什么是增强功能？

增强功能是为个人创作者设计的一系列可选功能，在保持 **Local-First** 和 **隐私优先** 的基础上，提供更多强大的能力：

- 🎤 **多种 AI 提供商** - Groq、OpenAI、Deepgram、Local Whisper
- 📱 **社交平台发布** - Telegram、WhatsApp 一键发布
- 💾 **本地数据管理** - 任务历史、使用统计
- 🎨 **视频模板和效果** - 预设模板、特效库

## 🚀 快速开始

### 新手推荐

1. 阅读 [快速开始指南](QUICKSTART.md)
2. 运行配置向导: `python3 scripts/setup_enhancements.py`
3. 查看示例代码: `examples/enhancements/`

### 已有经验

直接跳转到您需要的文档：
- [AI 提供商配置](#ai-提供商)
- [社交平台发布](#社交平台发布)
- [数据管理](#数据管理)
- [视频模板](#视频模板)

## 📖 文档目录

### 入门指南

- **[快速开始指南](QUICKSTART.md)** - 5 分钟快速上手
- **[故障排除指南](TROUBLESHOOTING.md)** - 常见问题解决方案
- **[配置向导使用](#配置向导)** - 交互式配置工具

### 功能文档

#### AI 提供商

- **[语音识别 (STT)](AI_PROVIDERS.md#stt)** - 4 种 STT 提供商详解
- **[语音合成 (TTS)](AI_PROVIDERS.md#tts)** - 3 种 TTS 提供商详解
- **[提供商对比](AI_PROVIDERS.md#comparison)** - 速度、质量、费用对比

#### 社交平台发布

- **[Telegram 发布](SOCIAL_PUBLISHING.md#telegram)** - Telegram Bot 配置和使用
- **[WhatsApp 发布](SOCIAL_PUBLISHING.md#whatsapp)** - 两种发布方式详解
- **[批量发布](SOCIAL_PUBLISHING.md#batch)** - 多平台同时发布

#### 数据管理

- **[本地数据库](DATA_MANAGEMENT.md#database)** - SQLite 数据库使用
- **[使用统计](DATA_MANAGEMENT.md#analytics)** - 分析和报告
- **[配置管理](DATA_MANAGEMENT.md#config)** - 配置存储和读取

#### 视频模板

- **[预设模板](VIDEO_TEMPLATES.md#presets)** - TikTok、Instagram、YouTube 预设
- **[视频效果](VIDEO_TEMPLATES.md#effects)** - 颜色、速度、艺术效果
- **[自定义模板](VIDEO_TEMPLATES.md#custom)** - 创建自己的模板

### 示例代码

查看 `examples/enhancements/` 目录：

- **[STT 示例](../examples/enhancements/stt_examples.py)** - 语音识别使用示例
- **[社交发布示例](../examples/enhancements/social_publishing_examples.py)** - 社交平台发布示例
- **[数据管理示例](../examples/enhancements/data_management_examples.py)** - 数据管理使用示例

## 🎓 使用场景

### 场景 1: 完全离线使用

适合：隐私敏感、无网络环境

```bash
# 安装依赖
pip install openai-whisper

# 使用
./auto_clip.sh "VIDEO_URL" --stt local_whisper
```

优点：
- ✅ 完全离线
- ✅ 数据不上传
- ✅ 无需 API 密钥
- ✅ 完全免费

### 场景 2: 速度优先

适合：需要快速处理大量视频

```bash
# 安装依赖
pip install groq

# 配置
export GROQ_API_KEY="your_key"

# 使用
./auto_clip.sh "VIDEO_URL" --stt groq_whisper
```

优点：
- ✅ 超快速（比本地快 10 倍+）
- ✅ 部分免费
- ✅ 高准确度

### 场景 3: 质量优先

适合：专业制作、需要最高质量

```bash
# 配置 OpenAI
export OPENAI_API_KEY="your_key"

# 使用最佳组合
./auto_clip.sh "VIDEO_URL" \
  --stt openai_whisper \
  --tts openai_tts \
  --preset cinematic
```

优点：
- ✅ 最高质量
- ✅ 专业级效果
- ✅ 多语言支持

### 场景 4: 自动化发布

适合：内容创作者、需要批量发布

```bash
# 配置 Telegram
export TELEGRAM_BOT_TOKEN="your_token"
export TELEGRAM_CHAT_ID="@your_channel"

# 处理并发布
./auto_clip.sh "VIDEO_URL" \
  --preset tiktok_viral \
  --publish-telegram \
  --publish-whatsapp
```

优点：
- ✅ 一键发布
- ✅ 多平台同步
- ✅ 节省时间

## 🔧 配置向导

使用交互式配置向导：

```bash
python3 scripts/setup_enhancements.py
```

向导将引导您：
1. 选择默认 STT 提供商
2. 选择默认 TTS 提供商
3. 配置社交平台
4. 设置环境变量
5. 生成安装命令

## 📊 功能对比

### STT 提供商对比

| 提供商 | 速度 | 质量 | 费用 | 离线 | 推荐 |
|--------|------|------|------|------|------|
| Groq Whisper | ⚡⚡⚡ | ⭐⭐⭐ | 免费（有限） | ❌ | 速度优先 |
| OpenAI Whisper | ⚡⚡ | ⭐⭐⭐⭐ | 付费 | ❌ | 质量优先 |
| Deepgram | ⚡⚡⚡ | ⭐⭐⭐ | 付费 | ❌ | 专业使用 |
| Local Whisper | ⚡ | ⭐⭐⭐ | 免费 | ✅ | 隐私优先 |

### TTS 提供商对比

| 提供商 | 音质 | 语言 | 费用 | 离线 | 推荐 |
|--------|------|------|------|------|------|
| Edge TTS | ⭐⭐ | 🌍 多 | 免费 | ❌ | 日常使用 |
| OpenAI TTS | ⭐⭐⭐⭐ | 🌍 多 | 付费 | ❌ | 质量优先 |
| ElevenLabs | ⭐⭐⭐⭐⭐ | 🌍 多 | 付费 | ❌ | 专业制作 |

## 🎯 推荐组合

### 入门组合（免费）

```bash
# Local Whisper + Edge TTS
./auto_clip.sh "VIDEO_URL" \
  --stt local_whisper \
  --tts edge_tts
```

- 完全免费
- 可离线使用
- 适合新手

### 性能组合（快速）

```bash
# Groq Whisper + Edge TTS
./auto_clip.sh "VIDEO_URL" \
  --stt groq_whisper \
  --tts edge_tts
```

- 速度快
- 部分免费
- 适合批量处理

### 专业组合（最佳质量）

```bash
# OpenAI STT + TTS
./auto_clip.sh "VIDEO_URL" \
  --stt openai_whisper \
  --tts openai_tts \
  --preset cinematic
```

- 最高质量
- 专业级效果
- 适合商业使用

## 💡 最佳实践

### 1. 环境变量管理

使用 `.env` 文件：

```bash
# .env
GROQ_API_KEY=your_key
TELEGRAM_BOT_TOKEN=your_token
```

加载：

```python
from dotenv import load_dotenv
load_dotenv()
```

### 2. 错误处理

```python
from enhancements.ai_providers import auto_select_stt, ProviderNotAvailableError

try:
    stt = auto_select_stt()
    result = stt.transcribe(audio_path)
except ProviderNotAvailableError:
    print("没有可用的 STT 提供商")
except Exception as e:
    print(f"转录失败: {e}")
```

### 3. 配置管理

```python
from enhancements.data_management import get_database

db = get_database()

# 保存配置
db.set_config("default_stt", "groq_whisper")

# 读取配置
default_stt = db.get_config("default_stt", "local_whisper")
```

### 4. 批量处理

```python
from enhancements.ai_providers import get_stt_provider

stt = get_stt_provider("groq_whisper")

for audio_path in audio_files:
    result = stt.transcribe(audio_path)
    print(f"{audio_path}: {result.text[:50]}...")
```

## 🆘 获取帮助

### 文档

- [快速开始](QUICKSTART.md)
- [故障排除](TROUBLESHOOTING.md)
- [API 参考](API_REFERENCE.md)

### 示例

- `examples/enhancements/` - 代码示例
- `examples/showcases/` - 完整场景

### 社区

- GitHub Issues: https://github.com/outhsics/openfang-auto-clip/issues
- Discussions: https://github.com/outhsics/openfang-auto-clip/discussions

### 调试

```bash
# 启用调试日志
export OPENFANG_LOG_LEVEL=DEBUG

# 运行诊断
./auto_clip.sh --doctor

# 查看日志
tail -f ~/.openfang/logs/auto_clip.log
```

## 📈 路线图

### v0.5.0（当前）

- ✅ 多种 AI 提供商
- ✅ 社交平台发布
- ✅ 本地数据管理
- ✅ 视频模板和效果

### v0.6.0（计划中）

- ⏳ 更多 STT/TTS 提供商
- ⏳ 更多社交平台（Discord、Slack）
- ⏳ 高级视频效果
- ⏳ 批量处理优化

### v0.7.0（未来）

- ⏳ AI 内容建议
- ⏳ 自动标题生成
- ⏳ 热门趋势分析
- ⏳ Web UI 增强

## 🤝 贡献

欢迎贡献！

1. Fork 项目
2. 创建功能分支
3. 提交 Pull Request

查看 [贡献指南](../../CONTRIBUTING.md)

## 📄 许可证

MIT License - 与主项目一致

---

**开始使用**: [快速开始指南](QUICKSTART.md) 🚀
