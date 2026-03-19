# Level 2 样例产物

这些已提交到仓库的产物由内置 transcript fixture 生成。
它们让访客不用先跑 CLI，也能直接查看真实的 Level 2 输出结果。

- 生成时间：2026-03-19T14:37:11

## 样例列表

### 英文 SRT 样例
- 语言：en
- Transcript 格式：srt
- 评审状态：可进入人工审阅
- 评审得分：100/100
- Transcript fixture：`examples/demo/sample_level2_transcript.srt`
- 脚本包：`examples/demo/level2_samples/en/script_package.json`
- 脚本草稿：`examples/demo/level2_samples/en/script_draft.md`
- Blueprint：`examples/demo/level2_samples/en/production_blueprint.json`
- 交接 JSON：`examples/demo/level2_samples/en/operator_handoff.json`
- 评审 JSON：`examples/demo/level2_samples/en/review_report.json`
- 评审 Markdown：`examples/demo/level2_samples/en/review_report.md`

### 中文 SRT 样例
- 语言：zh
- Transcript 格式：srt
- 评审状态：可进入人工审阅
- 评审得分：100/100
- Transcript fixture：`examples/demo/sample_level2_transcript_zh.srt`
- 脚本包：`examples/demo/level2_samples/zh/script_package.json`
- 脚本草稿：`examples/demo/level2_samples/zh/script_draft.md`
- Blueprint：`examples/demo/level2_samples/zh/production_blueprint.json`
- 交接 JSON：`examples/demo/level2_samples/zh/operator_handoff.json`
- 评审 JSON：`examples/demo/level2_samples/zh/review_report.json`
- 评审 Markdown：`examples/demo/level2_samples/zh/review_report.md`

### 英文 JSON 样例
- 语言：en
- Transcript 格式：json
- 评审状态：可进入人工审阅
- 评审得分：100/100
- Transcript fixture：`examples/demo/sample_level2_transcript.json`
- 脚本包：`examples/demo/level2_samples/en_json/script_package.json`
- 脚本草稿：`examples/demo/level2_samples/en_json/script_draft.md`
- Blueprint：`examples/demo/level2_samples/en_json/production_blueprint.json`
- 交接 JSON：`examples/demo/level2_samples/en_json/operator_handoff.json`
- 评审 JSON：`examples/demo/level2_samples/en_json/review_report.json`
- 评审 Markdown：`examples/demo/level2_samples/en_json/review_report.md`

### 中文 VTT 样例
- 语言：zh
- Transcript 格式：vtt
- 评审状态：可进入人工审阅
- 评审得分：100/100
- Transcript fixture：`examples/demo/sample_level2_transcript_zh.vtt`
- 脚本包：`examples/demo/level2_samples/zh_vtt/script_package.json`
- 脚本草稿：`examples/demo/level2_samples/zh_vtt/script_draft.md`
- Blueprint：`examples/demo/level2_samples/zh_vtt/production_blueprint.json`
- 交接 JSON：`examples/demo/level2_samples/zh_vtt/operator_handoff.json`
- 评审 JSON：`examples/demo/level2_samples/zh_vtt/review_report.json`
- 评审 Markdown：`examples/demo/level2_samples/zh_vtt/review_report.md`

## 说明

- 如需刷新这些产物，运行 `python3 scripts/export_level2_demo_samples.py`。
- 如果你想要带时间戳的实时产物，请直接使用 CLI 输出到 `~/.openfang/clips/script_packages/`。
