# PR #3 — 真实素材端到端验证

验证日期：2026-09-08。被测业务代码：`79b95931906e967f39c4e4c8772284a3c9fffa53`。
本次只补验证记录与复现工具，没有修复或更改出片逻辑。

**结论：真实素材能生成 45 秒、9:16、烧录字幕的 MP4；不能据此将字幕功能整体判为通过。密集对白存在稳定复现的漏字幕缺陷。**

## 素材和环境

- 视频：[Tears of Steel 720p MOV](https://download.blender.org/demo/movies/ToS/tears_of_steel_720p.mov)，372,178,639 bytes，734.166667 秒。
- 字幕：[原始英文 SRT](https://download.blender.org/demo/movies/ToS/subtitles/TOS-en.srt)。未编造对白、未人工调整时间轴。
- 署名：**(CC) Blender Foundation | mango.blender.org**；影片 [CC BY 3.0 授权说明](https://mango.blender.org/sharing/)。本地成片为裁剪、缩放、补黑边并烧录字幕的技术验证衍生片段。
- macOS 26.5.2 / Apple Silicon；出片 Python 3.14.7、Pillow 12.2.0；FFmpeg/ffprobe 9.0.1（ffmpeg-full，含 libass/subtitles、libx264）；审计工具 Python 3.12.13 + NumPy。
- 实测入口是 `python3 auto_clip.py clip` + 下载后的本地 MOV；不代表 YouTube/yt-dlp URL 入口、Whisper 转录、无 libass 的 PNG 回退、中文或安装后的 console entry point 已通过。

输入 SHA-256：

```text
video efa9062d9cdb7a338e40ad530dfdf234806743f29ae6a1a136b97ece4e588e8f
srt   ce9578f6fe098a5821045a38884b229160f9e7ba27890448a92f5be330c6e6fe
```

## 复现命令

在 PR 分支的仓库根目录执行；`RUN` 放在仓库外，避免提交原片、成片、虚拟环境或缓存。依赖安装需要联网。

```bash
git fetch origin feat/v0.6-clip-path
git switch feat/v0.6-clip-path
git rev-parse HEAD
# 被测业务版本为 79b9593；后续验证文档提交不改变业务代码。
RUN="$(mktemp -d /tmp/openfang-pr3.XXXXXX)"
python3 -m venv "$RUN/venv"
"$RUN/venv/bin/pip" install Pillow==12.2.0 numpy
PY="$RUN/venv/bin/python"
ffmpeg -version
ffmpeg -hide_banner -filters | rg ' subtitles '
curl -Lf --retry 2 \
  https://download.blender.org/demo/movies/ToS/tears_of_steel_720p.mov \
  -o "$RUN/source.mov"
curl -Lf --retry 2 \
  https://download.blender.org/demo/movies/ToS/subtitles/TOS-en.srt \
  -o "$RUN/TOS-en.srt"
shasum -a 256 "$RUN/source.mov" "$RUN/TOS-en.srt"
"$PY" auto_clip.py clip "$RUN/source.mov" \
  --transcript "$RUN/TOS-en.srt" --duration 45 --max-clips 1 --out "$RUN/main"

# 密集对白：仅筛选原字幕中 356 <= start < 395 的真实条目，保留原片时间轴。
"$PY" - "$RUN/TOS-en.srt" "$RUN/dense.srt" <<'PY'
import sys
from pathlib import Path
from auto_clip import build_transcript_payload
from src.clip_pipeline import write_srt
segments = build_transcript_payload(Path(sys.argv[1]))['segments']
write_srt([s for s in segments if 356 <= s['start'] < 395], Path(sys.argv[2]))
PY
"$PY" auto_clip.py clip "$RUN/source.mov" \
  --transcript "$RUN/dense.srt" --duration 45 --max-clips 1 --out "$RUN/dense"

"$PY" docs/validation/audit_real_clip.py "$RUN/source.mov" "$RUN/main" "$RUN/dense"
# macOS 可选：原生解码器验证（使用系统 Swift/AVFoundation）。
swift docs/validation/decode_mp4_macos.swift "$RUN/main/clip_01_0016s-0061s.mp4"
"$PY" -m unittest tests.test_clip_pipeline tests.test_auto_clip_cli
```

审计脚本会写入 `ffprobe.json` 和 `audit.json`，并执行 FFmpeg 全片严格解码。它专用于本次 24 fps、底部留黑的 Tears of Steel 素材，利用字幕区域像素检查显示区间和各条字幕中点，不是通用 OCR 或任意视频的字幕验收器。字幕缺失以 `visible: false` 记录，脚本退出 0 不表示所有字幕通过。

## 主片实测

| 检查 | 结果 |
| --- | --- |
| 自动选段 | 原片 16.650–61.650 秒 |
| 文件 | `clip_01_0016s-0061s.mp4`，6,881,213 bytes |
| 时长 | 容器、视频、音频均 45.000000 秒，均从 0 开始 |
| 视频 | 1080×1920，DAR 9:16，SAR 1:1，24 fps，1080 帧 |
| 编码 | H.264 High / Level 4.0 / `avc1` / `yuv420p`；AAC-LC、44.1 kHz、立体声 |
| 烧录 | 无软字幕轨；11/11 条在各自中点有字幕像素，ASS 11 条；抽帧检查文字可见、未越出画面 |
| 文件兼容性 | FFmpeg `-v error -xerror` 全片解码无错误；AVFoundation 解码 1080 视频帧、281 PCM 音频缓冲，status=2/completed、error=nil |
| 快速起播 | `moov` 位于 byte 32，早于 byte 35997 的 `mdat` |
| 现有测试 | `tests.test_clip_pipeline` + `tests.test_auto_clip_cli`，16 tests，OK |

主片 SHA-256：`5ec4c2d405ad76032a1625835e309c27477df928f1957cfff4b883e9eed471bf`。
编码器版本/线程等环境变化可能影响输出哈希；输入哈希和媒体参数是复现比对的主要依据。

### 字幕同步检查

逐帧分析全部 1080 帧的底部字幕区域：第一条 SRT 为 6.350–7.850 秒，实际字幕像素区间为 `[6.375, 7.875)`；第 4 条开始于 14.166667 秒（SRT 14.150）；第 10 条为 `[33.375, 36.875)`（SRT 33.350–36.850）。非相邻字幕边界最大偏差 33.334 ms，小于 24 fps 的一帧 41.667 ms。相邻无空隙字幕的像素区间会合并，不以此声称逐字 OCR 校验。

音频按原片选段起点 16.650 秒提取参考 PCM，与成片在 6、20、34 秒处各取 2 秒进行 ±100 ms 互相关；三处最佳延迟均为 0.000 ms，相关系数分别为 0.999299、0.999661、0.998836。结合 SRT 减去选段起点及逐帧结果，未发现流水线引入的整体声画/字幕时轴偏移。

这证明的是保留原素材与上游字幕的同步关系，不是对白转录准确性或人工逐句听审。尝试独立 Whisper 校验时模型下载遇到 TLS 连接错误，未将其计为通过。也未实测浏览器、手机设备或社交平台上传兼容性。

## 发现的问题

### P1：第 13 条及以后的字幕被静默丢弃

`src/clip_pipeline.py` 的 `burn_clip()` 在解析后使用 `[:12]`；该限制在 libass 和 PNG 回退分支之前。

上述密集对白复现自动选择原片 349.750–394.750 秒：成片同样 45 秒，生成的 SRT 有 15 条，ASS 只有 12 条；第 13/14/15 条在成片 38.250/39.750/42.000 秒抽帧均无字幕像素。缺失区间分别为 37.250–39.250、39.250–40.250、40.750–43.250 秒。任务仍退出 0，report 未提示截断。

建议移除无提示的条数上限；如 PNG 路径存在资源限制，应显式报错或采用不会丢字的分批渲染。增加超过 12 条字幕的真实时序回归断言，不能仅检查文件存在或尺寸。

密集片 SHA-256：`f44d5e1447a81e2f906db6b41c56ff112f7e74862faa3a24158e03152de4cc7f`。

### P2：输出字幕时间轴越过成片结束，结尾对白被截断

主片最后一条字幕在 SRT/ASS 中是 44.350–46.350 秒，而文件仅 45 秒。画面实际只显示 `[44.375, 45.000)`，原字幕剩余 1.35 秒随片尾被切掉。`run_clip_job()` 平移字幕时没有将 end 裁到 clip_duration，选段也不对齐句子边界。

建议至少将导出字幕限制到 `[0, duration]`；如要求完整句子，应另外调整窗口选择策略，在固定 45 秒约束下避免切断对白。单纯裁 SRT end 不会恢复被切掉的语音。

### 画面表现：9:16 画布通过，但主体为居中横屏加黑边

抽查 6.2、6.5、15、34、44.6 秒及密集片 39 秒。当前 `scale(...decrease)+pad` 保留横屏构图，大片上下黑边，字幕靠画布底部、距离主体较远。技术上是 9:16，但不等价于满屏竖向重构；属于当前产品表现，不应在验收描述中称为人像跟踪或满屏裁剪。

## 证据

- [主片逐帧/音轨审计 JSON](pr3-main-audit.json)
- [密集对白审计 JSON](pr3-dense-audit.json)
- [可复现审计脚本](audit_real_clip.py)
- [macOS 原生解码检查](decode_mp4_macos.swift)

视频、原始素材、模型/依赖缓存和运行日志保留在本地交付目录，不提交大文件到 Git。PR 仍需处理上述字幕缺陷后才能宣称完整验收通过。
