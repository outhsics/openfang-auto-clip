# 🔧 增强功能故障排除指南

## 常见问题及解决方案

### 🎤 AI 提供商相关问题

#### Groq Whisper 速度慢或失败

**症状**: Groq Whisper 响应很慢或返回错误

**解决方案**:

1. 检查 API 密钥:
```bash
echo $GROQ_API_KEY
```

2. 验证 API 密钥是否有效:
```python
import groq
client = groq.Groq(api_key="your_api_key")
# 如果出错，密钥无效
```

3. 检查网络连接:
```bash
curl -I https://api.groq.com
```

4. 如果遇到速率限制，考虑使用 Local Whisper 作为备选

#### Local Whisper 下载模型失败

**症状**: 首次使用时下载模型失败

**解决方案**:

1. 检查网络连接
2. 手动下载模型:

```bash
# 设置镜像（中国大陆用户）
export HF_ENDPOINT=https://hf-mirror.com

# 预下载模型
python3 -c "import whisper; whisper.load_model('base')"
```

3. 使用更小的模型:
```python
# 使用 tiny 模型（最快，但准确度较低）
stt = LocalWhisperSTT(model_size="tiny")
```

#### OpenAI API 认证失败

**症状**: `openai.AuthenticationError`

**解决方案**:

1. 检查 API 密钥格式:
```bash
# 应该以 sk- 开头
echo $OPENAI_API_KEY
```

2. 重新设置密钥:
```bash
export OPENAI_API_KEY="sk-..."
```

3. 验证密钥:
```python
import openai
client = openai.OpenAI(api_key="your_api_key")
try:
    client.models.list()
    print("✅ 密钥有效")
except:
    print("❌ 密钥无效")
```

### 📱 社交平台发布问题

#### Telegram Bot 无法发送消息

**症状**: Bot 创建成功但无法发送消息

**解决方案**:

1. 确保 Bot 已被添加到频道/群组
2. 检查 Bot 权限:
   - 在频道中，Bot 必须是管理员
   - 在群组中，Bot 必须有发送消息权限

3. 验证 chat_id:
```python
import asyncio
from telegram import Bot

async def check_bot():
    bot = Bot(token="your_bot_token")
    updates = await bot.get_updates()
    for update in updates:
        print(f"Chat ID: {update.message.chat_id}")

asyncio.run(check_bot())
```

4. 使用正确的 chat_id 格式:
   - 频道: `@channelname` 或 `-100xxxxxxxxxx`
   - 群组: `-100xxxxxxxxxx`
   - 私聊: 数字 ID

#### WhatsApp pywhatkit 发送失败

**症状**: pywhatkit 无法发送消息

**解决方案**:

1. 确保手机上已打开 WhatsApp Web
2. 检查电话号码格式（带国家代码）:
```python
# 正确: +8613800138000
# 错误: 13800138000
```

3. 增加等待时间:
```python
import pywhatkit
import time

pywhatkit.sendwhatmsg_instantly(
    phone_no="+8613800138000",
    message="测试消息",
    wait_time=15,  # 增加等待时间
    tab_close=True
)
```

4. 考虑使用 Twilio API（更稳定）

### 💾 数据管理问题

#### SQLite 数据库锁定

**症状**: `sqlite3.OperationalError: database is locked`

**解决方案**:

1. 确保没有其他进程正在使用数据库
2. 增加超时时间:
```python
import sqlite3

conn = sqlite3.connect(
    "database.db",
    timeout=30.0  # 增加到 30 秒
)
```

3. 使用 WAL 模式:
```python
conn.execute("PRAGMA journal_mode=WAL")
```

#### 数据库文件损坏

**症状**: 无法读取数据库

**解决方案**:

1. 备份数据库:
```bash
cp ~/.openfang/tasks.db ~/.openfang/tasks.db.backup
```

2. 尝试修复:
```bash
sqlite3 ~/.openfang/tasks.db "PRAGMA integrity_check;"
```

3. 如果损坏严重，删除并重建:
```bash
rm ~/.openfang/tasks.db
# 下次使用时会自动创建
```

### 🎬 视频处理问题

#### FFmpeg 未找到

**症状**: `ffmpeg: command not found`

**解决方案**:

**macOS**:
```bash
brew install ffmpeg
```

**Ubuntu/Debian**:
```bash
sudo apt update
sudo apt install ffmpeg
```

**Windows**:
1. 下载: https://ffmpeg.org/download.html
2. 添加到 PATH

#### 视频处理速度慢

**症状**: 处理视频需要很长时间

**解决方案**:

1. 使用硬件加速（如果可用）:
```bash
# NVIDIA GPU
ffmpeg -hwaccel cuda -i input.mp4 output.mp4

# macOS (VideoToolbox)
ffmpeg -hwaccel videotoolbox -i input.mp4 output.mp4
```

2. 降低质量设置:
```python
preset = VideoPreset(
    ...
    crf=28,  # 增加到 28（质量更低，速度更快）
    preset="fast"  # 使用 faster 或 ultrafast
)
```

3. 考虑使用更快的 STT 提供商（Groq Whisper）

### 🔧 配置问题

#### 环境变量未生效

**症状**: 设置的环境变量无法读取

**解决方案**:

1. 检查是否已设置:
```bash
echo $GROQ_API_KEY
```

2. 永久设置环境变量:

**bash/zsh**:
```bash
echo 'export GROQ_API_KEY="your_key"' >> ~/.bashrc
source ~/.bashrc
```

**fish**:
```bash
echo 'set -x GROQ_API_KEY "your_key"' >> ~/.config/fish/config.fish
```

3. 使用 `.env` 文件:
```bash
# 在项目目录创建 .env
echo 'GROQ_API_KEY=your_key' > .env

# 使用 python-dotenv 加载
pip install python-dotenv
```

#### 配置文件格式错误

**症状**: JSON 解析错误

**解决方案**:

1. 验证 JSON 格式:
```bash
python3 -m json.tool ~/.openfang/enhancements_config.json
```

2. 使用配置模板:
```bash
cp config/enhancements_config.example.json ~/.openfang/enhancements_config.json
```

### 🌐 网络问题

#### 连接超时

**症状**: API 请求超时

**解决方案**:

1. 检查网络连接:
```bash
ping -c 3 api.groq.com
```

2. 增加超时时间:
```python
stt = GroqWhisperSTT()
result = stt.transcribe(
    audio_path,
    timeout=60  # 增加到 60 秒
)
```

3. 使用代理（如果在中国大陆）:
```bash
export HTTP_PROXY="http://127.0.0.1:7890"
export HTTPS_PROXY="http://127.0.0.1:7890"
```

#### API 速率限制

**症状**: `RateLimitError` 或 `429 Too Many Requests`

**解决方案**:

1. 等待一段时间后重试
2. 使用多个 API 密钥轮换
3. 考虑升级到付费计划
4. 使用本地模型（Local Whisper）作为备选

### 📦 依赖问题

#### pip 安装失败

**症状**: `pip install` 失败

**解决方案**:

1. 更新 pip:
```bash
pip install --upgrade pip
```

2. 使用国内镜像（中国大陆）:
```bash
pip install -i https://pypi.tuna.tsinghua.edu.cn/simple package_name
```

3. 使用 conda（如果 pip 失败）:
```bash
conda install -c conda-forge openai-whisper
```

#### 依赖冲突

**症状**: `ModuleNotFoundError` 或版本冲突

**解决方案**:

1. 使用虚拟环境:
```bash
python3 -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
```

2. 检查依赖:
```bash
pip list
pip check
```

3. 重新安装:
```bash
pip uninstall package_name
pip install package_name
```

### 🆘 获取帮助

如果以上解决方案都无法解决您的问题：

1. **查看日志**:
```bash
# 启用详细日志
export OPENFANG_LOG_LEVEL=DEBUG
./auto_clip.sh "VIDEO_URL"
```

2. **运行诊断**:
```bash
./auto_clip.sh --doctor
```

3. **查看示例**:
```bash
python3 examples/enhancements/stt_examples.py
```

4. **提交 Issue**:
   - GitHub: https://github.com/outhsics/openfang-auto-clip/issues
   - 包含错误信息和系统信息

5. **联系社区**:
   - 查看文档: `docs/enhancements/README.md`
   - 查看示例: `examples/enhancements/`

### 📝 调试技巧

#### 启用调试日志

```python
import logging

logging.basicConfig(level=logging.DEBUG)
```

#### 测试单个功能

```python
# 测试 STT
from enhancements.ai_providers import get_stt_provider
stt = get_stt_provider("local_whisper")
result = stt.transcribe("test_audio.mp3")
print(result.text)
```

#### 检查环境

```bash
# Python 版本
python3 --version

# 依赖检查
pip list | grep -E "groq|openai|whisper"

# 环境变量
env | grep -E "API_KEY|TOKEN"
```

---

**提示**: 大多数问题都可以通过查看错误消息和日志来解决。确保仔细阅读完整的错误堆栈跟踪！
