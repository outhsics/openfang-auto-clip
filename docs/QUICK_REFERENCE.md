# 快速参考手册 / Quick Reference Guide

[English](#english) | 简体中文

---

## 简体中文

### 安装

```bash
git clone https://github.com/outhsics/openfang-auto-clip.git
cd openfang-auto-clip
pip install -e .
```

### 基础命令

```bash
# 环境检查
./auto_clip.sh --doctor

# 下载并转换视频
./auto_clip.sh "URL" --transform 1

# 批量处理
python3 auto_clip.py --batch-file urls.txt --parallel 2

# AIGC 图像生成
python3 auto_clip.py --aigc-image "提示词" --style cinematic

# AIGC 视频生成
python3 auto_clip.py --aigc-video "提示词" --duration 4.0
```

### Python API

```python
# 基础使用
from src.aigc import generate_image

result = generate_image(
    prompt="美丽的风景",
    style="cinematic"
)

# Agent 技能
from src.agent_skills import Agent

agent = Agent("my_agent")
agent.add_skill("video_download")
agent.add_skill("video_transform")

result = agent.execute("video_download", {
    "url": "https://youtube.com/watch?v=VIDEO_ID"
})
```

### 常用参数

| 参数 | 描述 | 默认值 |
|------|------|--------|
| `--transform` | 转换级别 (0-3) | 1 |
| `--duration` | 片段时长（秒） | 60 |
| `--preset` | 转换预设 | default |
| `--parallel` | 并行进程数 | 1 |
| `--batch-file` | 批量文件 | - |

### 转换预设

| 预设 | 风格 |
|------|------|
| `default` | 平衡 |
| `cinematic` | 电影感 |
| `retro` | 复古 |
| `cyberpunk` | 赛博朋克 |
| `tiktok` | TikTok 优化 |

### AIGC 风格

| 风格 | 描述 |
|------|------|
| `cinematic` | 电影感 |
| `anime` | 动漫 |
| `cyberpunk` | 赛博朋克 |
| `realistic` | 写实 |
| `vintage` | 复古 |

### 输出位置

```
~/.openfang/
├── clips/           # 处理后的视频
├── downloads/       # 下载的视频
├── aigc/           # AIGC 生成内容
│   ├── images/     # AI 图像
│   └── videos/     # AI 视频
└── transcripts/    # 字幕文件
```

### 故障排查

| 问题 | 解决方案 |
|------|----------|
| FFmpeg 未找到 | `brew install ffmpeg` 或 `apt install ffmpeg` |
| 下载失败 | 检查网络或使用代理 |
| 内存不足 | 降低并行数或分辨率 |
| AIGC 连接失败 | 确认 SD WebUI 正在运行 |

### 获取帮助

- 📖 [完整文档](README.md)
- 💬 [GitHub Discussions](https://github.com/outhsics/openfang-auto-clip/discussions)
- 🐛 [报告问题](https://github.com/outhsics/openfang-auto-clip/issues)

---

## English

### Installation

```bash
git clone https://github.com/outhsics/openfang-auto-clip.git
cd openfang-auto-clip
pip install -e .
```

### Basic Commands

```bash
# Environment check
./auto_clip.sh --doctor

# Download and transform video
./auto_clip.sh "URL" --transform 1

# Batch processing
python3 auto_clip.py --batch-file urls.txt --parallel 2

# AIGC image generation
python3 auto_clip.py --aigc-image "prompt" --style cinematic

# AIGC video generation
python3 auto_clip.py --aigc-video "prompt" --duration 4.0
```

### Python API

```python
# Basic usage
from src.aigc import generate_image

result = generate_image(
    prompt="Beautiful landscape",
    style="cinematic"
)

# Agent skills
from src.agent_skills import Agent

agent = Agent("my_agent")
agent.add_skill("video_download")
agent.add_skill("video_transform")

result = agent.execute("video_download", {
    "url": "https://youtube.com/watch?v=VIDEO_ID"
})
```

### Common Parameters

| Parameter | Description | Default |
|-----------|-------------|---------|
| `--transform` | Transform level (0-3) | 1 |
| `--duration` | Clip duration (seconds) | 60 |
| `--preset` | Transform preset | default |
| `--parallel` | Parallel workers | 1 |
| `--batch-file` | Batch file | - |

### Transform Presets

| Preset | Style |
|--------|-------|
| `default` | Balanced |
| `cinematic` | Cinematic |
| `retro` | Retro |
| `cyberpunk` | Cyberpunk |
| `tiktok` | TikTok optimized |

### AIGC Styles

| Style | Description |
|-------|-------------|
| `cinematic` | Cinematic |
| `anime` | Anime |
| `cyberpunk` | Cyberpunk |
| `realistic` | Realistic |
| `vintage` | Vintage |

### Output Locations

```
~/.openfang/
├── clips/           # Processed videos
├── downloads/       # Downloaded videos
├── aigc/           # AIGC content
│   ├── images/     # AI images
│   └── videos/     # AI videos
└── transcripts/    # Subtitle files
```

### Troubleshooting

| Issue | Solution |
|-------|----------|
| FFmpeg not found | `brew install ffmpeg` or `apt install ffmpeg` |
| Download failed | Check network or use proxy |
| Out of memory | Reduce parallel workers or resolution |
| AIGC connection failed | Ensure SD WebUI is running |

### Get Help

- 📖 [Full Documentation](README_EN.md)
- 💬 [GitHub Discussions](https://github.com/outhsics/openfang-auto-clip/discussions)
- 🐛 [Report Issues](https://github.com/outhsics/openfang-auto-clip/issues)
