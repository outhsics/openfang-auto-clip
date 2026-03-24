# AIGC 集成指南 / AIGC Integration Guide

[English](#english) | 简体中文

---

## 简体中文

OpenFang Auto Clip 现已集成 AIGC (AI Generated Content) 功能，支持 AI 图像和视频生成。

### 功能特性

- **AI 图像生成**: 使用 Stable Diffusion、DALL-E、Replicate 等生成图像
- **AI 视频生成**: 从文本提示生成视频片段
- **多种风格预设**: 电影感、动漫、写实、赛博朋克等
- **批量生成**: 一次生成多个变体
- **图像动画**: 将静态图像转换为动态视频

### 支持的 AI 提供商

| 提供商 | 图像生成 | 视频生成 | 说明 |
|--------|----------|----------|------|
| **Stable Diffusion** | ✅ | ✅ | 本地部署，免费 |
| **OpenAI DALL-E** | ✅ | ❌ | 需要付费 API |
| **Replicate** | ✅ | ✅ | 支持多种模型 |
| **LibLib.tv** | ✅ | ❌ | 国内 AI 艺术平台 |
| **ComfyUI** | ✅ | ✅ | 节点式工作流 |

### 快速开始

#### 1. 安装依赖

```bash
# 基础依赖（已包含）
pip install -r requirements.txt

# 可选：安装特定提供商依赖
pip install openai  # DALL-E
pip install replicate  # Replicate
pip install pillow opencv-python  # 图像/视频处理
```

#### 2. 配置 AI 提供商

**使用 Stable Diffusion (推荐，免费)**

```bash
# 下载并启动 Stable Diffusion WebUI
git clone https://github.com/AUTOMATIC1111/stable-diffusion-webui
cd stable-diffusion-webui
./webui.sh --api  # Linux/Mac
# 或 webui.bat --api  # Windows

# WebUI 将在 http://127.0.0.1:7860 启动
```

**使用 OpenAI DALL-E**

```bash
# 设置 API Key
export OPENAI_API_KEY="your-api-key-here"

# 或保存到配置文件
echo '{"openai_dalle": {"api_key": "your-key", "enabled": true}}' > ~/.openfang/aigc_providers.json
```

**使用 ComfyUI**

```bash
# 下载 ComfyUI
git clone https://github.com/comfyanonymous/ComfyUI
cd ComfyUI
# 安装依赖后启动
python main.py --enable-cors-header "*"

# ComfyUI 将在 http://127.0.0.1:8188 启动
```

#### 3. 生成图像

**命令行使用**

```bash
# 使用 Stable Diffusion 生成图像
python3 -m src.aigc.image_generator \
    --prompt "一只可爱的猫咪在花园里" \
    --style cinematic \
    --width 1024 --height 1024

# 生成多个变体
python3 -m src.aigc.image_generator \
    --prompt "未来城市景观" \
    --variations 4 \
    --style cyberpunk

# 使用预设
python3 -m src.aigc.image_generator \
    --preset youtube_thumbnail \
    --customizations "prompt=震撼的科技缩略图"
```

**Python API**

```python
from src.aigc import generate_image, ImageStyle

# 基础生成
result = generate_image(
    prompt="美丽的日落海滩",
    provider="stable_diffusion",
    style="cinematic",
    width=1920,
    height=1080
)

if result["success"]:
    print(f"图像已保存: {result['save_path']}")

# 使用图像生成器类
from src.aigc import ImageGenerator

generator = ImageGenerator()

result = generator.generate(
    prompt="赛博朋克风格的街道",
    negative_prompt="模糊, 低质量",
    style=ImageStyle.CYBERPUNK,
    steps=30,
    guidance_scale=8.0
)

# 批量生成
prompts = [
    "山景日出",
    "森林小径",
    "海浪拍岸"
]

results = generator.generate_batch(prompts, style=ImageStyle.REALISTIC)

# 生成变体
variations = generator.generate_variations(
    base_prompt="一个神秘城堡",
    num_variations=4
)
```

#### 4. 生成视频

**命令行使用**

```bash
# 生成短视频
python3 -m src.aigc.video_generator \
    --prompt "云层在山间流动" \
    --duration 4.0 \
    --fps 30

# 生成循环视频
python3 -m src.aigc.video_generator \
    --prompt "抽象渐变动画" \
    --style loop \
    --duration 5.0

# 使用预设（社交媒体竖屏）
python3 -m src.aigc.video_generator \
    --preset social_short \
    --prompt "时尚产品展示"
```

**Python API**

```python
from src.aigc import generate_video, VideoGenerator

# 基础视频生成
result = generate_video(
    prompt="花朵绽放的延时摄影",
    provider="stable_diffusion",
    duration=4.0,
    fps=30
)

if result["success"]:
    print(f"视频已保存: {result['save_path']}")

# 使用视频生成器类
generator = VideoGenerator()

result = generator.generate(
    prompt="未来城市飞行器",
    duration=6.0,
    style=VideoStyle.SCI_FI
)

# 图像转视频
result = generator.image_to_video(
    image_path="input.jpg",
    motion_prompt="缓慢缩放和旋转",
    duration=5.0,
    motion_strength=0.6
)

# 多场景视频生成
script = "这是一段关于自然的视频"
scenes = [
    "森林阳光透过树叶",
    "溪水流过岩石",
    "鸟儿飞过天空"
]

result = generator.text_to_video(
    script=script,
    scene_descriptions=scenes,
    output_path="nature_video.mp4",
    transition="fade"
)
```

### 风格预设

#### 图像风格

| 风格 | 描述 | 适用场景 |
|------|------|----------|
| `realistic` | 照片级真实 | 产品展示、人像 |
| `anime` | 动漫风格 | 动漫内容、角色 |
| `oil_painting` | 油画风格 | 艺术创作 |
| `watercolor` | 水彩风格 | 唯美场景 |
| `cyberpunk` | 赛博朋克 | 科技内容 |
| `fantasy` | 奇幻风格 | 游戏内容 |
| `cinematic` | 电影感 | 视频素材 |
| `vintage` | 复古风格 | 怀旧内容 |

#### 视频风格

| 风格 | 描述 | 适用场景 |
|------|------|----------|
| `cinematic` | 电影质感 | 专业视频 |
| `anime` | 动漫动画 | 动漫内容 |
| `realistic` | 真实感 | 纪录片风格 |
| `loop` | 无缝循环 | 背景视频 |
| `slow_motion` | 慢动作 | 特效镜头 |
| `timelapse` | 延时摄影 | 时间流逝 |

### 高级功能

#### 自定义工作流 (ComfyUI)

```python
from src.aigc import get_provider

# 获取 ComfyUI 提供商
provider = get_provider("comfyui", base_url="http://127.0.0.1:8188")

# 使用自定义工作流
custom_workflow = {
    "1": {
        "class_type": "KSampler",
        "inputs": {
            "seed": 12345,
            "steps": 30,
            "cfg": 8,
            # ... 更多节点配置
        }
    }
}

result = provider.generate_image(
    prompt="自定义提示词",
    workflow=custom_workflow
)
```

#### 批量处理

```python
from src.aigc import ImageGenerator

generator = ImageGenerator()

# 批量生成
prompts = [f"场景 {i+1}" for i in range(10)]
results = generator.generate_batch(
    prompts,
    style="cinematic",
    width=1920,
    height=1080
)

# 查看生成历史
history = generator.get_history(limit=20)
for item in history:
    print(f"{item['timestamp']}: {item['prompt']}")
```

### 集成到视频处理流程

```python
from src.aigc import generate_image, generate_video
from src.auto_clip import process_video

# 生成自定义封面图
cover = generate_image(
    prompt="震撼的电影级缩略图",
    preset="youtube_thumbnail"
)

# 生成背景视频
bg_video = generate_video(
    prompt="抽象渐变背景",
    style="loop",
    duration=10.0
)

# 使用 AIGC 内容处理视频
process_video(
    input_url="source_video.mp4",
    cover_image=cover["save_path"],
    background_video=bg_video["save_path"],
    # ... 其他参数
)
```

### 故障排查

#### Stable Diffusion 连接失败

```
错误: Cannot connect to Stable Diffusion API
解决:
1. 确认 WebUI 正在运行: http://127.0.0.1:7860
2. 启动时添加 --api 参数: ./webui.sh --api
3. 检查防火墙设置
```

#### 生成速度慢

```
问题: 图像/视频生成时间过长
解决:
1. 降低 steps 参数 (默认 20，可降至 15)
2. 减小分辨率 (1024x1024 → 512x512)
3. 使用更快的模型 (sd_base → sd_turbo)
4. 启用 GPU 加速
```

#### 内存不足

```
错误: CUDA out of memory
解决:
1. 减小批次大小
2. 降低分辨率
3. 使用更小的模型
4. 关闭其他应用程序
```

### 配置文件

创建 `~/.openfang/aigc_providers.json`:

```json
{
  "default_provider": "stable_diffusion",
  "providers": {
    "stable_diffusion": {
      "base_url": "http://127.0.0.1:7860",
      "api_key": null,
      "enabled": true,
      "model": "sd_xl_base_1.0"
    },
    "openai_dalle": {
      "api_key": "your-openai-key",
      "enabled": false,
      "model": "dall-e-3"
    },
    "replicate": {
      "api_key": "your-replicate-key",
      "enabled": false,
      "model": "stability-ai/sdxl"
    },
    "comfyui": {
      "base_url": "http://127.0.0.1:8188",
      "enabled": false
    }
  }
}
```

### 最佳实践

1. **预览优先**: 先用低分辨率/少步数测试效果
2. **保存配置**: 将成功的参数保存为预设
3. **批量处理**: 使用批量功能提高效率
4. **风格一致**: 同一项目使用相同风格参数
5. **定期清理**: 清理生成历史释放磁盘空间

### 示例项目

**生成视频缩略图**

```python
from src.aigc import ImageGenerator, ImageStyle

generator = ImageGenerator()

thumbnail = generator.generate(
    prompt="科技产品特写，明亮背景，专业摄影",
    style=ImageStyle.CINEMATIC,
    width=1280,
    height=720,
    steps=25
)

print(f"缩略图: {thumbnail['save_path']}")
```

**生成背景素材**

```python
from src.aigc import VideoGenerator, VideoStyle

generator = VideoGenerator()

background = generator.generate_loop(
    prompt="抽象几何图形缓慢移动",
    duration=15.0,
    fps=30
)

print(f"背景视频: {background['save_path']}")
```

---

## English

OpenFang Auto Clip now includes AIGC (AI Generated Content) integration for AI-powered image and video generation.

### Features

- **AI Image Generation**: Generate images using Stable Diffusion, DALL-E, Replicate, etc.
- **AI Video Generation**: Create video clips from text prompts
- **Style Presets**: Cinematic, anime, realistic, cyberpunk, and more
- **Batch Generation**: Generate multiple variations at once
- **Image Animation**: Convert static images to motion videos

### Supported AI Providers

| Provider | Image Gen | Video Gen | Notes |
|----------|-----------|-----------|-------|
| **Stable Diffusion** | ✅ | ✅ | Local deployment, free |
| **OpenAI DALL-E** | ✅ | ❌ | Requires paid API |
| **Replicate** | ✅ | ✅ | Multiple models available |
| **LibLib.tv** | ✅ | ❌ | Chinese AI art platform |
| **ComfyUI** | ✅ | ✅ | Node-based workflow |

### Quick Start

#### 1. Install Dependencies

```bash
# Base dependencies (already included)
pip install -r requirements.txt

# Optional: Install provider-specific dependencies
pip install openai  # DALL-E
pip install replicate  # Replicate
pip install pillow opencv-python  # Image/video processing
```

#### 2. Configure AI Provider

**Using Stable Diffusion (Recommended, Free)**

```bash
# Download and launch Stable Diffusion WebUI
git clone https://github.com/AUTOMATIC1111/stable-diffusion-webui
cd stable-diffusion-webui
./webui.sh --api  # Linux/Mac
# or webui.bat --api  # Windows

# WebUI will start at http://127.0.0.1:7860
```

**Using OpenAI DALL-E**

```bash
# Set API Key
export OPENAI_API_KEY="your-api-key-here"

# Or save to config file
echo '{"openai_dalle": {"api_key": "your-key", "enabled": true}}' > ~/.openfang/aigc_providers.json
```

#### 3. Generate Images

**Command Line**

```bash
# Generate image with Stable Diffusion
python3 -m src.aigc.image_generator \
    --prompt "A cute cat in a garden" \
    --style cinematic \
    --width 1024 --height 1024

# Generate multiple variations
python3 -m src.aigc.image_generator \
    --prompt "Futuristic cityscape" \
    --variations 4 \
    --style cyberpunk
```

**Python API**

```python
from src.aigc import generate_image, ImageStyle

# Basic generation
result = generate_image(
    prompt="Beautiful sunset beach",
    provider="stable_diffusion",
    style="cinematic",
    width=1920,
    height=1080
)

if result["success"]:
    print(f"Image saved: {result['save_path']}")
```

#### 4. Generate Videos

```python
from src.aigc import generate_video, VideoGenerator

# Basic video generation
result = generate_video(
    prompt="Clouds flowing over mountains",
    provider="stable_diffusion",
    duration=4.0,
    fps=30
)

# Generate looping video
generator = VideoGenerator()
loop_video = generator.generate_loop(
    prompt="Abstract gradient animation",
    duration=5.0
)
```

### Style Presets

#### Image Styles

| Style | Description | Use Case |
|-------|-------------|----------|
| `realistic` | Photorealistic | Product shots, portraits |
| `anime` | Anime style | Anime content |
| `cinematic` | Movie quality | Video assets |
| `cyberpunk` | Cyberpunk | Tech content |
| `vintage` | Retro style | Nostalgic content |

#### Video Styles

| Style | Description | Use Case |
|-------|-------------|----------|
| `cinematic` | Cinematic quality | Professional videos |
| `loop` | Seamless loop | Background videos |
| `slow_motion` | Slow motion | Effect shots |
| `timelapse` | Timelapse | Time passage |

### Troubleshooting

**Stable Diffusion connection failed:**
```
1. Ensure WebUI is running: http://127.0.0.1:7860
2. Launch with --api flag: ./webui.sh --api
3. Check firewall settings
```

**Slow generation:**
```
1. Reduce steps (default 20 → 15)
2. Lower resolution (1024 → 512)
3. Use faster model (sd_turbo)
4. Enable GPU acceleration
```

### Configuration File

Create `~/.openfang/aigc_providers.json`:

```json
{
  "default_provider": "stable_diffusion",
  "providers": {
    "stable_diffusion": {
      "base_url": "http://127.0.0.1:7860",
      "enabled": true,
      "model": "sd_xl_base_1.0"
    },
    "openai_dalle": {
      "api_key": "your-key",
      "enabled": false
    }
  }
}
```

### Best Practices

1. **Preview first**: Test with low resolution/steps
2. **Save configs**: Save successful parameters as presets
3. **Batch processing**: Use batch features for efficiency
4. **Style consistency**: Use same style for same project
5. **Regular cleanup**: Clear history to free disk space
