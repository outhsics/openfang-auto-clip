# Demo 走查

这个目录给第一次评估项目的人提供一个轻量级、无需复杂准备的示例说明。

## 它展示什么

- 真正的 CLI 入口
- 一次成功运行后会生成怎样的目录结构
- 下游运营或发布流程可以消费的报告格式

## 推荐命令

```bash
./auto_clip.sh "https://www.youtube.com/watch?v=VIDEO_ID" --transform 1 --duration 45
python3 auto_clip.py --demo-script-package
python3 auto_clip.py --review-package ~/.openfang/clips/script_packages/TIMESTAMP_source
python3 scripts/run_level2_demo_suite.py
```

Level 2 demo 命令会直接使用仓库内置的 `sample_level2_transcript.srt`，无需下载媒体素材，也能产出可审阅的脚本包。
review 命令会刷新 `review_report.json` 和 `review_report.md`，输出面向人工验收的双语检查结果。
suite 命令会同时跑仓库内置的中英 transcript，并输出 `level2_demo_suite_report.json` 和 `level2_demo_suite_report.md`。

## 期望输出结构

```text
~/.openfang/clips/
├── downloads/
│   └── source_video.mp4
└── 20260307_120000/
    ├── clip_01_0000s-0045s.mp4
    ├── clip_02_0045s-0090s.mp4
    ├── clip_03_0090s-0135s.mp4
    └── report.json
```

## 示例报告

参见 [`sample_report.json`](sample_report.json)。

这个示例是合成数据，目的是让项目评估者在快速浏览仓库时，也能理解产出结构，而不需要真的下载媒体素材。
