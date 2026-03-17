# Versioning Guide

OpenFang Auto Clip follows semantic versioning.

## Tag format

Use tags in the form:

```text
vMAJOR.MINOR.PATCH
```

Examples:

- `v0.3.0`
- `v0.3.1`
- `v1.0.0`

## Meaning

- `MAJOR`: breaking CLI or workflow changes
- `MINOR`: new backward-compatible capabilities
- `PATCH`: fixes, docs, hardening, and small behavior corrections

## Release flow

1. Merge validated work into `main`
2. Run `python3 scripts/release_prep.py vX.Y.Z --report tmp/demo-benchmark-vXYZ/benchmark_report.json`
3. Commit any final changelog updates
4. Create and push the tag

```bash
git tag v0.3.0
git push origin main
git push origin v0.3.0
```

The release-prep script now bundles:

- `release_notes.md`
- copied benchmark report
- preview and storyboard images when present
- `launch_post.md`
- English and Chinese social preview SVGs

When the tag reaches GitHub, `.github/workflows/release.yml` will:

- install dependencies
- run the test suite
- generate release notes
- create the GitHub Release automatically

## Practical guidance

- Use `0.x` while the product surface is still changing quickly
- Do not mark `1.0.0` until Level 1, web manager, docs, and release flow are all stable
- Prefer shipping small tagged increments over large delayed releases
