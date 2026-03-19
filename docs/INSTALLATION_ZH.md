# 安装指南

## 环境要求

- Python `3.9+`
- `ffmpeg`
- `yt-dlp`
- 如果要使用 OpenFang Agent OS 工作流，需要 `OpenFang 0.1.9+`

## 快速安装

```bash
git clone https://github.com/outhsics/openfang-auto-clip.git
cd openfang-auto-clip
./scripts/install.sh
```

安装脚本会自动：

- 检查 Python、FFmpeg 和 OpenFang
- 在 `~/.openfang/venv` 创建虚拟环境
- 安装 Python 依赖
- 创建 `~/.openfang/clips`、`~/.openfang/downloads`、`~/.openfang/logs`
- 将默认配置复制到 `~/.openfang/auto_clip_config.json`

## 手动安装

```bash
python3 -m venv ~/.openfang/venv
source ~/.openfang/venv/bin/activate
pip install --upgrade pip
pip install -r requirements.txt
```

如果缺少 `ffmpeg`：

```bash
# macOS
brew install ffmpeg

# Ubuntu / Debian
sudo apt-get update
sudo apt-get install -y ffmpeg
```

## 验证安装

```bash
./auto_clip.sh --doctor
python3 scripts/run_local_evaluation.py
./auto_clip.sh "https://www.youtube.com/watch?v=VIDEO_ID" --dry-run
./auto_clip.sh --help
python3 -m unittest discover -s tests
```

## 关键路径

- 配置文件：`~/.openfang/auto_clip_config.json`
- 下载目录：`~/.openfang/clips/downloads/`
- 输出目录：`~/.openfang/clips/<timestamp>/`
- Web 任务状态：`~/.openfang/web_tasks.json`
