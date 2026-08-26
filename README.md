# OpenFang Auto Clip

本地优先的短视频出片 CLI：长视频进，带字幕的 9:16 短片出。MIT。

不上传你的素材。不按条收费。中文和英文都能切。

```bash
pip install -e .
openfang clip "https://www.youtube.com/watch?v=VIDEO_ID" --transcript talk.srt
# 或本地文件
openfang clip lecture.mp4 --transcript lecture.srt --duration 45
```

输出：`~/.openfang/clips/clips/<时间戳>/clip_01_....mp4`

没有现成字幕时，加 `--transcribe` 会走本机 Whisper（慢，但不出网）。

## 和竞品差在哪

| | OpenFang | Opus Clip / Vizard | autoclip 等开源切片 |
|---|---|---|---|
| 出片 | 本地 9:16 + 烧字幕 | 云端，按分钟/条收费 | 本地 9:16 + 字幕 |
| 隐私 | 素材不出机器 | 要上传 | 本地 |
| 中文 | 按中文 hook 选片 | 英文产品为主 | 英文为主 |
| 版权安全重建 | 规划中（v0.7 要真正渲出视频） | 切原片 | 切原片 |

## 今天能用 / 还不能用

| 能力 | 状态 |
|---|---|
| `openfang clip` 出 9:16 带字幕 MP4 | 可用（v0.6） |
| 用 SRT/VTT 选 hook，而不是均分切片 | 可用 |
| Level 1 视觉混音 | 可用，旧 CLI：`python auto_clip.py URL --transform 1` |
| Level 2 脚本包 | 只出 JSON/Markdown，**还不是视频** |
| Level 3 完全重建 | 未实现 |
| 说话人跟踪 / 卡拉 OK 逐词字幕 | 还没有 |
| 托管 SaaS / 手机 App | 不做 |

环境：Python 3.9+，[ffmpeg](https://ffmpeg.org/)（需要能烧字幕的 build），yt-dlp 用于下载。

更细的路线看 [ROADMAP.md](ROADMAP.md)。英文：[README_EN.md](README_EN.md)。
