# Showcase：从 Benchmark 到 Release 证据

## 目标

证明这个仓库不用下载受版权保护素材，也能产出一套完整可展示的证据链。

## 命令

```bash
python3 scripts/run_demo_benchmark.py --output-dir tmp/demo-benchmark-v030 --duration 18 --segment-duration 6 --transform 1
python3 scripts/release_prep.py v0.3.0 --report tmp/demo-benchmark-v030/benchmark_report.json
```

## 产出

- synthetic source video
- 3 个竖屏 clips
- `preview.png`
- `storyboard.png`
- `benchmark_report.json`
- `dist/releases/v0.3.0/` 下的一整套 release bundle

## 为什么重要

- 证明仓库可以在不碰外部版权素材的前提下被评估
- 给 GitHub release 和社交发布提供视觉素材
- 把叙事建立在可重复 benchmark 上，而不是空泛承诺

## 适合使用的场景

- GitHub release 页面
- 首波 launch 帖
- 给新贡献者讲解仓库能力
