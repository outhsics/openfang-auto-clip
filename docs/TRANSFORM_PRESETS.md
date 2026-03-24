# 转换效果预设指南 / Transform Effect Presets Guide

[English](#english) | 简体中文

---

## 简体中文

OpenFang Auto Clip 提供多种预设效果，让你快速应用不同的视觉风格。

### 基础预设 / Basic Presets

| 预设 | 描述 | 保护级别 | 速度 |
|------|------|----------|------|
| `default` | 平衡的版权保护和画质 | 高 | 1.15x |
| `mild` | 轻微改变，保持原貌 | 低 | 1.05x |
| `strong` | 最大版权保护 | 很高 | 1.25x |

### 风格预设 / Style Presets

| 预设 | 描述 | 适用场景 |
|------|------|----------|
| `cinematic` | 电影感色彩分级 | 影视解说 |
| `retro` | 90年代 VHS 风格 | 怀旧内容 |
| `cyberpunk` | 霓虹未来感 | 科技内容 |
| `vintage` | 老电影棕褐色调 | 历史内容 |
| `noir` | 黑白黑色电影风格 | 悬疑/推理 |

### 社交媒体预设 / Social Media Presets

| 预设 | 描述 | 平台优化 |
|------|------|----------|
| `tiktok` | 快节奏、高饱和度 | TikTok |
| `instagram` | 干净、美学风格 | Instagram Reels |
| `youtube` | 平衡风格 | YouTube Shorts |

### 情绪预设 / Mood Presets

| 预设 | 描述 | 情绪 |
|------|------|------|
| `dramatic` | 高对比度、强烈情绪 | 戏剧性 |
| `dreamy` | 柔和、梦幻 | 梦幻 |
| `intense` | 大胆、引人注目 | 激烈 |

### 使用方法

#### 命令行使用

```bash
# 使用预设
python3 auto_clip.py "URL" --preset cinematic

# 查看所有预设
python3 auto_clip.py --list-presets

# 按类别查看
python3 auto_clip.py --list-presets --category style
```

#### Python API

```python
from src.transform_effects import apply_preset

# 应用预设
apply_preset(
    input_path="input.mp4",
    output_path="output.mp4",
    preset_name="cinematic"
)
```

### 创建自定义预设

编辑 `config/transform_presets.json`:

```json
{
  "custom_presets": {
    "my_preset": {
      "name": "My Preset",
      "description": "My custom effect",
      "video_filter": "scale=1920:1080,hflip,eq=contrast=1.2",
      "audio_filter": "atempo=1.15",
      "speed_factor": 1.15,
      "protection_level": "high"
    }
  }
}
```

### 预览效果

```bash
# 生成预览（前 10 秒）
python3 auto_clip.py "URL" --preset cinematic --preview-duration 10
```

---

## English

OpenFang Auto Clip provides various preset effects for quickly applying different visual styles.

### Basic Presets

| Preset | Description | Protection Level | Speed |
|--------|-------------|------------------|-------|
| `default` | Balanced protection and quality | High | 1.15x |
| `mild` | Subtle changes, maintains original | Low | 1.05x |
| `strong` | Maximum copyright protection | Very High | 1.25x |

### Style Presets

| Preset | Description | Use Case |
|--------|-------------|----------|
| `cinematic` | Movie-like color grading | Film commentary |
| `retro` | 90s VHS style | Nostalgic content |
| `cyberpunk` | Neon, futuristic | Tech content |
| `vintage` | Old film sepia | Historical content |
| `noir` | B&W film noir | Mystery/suspense |

### Social Media Presets

| Preset | Description | Platform Optimized |
|--------|-------------|-------------------|
| `tiktok` | Fast-paced, vibrant | TikTok |
| `instagram` | Clean, aesthetic | Instagram Reels |
| `youtube` | Balanced style | YouTube Shorts |

### Mood Presets

| Preset | Description | Mood |
|--------|-------------|------|
| `dramatic` | High contrast, intense | Dramatic |
| `dreamy` | Soft, ethereal | Dreamy |
| `intense` | Bold, attention-grabbing | Intense |

### Usage

#### Command Line

```bash
# Use a preset
python3 auto_clip.py "URL" --preset cinematic

# List all presets
python3 auto_clip.py --list-presets

# List by category
python3 auto_clip.py --list-presets --category style
```

#### Python API

```python
from src.transform_effects import apply_preset

# Apply preset
apply_preset(
    input_path="input.mp4",
    output_path="output.mp4",
    preset_name="cinematic"
)
```

### Create Custom Presets

Edit `config/transform_presets.json`:

```json
{
  "custom_presets": {
    "my_preset": {
      "name": "My Preset",
      "description": "My custom effect",
      "video_filter": "scale=1920:1080,hflip,eq=contrast=1.2",
      "audio_filter": "atempo=1.15",
      "speed_factor": 1.15,
      "protection_level": "high"
    }
  }
}
```

### Preview Effects

```bash
# Generate preview (first 10 seconds)
python3 auto_clip.py "URL" --preset cinematic --preview-duration 10
```

### Technical Details

Each preset consists of:

- **video_filter**: FFmpeg video filter chain
- **audio_filter**: FFmpeg audio filter chain
- **speed_factor**: Playback speed adjustment
- **protection_level**: Copyright protection strength

### Best Practices

1. **Test first**: Use `--preview-duration` to test presets
2. **Match content**: Choose preset that fits your content style
3. **Platform optimization**: Use social media presets for specific platforms
4. **Customize**: Create custom presets for your brand

### Examples

```bash
# Cinematic movie explanation
python3 auto_clip.py "MOVIE_URL" --preset cinematic --transform 1

# Retro gaming content
python3 auto_clip.py "GAMEPLAY_URL" --preset retro --transform 1

# TikTok tech video
python3 auto_clip.py "TECH_URL" --preset tiktok --transform 1 --duration 30

# Dreamy travel montage
python3 auto_clip.py "TRAVEL_URL" --preset dreamy --transform 1
```

### Troubleshooting

**Preset not found:**
```bash
# List available presets
python3 auto_clip.py --list-presets
```

**Effect too strong:**
```bash
# Use milder preset
python3 auto_clip.py "URL" --preset mild
```

**Effect not visible:**
```bash
# Use stronger preset
python3 auto_clip.py "URL" --preset strong
```

### Performance Tips

1. **Preview first**: Always test with short preview
2. **GPU acceleration**: Use FFmpeg with CUDA for faster processing
3. **Batch processing**: Apply same preset to multiple videos
4. **Cache results**: Save transformed videos for reuse
