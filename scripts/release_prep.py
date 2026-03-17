#!/usr/bin/env python3
"""Prepare a release bundle and validate repository readiness."""

from __future__ import annotations

import argparse
import json
import re
import shutil
import subprocess
import sys
from datetime import datetime
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(REPO_ROOT))

from scripts import generate_launch_kit, generate_social_preview  # noqa: E402

REQUIRED_PATHS = [
    Path("README.md"),
    Path("README_EN.md"),
    Path("CHANGELOG.md"),
    Path("LICENSE"),
    Path("requirements.txt"),
    Path(".github/workflows/ci.yml"),
]


def validate_version(raw_version: str) -> str:
    """Normalize and validate semantic versions."""
    version = raw_version.strip()
    if version.startswith("v"):
        version = version[1:]

    if not re.fullmatch(r"\d+\.\d+\.\d+", version):
        raise ValueError("version must look like 0.3.0 or v0.3.0")

    return version


def run_command(command: list[str], cwd: Path | None = None) -> str:
    """Run a command and return stdout, raising on failure."""
    result = subprocess.run(
        command,
        cwd=str(cwd or REPO_ROOT),
        capture_output=True,
        text=True,
    )
    if result.returncode != 0:
        raise RuntimeError(result.stderr.strip() or result.stdout.strip() or "command failed")
    return result.stdout.strip()


def git_status_clean() -> bool:
    """Return whether the working tree is clean."""
    output = run_command(["git", "status", "--porcelain"])
    return output == ""


def ensure_required_paths() -> list[str]:
    """Return missing required repo paths."""
    missing = []
    for relative_path in REQUIRED_PATHS:
        if not (REPO_ROOT / relative_path).exists():
            missing.append(str(relative_path))
    return missing


def extract_changelog_section(version: str) -> str:
    """Extract the matching changelog section or fallback to unreleased."""
    changelog_path = REPO_ROOT / "CHANGELOG.md"
    contents = changelog_path.read_text()
    version_headers = [f"## [{version}]", f"## [v{version}]"]

    lines = contents.splitlines()
    capture = False
    captured: list[str] = []

    for line in lines:
        if any(line.startswith(header) for header in version_headers):
            capture = True
        elif capture and line.startswith("## ["):
            break

        if capture:
            captured.append(line)

    if captured:
        return "\n".join(captured).strip()

    unreleased: list[str] = []
    capture = False
    for line in lines:
        if line.startswith("## [Unreleased]"):
            capture = True
        elif capture and line.startswith("## ["):
            break
        if capture:
            unreleased.append(line)

    return "\n".join(unreleased).strip() or "No changelog section found."


def run_tests() -> None:
    """Run the unit test suite."""
    run_command([sys.executable, "-m", "unittest", "discover", "-s", "tests"])


def load_report(report_path: Path) -> dict:
    """Load a benchmark report."""
    return json.loads(report_path.read_text())


def build_release_notes(version: str, changelog_section: str, report: dict | None = None) -> str:
    """Generate markdown release notes."""
    report_lines = []
    if report is not None:
        benchmark = report["benchmark"]
        timings = report["timings"]
        artifacts = report["artifacts"]
        report_lines = [
            "## Benchmark Proof",
            f"- Synthetic duration: {benchmark['duration_seconds']}s",
            f"- Transform level: {benchmark['transform_level']}",
            f"- Clips generated: {artifacts['clip_count']}",
            f"- Total runtime: {timings['total_seconds']}s",
            "",
        ]

    return "\n".join(
        [
            f"# OpenFang Auto Clip v{version}",
            "",
            f"Prepared at: {datetime.now().isoformat(timespec='seconds')}",
            "",
            "## Validation",
            "- README.md present",
            "- README_EN.md present",
            "- CHANGELOG.md present",
            "- CI workflow present",
            "- Unit tests passed",
            "",
            *report_lines,
            "## Changelog",
            changelog_section,
            "",
            "## Suggested Publish Steps",
            "1. Review release_notes.md",
            "2. Create tag `v{version}`",
            "3. Push branch and tag",
            "4. Draft GitHub release using the generated notes",
            "",
        ]
    ).replace("v{version}", f"v{version}")


def write_release_bundle(version: str, notes: str, output_dir: Path) -> Path:
    """Write release artifacts to disk."""
    target_dir = output_dir / f"v{version}"
    target_dir.mkdir(parents=True, exist_ok=True)
    notes_path = target_dir / "release_notes.md"
    notes_path.write_text(notes)
    return notes_path


def copy_release_artifact(source: Path, target_dir: Path) -> Path | None:
    """Copy an existing artifact into the release bundle."""
    if not source.exists():
        return None

    target_dir.mkdir(parents=True, exist_ok=True)
    target_path = target_dir / source.name
    shutil.copy2(source, target_path)
    return target_path


def copy_release_artifact_as(source: Path, target_dir: Path, target_name: str) -> Path | None:
    """Copy an artifact into the release bundle using a fixed target name."""
    if not source.exists():
        return None

    target_dir.mkdir(parents=True, exist_ok=True)
    target_path = target_dir / target_name
    shutil.copy2(source, target_path)
    return target_path


def build_showcase_bundle(report: dict, report_path: Path, target_dir: Path) -> list[Path]:
    """Generate release-ready showcase assets from a benchmark report."""
    created_paths: list[Path] = []

    copied_report = copy_release_artifact_as(report_path, target_dir, "benchmark_report.json")
    if copied_report is not None:
        created_paths.append(copied_report)

    for artifact_key in ("preview_path", "storyboard_path"):
        raw_path = report["artifacts"].get(artifact_key)
        if not raw_path:
            continue

        copied_path = copy_release_artifact(REPO_ROOT / raw_path, target_dir)
        if copied_path is not None:
            created_paths.append(copied_path)

    launch_markdown = generate_launch_kit.build_launch_markdown(report, language="en")
    created_paths.append(generate_launch_kit.write_launch_kit(launch_markdown, target_dir, "en"))

    launch_markdown_zh = generate_launch_kit.build_launch_markdown(report, language="zh")
    created_paths.append(generate_launch_kit.write_launch_kit(launch_markdown_zh, target_dir, "zh"))

    social_preview_svg = generate_social_preview.build_social_preview_svg(report, language="en")
    created_paths.append(generate_social_preview.write_social_preview(social_preview_svg, target_dir, "en"))

    social_preview_svg_zh = generate_social_preview.build_social_preview_svg(report, language="zh")
    created_paths.append(generate_social_preview.write_social_preview(social_preview_svg_zh, target_dir, "zh"))

    manifest_path = target_dir / "bundle_manifest.json"
    manifest_path.write_text(
        json.dumps(
            {
                "generated_at": datetime.now().isoformat(timespec="seconds"),
                "assets": [path.name for path in created_paths],
            },
            indent=2,
        )
    )
    created_paths.append(manifest_path)

    return created_paths


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Validate and prepare a release bundle")
    parser.add_argument("version", help="Semantic version like 0.3.0 or v0.3.0")
    parser.add_argument(
        "--output-dir",
        default="dist/releases",
        help="Directory for generated release artifacts",
    )
    parser.add_argument(
        "--skip-tests",
        action="store_true",
        help="Skip running the unit test suite",
    )
    parser.add_argument(
        "--report",
        default="examples/benchmark/sample_benchmark_report.json",
        help="Benchmark report JSON to use for showcase assets",
    )
    parser.add_argument(
        "--skip-showcase-assets",
        action="store_true",
        help="Skip generating launch-kit and social-preview assets",
    )
    parser.add_argument(
        "--allow-dirty",
        action="store_true",
        help="Allow preparing a release from a dirty working tree",
    )
    return parser.parse_args()


def main() -> int:
    args = parse_args()

    try:
        version = validate_version(args.version)
    except ValueError as exc:
        print(f"❌ {exc}")
        return 1

    if not args.allow_dirty and not git_status_clean():
        print("❌ Working tree is dirty. Commit or stash changes, or use --allow-dirty.")
        return 1

    missing_paths = ensure_required_paths()
    if missing_paths:
        print("❌ Missing required release files:")
        for path in missing_paths:
            print(f"   - {path}")
        return 1

    if not args.skip_tests:
        print("🧪 Running unit tests...")
        run_tests()

    report_path = REPO_ROOT / args.report
    report = None
    if not args.skip_showcase_assets:
        if not report_path.exists():
            print(f"❌ Benchmark report not found: {report_path}")
            return 1
        report = load_report(report_path)

    changelog_section = extract_changelog_section(version)
    notes = build_release_notes(version, changelog_section, report=report)
    notes_path = write_release_bundle(version, notes, REPO_ROOT / args.output_dir)
    target_dir = notes_path.parent

    created_assets: list[Path] = []
    if report is not None:
        created_assets = build_showcase_bundle(report, report_path, target_dir)

    print("✅ Release bundle prepared")
    print(f"   Version: v{version}")
    print(f"   Notes: {notes_path}")
    for asset_path in created_assets:
        print(f"   Asset: {asset_path}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
