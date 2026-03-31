# 🎬 OpenFang Auto Clip

**The Fully Customizable, Local-First Video Automation Pipeline**

[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](LICENSE)
[![Python 3.9+](https://img.shields.io/badge/python-3.9+-blue.svg)](https://www.python.org/downloads/)
[![CI](https://github.com/outhsics/openfang-auto-clip/actions/workflows/ci.yml/badge.svg)](https://github.com/outhsics/openfang-auto-clip/actions/workflows/ci.yml)
[![GitHub Stars](https://img.shields.io/github/stars/outhsics/openfang-auto-clip?style=social)](https://github.com/outhsics/openfang-auto-clip/stargazers)


[English](README_EN.md) | 简体中文

---

## ⚡ 30-Second Quick Start

```bash
# Clone & install (one command)
git clone https://github.com/outhsics/openfang-auto-clip.git && \
cd openfang-auto-clip && pip install -e .

# Run quick demo - see results in 5 seconds (no video download needed!)
python3 auto_clip.py --quick-demo

# Process your first video
./auto_clip.sh "https://www.youtube.com/watch?v=VIDEO_ID" --transform 1
```

**Output:** `~/.openfang/clips/clips/TIMESTAMP/`

---

## 🎯 Why OpenFang?

### The Problem with SaaS Video Tools

| Challenge | SaaS Tools | OpenFang Auto Clip |
|-----------|-----------|-------------------|
| **Privacy** | ❌ Upload your content to cloud | ✅ Everything stays on your machine |
| **Cost** | 💰 $20-100/month + API fees | ✅ 100% free, MIT licensed |
| **Customization** | ❌ Limited to their features | ✅ Full Python + FFmpeg control |
| **API Limits** | 💸 Pay per use | ✅ No API costs for most features |
| **Data Ownership** | ⚠️ Locked into their platform | ✅ Your data, your workflow |
| **Offline** | ❌ Requires internet | ✅ Works completely offline |

### What Makes Us Different

**🔧 Fully Customizable**
- Unlike black-box SaaS tools, you have complete control
- Extend with custom FFmpeg filters
- Integrate any Python library
- Modify the pipeline to fit your needs

**🏠 Local-First Architecture**
- Your videos never leave your machine
- No API keys required for most features
- Works offline after initial setup
- Complete privacy and data ownership

**📊 Production-Ready Features**
- Reproducible benchmark system
- Bilingual documentation (EN/ZH)
- Synthetic demos (no external media needed)
- Enterprise-ready CLI and Web UI

---

## 60 秒判断值不值得看

- 先看项目状态快照：[PROJECT_STATUS.md](PROJECT_STATUS.md)
- 先跑不依赖外部素材的 benchmark：[examples/benchmark/README_ZH.md](examples/benchmark/README_ZH.md)
- 先看完整评估路径索引：[examples/evaluation/README_ZH.md](examples/evaluation/README_ZH.md)
- 直接看已提交的本地评估快照：[examples/evaluation/sample_local_evaluation_report.md](examples/evaluation/sample_local_evaluation_report.md)
- 看一次真实输出结构示例：[examples/demo/README_ZH.md](examples/demo/README_ZH.md)
- 直接看已提交的 Level 2 样例产物：[examples/demo/level2_samples/README_ZH.md](examples/demo/level2_samples/README_ZH.md)
- 看可复用的 launch / demo 场景：[examples/showcases/README_ZH.md](examples/showcases/README_ZH.md)
- 看转换能力边界：[docs/TRANSFORMATION_ZH.md](docs/TRANSFORMATION_ZH.md)
- 看开源增长计划：[OPEN_SOURCE_PLAN.md](OPEN_SOURCE_PLAN.md)
- 以后让别的 AI 接手时先看：[AI_CONTEXT.md](AI_CONTEXT.md)

## 这个仓库今天已经能做什么

- 用 `yt-dlp` 下载源视频
- 跑一个可用的本地 Level 1 FFmpeg 视觉混音路径
- 在提供 transcript 的前提下生成一个带时间锚点、shot plan、asset request、voiceover note 和 review rubric 的 Level 2 脚本再生包
- 用仓库自带 transcript 直接生成一个自包含的 Level 2 demo 包，方便首次评估
- 对已有 Level 2 脚本包生成双语 review report，方便人工验收
- 运行一个可复现的中英双语 Level 2 demo suite，比较脚本包结构质量并验证多种 transcript 格式
- 一条命令跑完本地评估链路：doctor、benchmark、Level 2 suite
- 按简单本地策略切成 9:16 短视频片段
- 提供 `--doctor` 和 `--dry-run` 方便先验环境与流程
- 提供本地 Web 管理界面做任务启动和查看
- 提供 synthetic benchmark、release 素材和 social preview 生成脚本
- synthetic benchmark 会额外输出双语 `benchmark_summary.md`

## Reality Check / 现状说明

| Area | 状态 | 说明 |
|------|------|------|
| 下载 + 切片导出 | 可用 | 当前主 CLI 路径 |
| Level 1 视觉混音 | 可用 | FFmpeg 本地可复现 |
| Web 管理器 | 可用 | 本地操作台，不是 SaaS |
| Synthetic benchmark | 可用 | 无需外部素材 |
| Social preview / release 素材 | 可用 | 已有脚本 |
| Level 2 脚本重写 | 部分可用 | 已能生成 transcript-to-script 包、shot plan 和 blueprint，但还不能自动重建成片 |
| Level 3 完全重制 | 脚手架 | 还不是生产能力 |
| Hosted SaaS / 公共 API | 不提供 | 当前定位是 local-first |

## 快速开始

```bash
git clone https://github.com/outhsics/openfang-auto-clip.git
cd openfang-auto-clip

python3 -m venv .venv
source .venv/bin/activate
pip install -e .

# Quick demo (5 seconds, no download needed!)
python3 auto_clip.py --quick-demo

# Check environment
./auto_clip.sh --doctor

# Run benchmark
python3 scripts/run_demo_benchmark.py

# Process your first video
./auto_clip.sh "https://www.youtube.com/watch?v=VIDEO_ID" --transform 1
```

如果你想用仓库自带安装脚本，见 [docs/INSTALLATION_ZH.md](docs/INSTALLATION_ZH.md)。

## 常用命令

```bash
# 检查本地环境
./auto_clip.sh --doctor

# 只生成执行计划，不下载媒体
./auto_clip.sh "URL" --dry-run

# 运行 synthetic benchmark
python3 scripts/run_demo_benchmark.py

# 运行零外部素材的 Level 2 demo
python3 auto_clip.py --demo-script-package

# 复查一个已生成的 Level 2 脚本包
python3 auto_clip.py --review-package ~/.openfang/clips/script_packages/TIMESTAMP_source

# 运行中英双语 Level 2 demo suite
python3 scripts/run_level2_demo_suite.py

# 一条命令跑完整个本地评估链路
python3 scripts/run_local_evaluation.py

# 刷新仓库里已提交的 demo / benchmark 样例资产
python3 scripts/refresh_demo_assets.py

# 基于 transcript 生成 Level 2 脚本包
./auto_clip.sh "URL" --transform 2 --transcript path/to/source.srt

# 生成 GitHub social preview 图
python3 scripts/generate_social_preview.py --report examples/benchmark/sample_benchmark_report.json --lang zh

# 生成带 benchmark 证据的 release bundle
python3 scripts/release_prep.py v0.3.0 --report tmp/demo-benchmark-v030/benchmark_report.json

# 启动本地 Web 管理器
./start_web_manager.sh

# 运行测试
python3 -m unittest discover -s tests
```

## 文档入口

- [DOCUMENTATION_ZH.md](DOCUMENTATION_ZH.md)
- [docs/INSTALLATION_ZH.md](docs/INSTALLATION_ZH.md)
- [docs/TRANSFORMATION_ZH.md](docs/TRANSFORMATION_ZH.md)
- [docs/SOCIAL_PREVIEW_ZH.md](docs/SOCIAL_PREVIEW_ZH.md)
- [docs/VERSIONING_ZH.md](docs/VERSIONING_ZH.md)
- [PROJECT_STATUS.md](PROJECT_STATUS.md)
- [OPEN_SOURCE_PLAN.md](OPEN_SOURCE_PLAN.md)
- [AI_CONTEXT.md](AI_CONTEXT.md)

## 对外定位

更准确的说法是：

- 一个本地优先的 operator workflow
- 一个可复现 benchmark 和 clip generation 仓库
- 一个今天已经能跑通 Level 1 的工具
- 一个已经交付 Level 2 第一阶段脚本包、但还没完成成片重建的项目

不应该继续这样说：

- 保证版权安全
- 已经是完整 SaaS
- Level 2 / 3 已经商业级可交付

## 支持与社区

- Bug： [GitHub Issues](https://github.com/outhsics/openfang-auto-clip/issues)
- 使用问题：看 [SUPPORT_ZH.md](SUPPORT_ZH.md)
- 安全问题：看 [SECURITY.md](SECURITY.md)
- 贡献方式：看 [CONTRIBUTING.md](CONTRIBUTING.md)

## License

仓库使用 MIT 许可证。涉及商业化或高风险使用前，请同时阅读 [LICENSE](LICENSE) 和 [DISCLAIMER.md](DISCLAIMER.md)。

---

## 🚀 v0.5.0 增强功能

### 🎤 多种 AI 提供商支持

**语音识别 (STT)**
- **Groq Whisper** - ⚡ 超快速，部分免费
- **OpenAI Whisper** - 🎵 高质量，付费
- **Deepgram** - 🚀 专业级，付费
- **Local Whisper** - 🏠 完全离线，免费

**语音合成 (TTS)**
- **Edge TTS** - 💰 完全免费，多语言
- **OpenAI TTS** - 🎵 高质量，付费
- **ElevenLabs** - 🎤 专业级，付费

```bash
# 使用 Groq Whisper（最快）
./auto_clip.sh "VIDEO_URL" --stt groq_whisper

# 使用本地 Whisper（离线）
./auto_clip.sh "VIDEO_URL" --stt local_whisper

# 使用 Edge TTS（免费）
./auto_clip.sh "VIDEO_URL" --tts edge_tts
```

### 📱 社交平台一键发布

- **Telegram** - 自动发送到频道/群组
- **WhatsApp** - 发送到个人/群组

```bash
# 处理并自动发布
./auto_clip.sh "VIDEO_URL" --publish-telegram --publish-whatsapp
```

### 💾 本地数据管理

- **SQLite 数据库** - 存储任务历史和元数据
- **使用统计** - 查看处理历史和性能指标
- **自动清理** - 定期清理旧数据

```bash
# 查看使用统计
python3 -m enhancements.data_management.analytics

# 导出分析报告
python3 -m enhancements.data_management.analytics --export-report
```

### 🎨 视频模板和效果

**预设模板**
- TikTok 热门格式
- Instagram Reels
- YouTube Shorts
- 自定义模板

**视频效果**
- 颜色调整（亮度、对比度、饱和度）
- 速度控制（加速/减速）
- 艺术效果（复古、黑白、模糊等）
- 变换效果（翻转、旋转）

```bash
# 使用 TikTok 预设
./auto_clip.sh "VIDEO_URL" --preset tiktok_viral

# 添加复古效果
./auto_clip.sh "VIDEO_URL" --effect vintage
```

### 🔒 隐私和安全

- ✅ 所有数据存储在本地
- ✅ API 密钥不会上传
- ✅ 可离线使用（本地模式）
- ✅ 无数据追踪
- ✅ 开源透明

---

