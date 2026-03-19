# OpenFang Auto Clip

<div align="center">

**Local-first video repurposing pipeline with reproducible benchmark and release assets**

[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](LICENSE)
[![Python 3.9+](https://img.shields.io/badge/python-3.9+-blue.svg)](https://www.python.org/downloads/)
[![CI](https://github.com/outhsics/openfang-auto-clip/actions/workflows/ci.yml/badge.svg)](https://github.com/outhsics/openfang-auto-clip/actions/workflows/ci.yml)

English | [简体中文](README.md)

</div>

![OpenFang Auto Clip overview](docs/assets/readme-hero.svg)

## 60-Second Evaluation

- Read the status snapshot in [PROJECT_STATUS.md](PROJECT_STATUS.md)
- Run the synthetic benchmark from [examples/benchmark/README.md](examples/benchmark/README.md)
- Inspect the sample operator output in [examples/demo/README.md](examples/demo/README.md)
- Browse reusable launch demos in [examples/showcases/README.md](examples/showcases/README.md)
- Review transformation scope in [docs/TRANSFORMATION.md](docs/TRANSFORMATION.md)
- Review the growth plan in [OPEN_SOURCE_PLAN.md](OPEN_SOURCE_PLAN.md)
- Use [AI_CONTEXT.md](AI_CONTEXT.md) for future AI handoff

## What This Repo Does Today

- downloads a source video with `yt-dlp`
- applies a working local Level 1 FFmpeg remix path
- builds a Level 2 transcript-to-script package with timed source anchors, shot plan, and review rubric when a transcript is provided
- generates a self-contained Level 2 demo package from a bundled transcript for quick evaluation
- slices output into 9:16 clips with a simple local strategy
- provides `--doctor` and `--dry-run` commands for safer evaluation
- includes a local web manager for task launching and inspection
- ships a synthetic benchmark plus release collateral generators

## Reality Check

| Area | Status | Notes |
|------|--------|-------|
| Download + clip export | Working | Main local CLI path |
| Level 1 remix | Working | FFmpeg-based and reproducible |
| Web manager | Working | Local-only operator console |
| Synthetic benchmark | Working | No external media required |
| Social preview + release assets | Working | Helper scripts are in-repo |
| Level 2 script regeneration | Partial | Transcript-to-script package, shot plan, and blueprint work; rebuilt video remains manual |
| Level 3 complete recreation | Scaffolded | Not production-ready |
| Hosted SaaS / public API | Not offered | This repo is local-first |

## Quick Start

```bash
git clone https://github.com/outhsics/openfang-auto-clip.git
cd openfang-auto-clip

python3 -m venv .venv
source .venv/bin/activate
pip install -e .

./auto_clip.sh --doctor
python3 scripts/run_demo_benchmark.py
python3 auto_clip.py --demo-script-package
./auto_clip.sh "https://www.youtube.com/watch?v=VIDEO_ID" --dry-run
./auto_clip.sh "https://www.youtube.com/watch?v=VIDEO_ID" --transform 1 --duration 45
./auto_clip.sh "https://www.youtube.com/watch?v=VIDEO_ID" --transform 2 --transcript path/to/source.srt
```

If you prefer the bundled installer, see [docs/INSTALLATION.md](docs/INSTALLATION.md).

## Common Commands

```bash
# Environment check
./auto_clip.sh --doctor

# Safe planning pass without downloading media
./auto_clip.sh "URL" --dry-run

# Run the synthetic benchmark
python3 scripts/run_demo_benchmark.py

# Run the zero-external-media Level 2 demo
python3 auto_clip.py --demo-script-package

# Generate a Level 2 script package from a transcript
./auto_clip.sh "URL" --transform 2 --transcript path/to/source.srt

# Generate GitHub social preview assets
python3 scripts/generate_social_preview.py --report examples/benchmark/sample_benchmark_report.json

# Prepare a release bundle with benchmark proof
python3 scripts/release_prep.py v0.3.0 --report tmp/demo-benchmark-v030/benchmark_report.json

# Start the local web manager
./start_web_manager.sh

# Run the test suite
python3 -m unittest discover -s tests
```

## Documentation Map

- [DOCUMENTATION.md](DOCUMENTATION.md)
- [docs/INSTALLATION.md](docs/INSTALLATION.md)
- [docs/TRANSFORMATION.md](docs/TRANSFORMATION.md)
- [docs/SOCIAL_PREVIEW.md](docs/SOCIAL_PREVIEW.md)
- [docs/VERSIONING.md](docs/VERSIONING.md)
- [PROJECT_STATUS.md](PROJECT_STATUS.md)
- [OPEN_SOURCE_PLAN.md](OPEN_SOURCE_PLAN.md)
- [AI_CONTEXT.md](AI_CONTEXT.md)

## Positioning

OpenFang Auto Clip should be described as:

- a local-first operator workflow
- a reproducible benchmark and clip-generation repo
- a practical Level 1 remix tool today
- an early Level 2 script-package workflow, not a finished regeneration suite

It should not be described as:

- a guaranteed copyright-safe system
- a hosted SaaS
- a finished Level 2 / Level 3 platform

## Support And Community

- Bugs: [GitHub Issues](https://github.com/outhsics/openfang-auto-clip/issues)
- Usage questions: see [SUPPORT.md](SUPPORT.md)
- Security concerns: see [SECURITY.md](SECURITY.md)
- Contribution guidelines: [CONTRIBUTING.md](CONTRIBUTING.md)

## License

This repository uses the MIT License. Read [LICENSE](LICENSE) and [DISCLAIMER.md](DISCLAIMER.md) before using it for commercial or high-risk workflows.
