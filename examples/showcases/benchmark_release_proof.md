# Showcase: Benchmark To Release Proof

## Goal

Show that the repository can generate proof without downloading copyrighted source media.

## Command

```bash
python3 scripts/run_demo_benchmark.py --output-dir tmp/demo-benchmark-v030 --duration 18 --segment-duration 6 --transform 1
python3 scripts/release_prep.py v0.3.0 --report tmp/demo-benchmark-v030/benchmark_report.json
```

## What This Produces

- a synthetic source video
- 3 vertical clips
- `preview.png`
- `storyboard.png`
- `benchmark_report.json`
- a release bundle under `dist/releases/v0.3.0/`

## Why It Matters

- proves the repo can be evaluated without external media rights
- gives you visuals for GitHub release pages and social posts
- keeps claims tied to a repeatable benchmark instead of vague promises

## Best Use

- GitHub release notes
- first launch thread
- repo walkthrough for new contributors
