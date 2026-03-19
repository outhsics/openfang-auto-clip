# Level 2 样例产物

这些已提交到仓库的产物由内置 transcript fixture 生成。
它们让访客不用先跑 CLI，也能直接查看真实的 Level 2 输出结果。

- 生成时间：2026-03-19T11:46:42

## 样例列表

### 英文样例
- 语言：en
- 评审状态：可进入人工审阅
- 评审得分：100/100
- Transcript fixture：`examples/demo/sample_level2_transcript.srt`
- 脚本包：`examples/demo/level2_samples/en/script_package.json`
- 脚本草稿：`examples/demo/level2_samples/en/script_draft.md`
- Blueprint：`examples/demo/level2_samples/en/production_blueprint.json`
- 评审 JSON：`examples/demo/level2_samples/en/review_report.json`
- 评审 Markdown：`examples/demo/level2_samples/en/review_report.md`

### 中文样例
- 语言：zh
- 评审状态：可进入人工审阅
- 评审得分：100/100
- Transcript fixture：`examples/demo/sample_level2_transcript_zh.srt`
- 脚本包：`examples/demo/level2_samples/zh/script_package.json`
- 脚本草稿：`examples/demo/level2_samples/zh/script_draft.md`
- Blueprint：`examples/demo/level2_samples/zh/production_blueprint.json`
- 评审 JSON：`examples/demo/level2_samples/zh/review_report.json`
- 评审 Markdown：`examples/demo/level2_samples/zh/review_report.md`

## 说明

- 如需刷新这些产物，运行 `python3 scripts/export_level2_demo_samples.py`。
- 如果你想要带时间戳的实时产物，请直接使用 CLI 输出到 `~/.openfang/clips/script_packages/`。
