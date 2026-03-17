# Changelog

All notable changes to OpenFang Auto Clip will be documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.0.0/),
and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

## [0.3.0] - 2026-03-17

### Added
- GitHub Actions CI for unit tests and Python compile checks
- Development dependency manifest (`requirements-dev.txt`)
- Installation guide at `docs/INSTALLATION.md`
- Demo evaluation assets in `examples/demo/` and `docs/assets/readme-hero.svg`
- CLI readiness commands: `--doctor` and `--dry-run`
- `scripts/release_prep.py` for validated release-note generation
- Synthetic benchmark workflow in `scripts/run_demo_benchmark.py`
- Automated GitHub tag release workflow and versioning guide
- GitHub issue templates and pull request template
- Benchmark storyboard generation for shareable visual output
- Launch-kit generator for benchmark-based promotion copy
- Social preview generator for GitHub and launch posts
- Governance and support files: `SECURITY.md`, `SUPPORT.md`, `CODE_OF_CONDUCT.md`, `DISCLAIMER.md`
- Persistent AI handoff docs: `AI_CONTEXT.md`, `PROJECT_STATUS.md`, `OPEN_SOURCE_PLAN.md`
- Packaging metadata via `pyproject.toml` and `setup.py`
- Release bundle generation with benchmark report, preview, storyboard, launch post, and social preview assets

### Changed
- Installer now uses the same `~/.openfang` paths as the runtime
- Quick start documentation now matches the actual CLI entrypoints
- Repository messaging now reflects shipped scope and avoids overclaiming Level 2 / Level 3
- Release flow now produces a benchmark-backed showcase bundle instead of notes only
- MIT license file restored to standard format for proper GitHub detection
- GitHub Discussions enabled for community support

### Planned
- Level 2 script regeneration
- Level 3 complete recreation
- Web dashboard
- API server
- Mobile app

## [Unreleased]

### Added

### Changed

### Planned

## [0.2.0] - 2026-02-28

### Added
- Copyright-safe transformation framework
- Level 1 visual remix (style transfer, speed modification)
- Multi-platform support (TikTok, Shorts, Reels, Douyin)
- Automated video downloading
- FFmpeg-based video processing
- Configuration system
- MIT License with copyright notice
- Chinese and English documentation
- Installation script
- Example configurations

### Changed
- Improved file name sanitization
- Better error handling
- Enhanced logging

### Fixed
- Special character issues in filenames
- FFmpeg path resolution
- Download failures with protected videos

## [0.1.0] - 2026-02-27

### Added
- Initial release
- Basic video downloading
- Simple clip detection
- FFmpeg integration
- OpenFang integration
- Whisper transcription support
- Basic documentation

---

## Version Format

- **Major.Minor.Patch** (e.g., 1.2.3)
- **Major**: Breaking changes
- **Minor**: New features (backward compatible)
- **Patch**: Bug fixes (backward compatible)

---

## Release Notes

### v0.2.0 Highlights

This release introduces **copyright-safe transformation**, a groundbreaking feature that helps content creators avoid copyright issues while maintaining content value.

**Key Features:**
- 🛡️ 3 levels of copyright protection
- 🎨 Visual remix (Level 1)
- 📝 Script regeneration framework (Level 2 - planned)
- 🎬 Complete recreation framework (Level 3 - planned)

**Legal Note:** This tool helps create original content, but users are responsible for ensuring compliance with applicable laws and platform terms.

---

**For older versions, see GitHub releases.**
