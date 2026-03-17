# Social Preview Guide

This repository can now generate a reusable social preview asset directly from a benchmark report.

## Why this matters

The GitHub repo page is part of growth. A strong social preview image improves:

- repository share cards
- GitHub release presentation
- launch posts on X / LinkedIn
- consistency between README claims and visual proof

## Generate the asset

```bash
python3 scripts/generate_social_preview.py --report examples/benchmark/sample_benchmark_report.json
python3 scripts/generate_social_preview.py --report examples/benchmark/sample_benchmark_report.json --lang zh
```

Outputs are written to:

```text
dist/social-preview/
├── github_social_preview.svg
└── github_social_preview_zh.svg
```

## Recommended workflow

1. Run the benchmark
2. Generate the social preview image
3. Upload the English asset in GitHub repository settings as the default social preview
4. Use the Chinese asset for local launch posts, docs-site screenshots, or release collateral

## What the image shows

- project positioning
- reproducible proof signals
- benchmark metrics
- repository path

## Positioning guidance

Keep the image aligned with the repo's real current status:

- promote `CLI`, `Level 1`, `benchmark`, `storyboard`, and `release flow`
- do not present `Level 2` or `Level 3` as finished commercial capabilities

## Related files

- `scripts/generate_social_preview.py`
- `examples/benchmark/sample_benchmark_report.json`
- `scripts/generate_launch_kit.py`
