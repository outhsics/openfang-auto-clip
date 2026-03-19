# Benchmark 演示

这个 benchmark 使用合成媒体生成输入，因此任何人都可以复现整条流水线，而不需要下载受版权保护的源视频。

## 会做什么

- 用 `ffmpeg` 生成一段合成测试视频
- 可选地应用 `Level 1` 转换
- 将结果切成竖屏 clip
- 输出 benchmark 报告、双语 benchmark 摘要、预览图和 storyboard

## 运行方式

```bash
python3 scripts/run_demo_benchmark.py
```

## 输出结构

```text
tmp/demo-benchmark/
├── benchmark_report.json
├── benchmark_summary.md
├── preview.png
├── storyboard.png
├── synthetic_source.mp4
└── clips/
    ├── clip_01_0000s-0006s.mp4
    ├── clip_02_0006s-0012s.mp4
    └── clip_03_0012s-0018s.mp4
```

## 示例报告

参见 [`sample_benchmark_report.json`](sample_benchmark_report.json)。
也可以直接看 [`sample_benchmark_summary.md`](sample_benchmark_summary.md) 这个已提交的双语摘要快照。

仓库里提交的是示例文件，实际在本地运行脚本后会生成带有你机器耗时数据的新报告。
其中 `benchmark_summary.md` 是最适合快速阅读和传播的双语摘要产物。

## 为什么 storyboard 很重要

`storyboard.png` 是 benchmark 运行后最适合传播的一份资产，适合直接拿去放到：

- GitHub Release
- issue 复现场景
- X / LinkedIn 发布帖
- README 更新素材
