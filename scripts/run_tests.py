#!/usr/bin/env python3
"""
Test runner for OpenFang Auto Clip

Runs all tests with coverage reporting.
"""

import sys
import subprocess
from pathlib import Path


def run_tests(coverage=False, verbose=False, pattern=None):
    """Run tests"""
    project_dir = Path(__file__).parent.parent
    tests_dir = project_dir / "tests"

    # Build pytest command
    cmd = [sys.executable, "-m", "pytest", str(tests_dir)]

    if verbose:
        cmd.append("-v")

    if coverage:
        cmd.extend([
            "--cov=src",
            "--cov-report=term-missing",
            "--cov-report=html",
            "--cov-report=xml"
        ])

    if pattern:
        cmd.extend(["-k", pattern])

    # Run tests
    result = subprocess.run(cmd, cwd=project_dir)

    return result.returncode


def run_specific_test(test_file):
    """Run a specific test file"""
    project_dir = Path(__file__).parent.parent
    test_path = project_dir / "tests" / test_file

    if not test_path.exists():
        print(f"Test file not found: {test_path}")
        return 1

    cmd = [sys.executable, "-m", "pytest", str(test_path), "-v"]
    result = subprocess.run(cmd, cwd=project_dir)

    return result.returncode


def list_tests():
    """List all available tests"""
    tests_dir = Path(__file__).parent.parent / "tests"

    test_files = sorted(tests_dir.glob("test_*.py"))

    print("Available test files:")
    for test_file in test_files:
        print(f"  - {test_file.name}")


def main():
    """Main entry point"""
    import argparse

    parser = argparse.ArgumentParser(description="Run OpenFang Auto Clip tests")
    parser.add_argument("--coverage", "-c", action="store_true",
                        help="Generate coverage report")
    parser.add_argument("--verbose", "-v", action="store_true",
                        help="Verbose output")
    parser.add_argument("--pattern", "-k",
                        help="Run tests matching pattern")
    parser.add_argument("--file", "-f",
                        help="Run specific test file")
    parser.add_argument("--list", "-l", action="store_true",
                        help="List all test files")

    args = parser.parse_args()

    if args.list:
        list_tests()
        return 0

    if args.file:
        return run_specific_test(args.file)

    return run_tests(
        coverage=args.coverage,
        verbose=args.verbose,
        pattern=args.pattern
    )


if __name__ == "__main__":
    sys.exit(main())
