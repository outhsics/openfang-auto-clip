#!/usr/bin/env python3
"""Compatibility wrapper for the repository root auto_clip module."""

from auto_clip import *  # noqa: F401,F403


if __name__ == "__main__":
    from auto_clip import main

    main()
