#!/usr/bin/env python3
"""
Release automation script

Helps automate the release process for OpenFang Auto Clip.
"""

import re
import subprocess
import sys
from pathlib import Path
from datetime import datetime


def get_current_version() -> str:
    """Get current version from __init__.py"""
    init_file = Path(__file__).parent.parent / "src" / "__init__.py"
    if init_file.exists():
        content = init_file.read_text()
        match = re.search(r'__version__\s*=\s*["\']([^"\']+)["\']', content)
        if match:
            return match.group(1)
    return "0.0.0"


def update_version(version: str):
    """Update version in __init__.py"""
    init_file = Path(__file__).parent.parent / "src" / "__init__.py"
    if init_file.exists():
        content = init_file.read_text()
        content = re.sub(
            r'__version__\s*=\s*["\'][^"\']+["\']',
            f'__version__ = "{version}"',
            content
        )
        init_file.write_text(content)
        print(f"✅ Updated version to {version}")


def update_changelog(version: str, changes: list):
    """Update CHANGELOG.md"""
    changelog_file = Path(__file__).parent.parent / "CHANGELOG.md"

    # Get today's date
    date = datetime.now().strftime("%Y-%m-%d")

    # Create new entry
    new_entry = f"""
## [{version}] - {date}

### 🚀 Features
{chr(10).join(f'- {change}' for change in changes.get('features', []))}

### 🐛 Bug Fixes
{chr(10).join(f'- {change}' for change in changes.get('fixes', []))}

### 📚 Documentation
{chr(10).join(f'- {change}' for change in changes.get('docs', []))}

### 🧪 Tests
{chr(10).join(f'- {change}' for change in changes.get('tests', []))}

"""

    if changelog_file.exists():
        content = changelog_file.read_text()
        # Insert after the first line (title)
        lines = content.split('\n', 1)
        content = lines[0] + new_entry + '\n' + lines[1]
        changelog_file.write_text(content)
    else:
        # Create new changelog
        changelog_file.write_text(f"# Changelog\n\n{new_entry}")

    print(f"✅ Updated CHANGELOG.md for {version}")


def create_git_tag(version: str):
    """Create and push git tag"""
    tag = f"v{version}"

    # Check if tag exists
    result = subprocess.run(
        ["git", "tag", "-l", tag],
        capture_output=True,
        text=True
    )

    if tag in result.stdout:
        print(f"⚠️  Tag {tag} already exists")
        return False

    # Create tag
    subprocess.run(["git", "tag", "-a", tag, "-m", f"Release {version}"])
    print(f"✅ Created git tag {tag}")

    # Ask before pushing
    response = input(f"Push tag {tag} to remote? (y/N): ")
    if response.lower() == 'y':
        subprocess.run(["git", "push", "origin", tag])
        print(f"✅ Pushed tag {tag}")
        return True

    return False


def build_package():
    """Build Python package"""
    print("📦 Building package...")

    # Clean old builds
    for pattern in ["dist/*", "build/*", "*.egg-info"]:
        subprocess.run(["rm", "-rf", *Path(".").glob(pattern)], shell=True)

    # Build
    subprocess.run(["python", "-m", "build"])
    print("✅ Package built successfully")


def publish_to_pypi(test: bool = True):
    """Publish to PyPI"""
    print("📤 Publishing to PyPI...")

    if test:
        print("   (Test mode - use --production for actual publish)")
        repository = "--repository testpypi"
    else:
        repository = ""

    result = subprocess.run(
        ["twine", "upload", repository, "dist/*"],
        capture_output=True,
        text=True
    )

    if result.returncode == 0:
        print("✅ Published to PyPI")
        return True
    else:
        print(f"❌ Failed to publish: {result.stderr}")
        return False


def run_pre_release_checks():
    """Run pre-release checks"""
    print("🔍 Running pre-release checks...")

    checks = []

    # Check if working directory is clean
    result = subprocess.run(
        ["git", "status", "--porcelain"],
        capture_output=True,
        text=True
    )

    if result.stdout.strip():
        print("⚠️  Working directory is not clean")
        checks.append(False)
    else:
        print("✅ Working directory is clean")
        checks.append(True)

    # Run tests
    print("🧪 Running tests...")
    result = subprocess.run(
        ["python", "-m", "pytest", "tests/", "-v"],
        capture_output=True,
        text=True
    )

    if result.returncode == 0:
        print("✅ All tests passed")
        checks.append(True)
    else:
        print("⚠️  Some tests failed")
        checks.append(False)

    return all(checks)


def main():
    """Main release workflow"""
    print("=" * 60)
    print("OpenFang Auto Clip - Release Automation")
    print("=" * 60)

    if len(sys.argv) < 2:
        print("""
Usage: python scripts/release.py <command> [options]

Commands:
  version          Show current version
  bump <type>      Bump version (major, minor, patch)
  changelog        Update changelog (interactive)
  tag              Create git tag
  build            Build package
  publish          Publish to PyPI (test mode)
  publish-prod     Publish to PyPI (production)
  release          Full release workflow
  check            Run pre-release checks

Examples:
  python scripts/release.py version
  python scripts/release.py bump patch
  python scripts/release.py release
        """)
        return

    command = sys.argv[1]

    if command == "version":
        version = get_current_version()
        print(f"Current version: {version}")

    elif command == "bump":
        if len(sys.argv) < 3:
            print("Usage: python scripts/release.py bump <major|minor|patch>")
            return

        bump_type = sys.argv[2]
        current = get_current_version()

        # Parse version
        parts = current.split(".")
        major, minor, patch = int(parts[0]), int(parts[1]), int(parts[2])

        if bump_type == "major":
            major += 1
            minor = 0
            patch = 0
        elif bump_type == "minor":
            minor += 1
            patch = 0
        elif bump_type == "patch":
            patch += 1
        else:
            print(f"Invalid bump type: {bump_type}")
            return

        new_version = f"{major}.{minor}.{patch}"
        update_version(new_version)

    elif command == "changelog":
        version = get_current_version()
        print(f"Updating CHANGELOG for {version}")
        print("Enter changes (one per line, empty line to finish):")

        changes = {
            "features": [],
            "fixes": [],
            "docs": [],
            "tests": []
        }

        category_map = {
            "1": ("features", "Features"),
            "2": ("fixes", "Bug Fixes"),
            "3": ("docs", "Documentation"),
            "4": ("tests", "Tests")
        }

        print("\nSelect category:")
        for key, (name, label) in category_map.items():
            print(f"  {key}. {label}")

        while True:
            choice = input("\nCategory (1-4, or Enter to finish): ")
            if not choice:
                break

            if choice not in category_map:
                continue

            key, label = category_map[choice]
            print(f"\nEnter {label} (empty line to finish category):")

            while True:
                change = input("  - ")
                if not change:
                    break
                changes[key].append(change)

        update_changelog(version, changes)

    elif command == "tag":
        version = get_current_version()
        create_git_tag(version)

    elif command == "build":
        build_package()

    elif command == "publish":
        publish_to_pypi(test=True)

    elif command == "publish-prod":
        publish_to_pypi(test=False)

    elif command == "check":
        if run_pre_release_checks():
            print("\n✅ All checks passed!")
        else:
            print("\n⚠️  Some checks failed")
            sys.exit(1)

    elif command == "release":
        # Full release workflow
        print("\n🚀 Starting release workflow...\n")

        # Run checks
        if not run_pre_release_checks():
            print("\n❌ Pre-release checks failed. Aborting.")
            sys.exit(1)

        # Build package
        build_package()

        # Create git tag
        version = get_current_version()
        if create_git_tag(version):
            # Publish to PyPI
            response = input("\nPublish to PyPI? (y/N): ")
            if response.lower() == 'y':
                publish_to_pypi(test=False)

        print("\n✅ Release workflow complete!")

    else:
        print(f"Unknown command: {command}")


if __name__ == "__main__":
    main()
