# 转换能力说明

本文档说明 OpenFang Auto Clip 当前的转换路径，以及哪些能力已经可用，哪些还只是路线图。

## 当前状态

| Level | 状态 | 说明 |
|------|------|------|
| 1 | 可用 | 基于 FFmpeg 的本地视觉混音 |
| 2 | 部分可用 | 已交付 transcript-to-script 脚本包，完整重建成片还没有实现 |
| 3 | 脚手架 | 完全重制仍然是概念路径 |

## Level 1

Level 1 是当前最成熟、最值得对外展示的转换路径。

它目前会做的事情包括：

- 镜像处理
- 节奏和速度调整
- 颜色、对比度等视觉变化
- 其他基于 FFmpeg 的画面处理

适用场景：

- 快速做本地 remix
- 跑可复现 demo
- 相比直接搬运，走一个更低风险的处理路径

示例命令：

```bash
./auto_clip.sh "URL" --transform 1
```

重要边界：

- 这不是法律意见
- 这不会自动消除商标、角色 IP 或音乐版权风险
- 不应把它宣传成“保证安全”

## Level 2

Level 2 现在已经有了第一阶段的可运行里程碑。

当前这一步能做的是：

1. 读取 transcript 或字幕文件
2. 提取源内容的关键段落
3. 生成一份新的讲述结构草稿
4. 输出 JSON + Markdown 脚本包供人工审阅

示例命令：

```bash
./auto_clip.sh "URL" --transform 2 --transcript path/to/source.srt
```

当前状态：

- CLI 现在可以生成 transcript-to-script 脚本包
- 脚本包包含 source outline、narration draft 和 production checklist
- 新配音、重建视觉素材和最终成片仍然需要后续人工或其他工具完成

## Level 3

Level 3 是完全重制方向的路线图能力。

目标链路是：

1. 分析原素材结构和目标
2. 生成原创脚本
3. 生成新的视觉、音频和节奏
4. 合成独立成片

当前状态：

- 仍是概念阶段
- 不适合做生产承诺
- 不适合做商业能力宣传

## 怎么选

- 本地评估：用 Level 1
- 做产品 demo：用 Level 1 加 synthetic benchmark
- 做脚本再生第一阶段：用 Level 2
- 讨论未来路线：用 Level 3

## 合规建议

- 把这个项目理解成降低风险的工程工具，不是法律护身符
- 发布前先看平台规则
- 商业化或高风险场景请单独做法律评估
- 对外表述前请先阅读 [DISCLAIMER.md](../DISCLAIMER.md)
