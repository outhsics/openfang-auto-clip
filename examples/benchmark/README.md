# Benchmark Demo

This benchmark uses synthetic media, so anyone can reproduce the pipeline without downloading copyrighted source videos.

## What it does

- generates a short synthetic source video with `ffmpeg`
- optionally applies Level 1 transformation
- cuts the result into vertical clips
- writes a benchmark report, bilingual benchmark summary, preview frame, and storyboard image

## Run it

```bash
python3 scripts/run_demo_benchmark.py
```

## Output

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

## Sample benchmark report

See [`sample_benchmark_report.json`](sample_benchmark_report.json).
See [`sample_benchmark_summary.md`](sample_benchmark_summary.md) for the committed bilingual summary snapshot.

The committed sample is illustrative. Running the script locally will generate a fresh report with your machine's timings.
The generated `benchmark_summary.md` is the fastest bilingual artifact to read or share.

## Why the storyboard matters

`storyboard.png` is the quickest shareable artifact from the benchmark run.
You can drop it into:

- GitHub releases
- issue reports
- X / LinkedIn launch posts
- README updates when you refresh the demo
