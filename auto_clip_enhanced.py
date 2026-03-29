#!/usr/bin/env python3
"""
OpenFang Auto Clip - Enhanced CLI

Improved command-line interface with better UX.
"""

import sys
import argparse
import logging
from pathlib import Path

# Add project root to path
REPO_ROOT = Path(__file__).resolve().parent
sys.path.insert(0, str(REPO_ROOT))

from scripts.cli_commands import add_enhanced_commands
from scripts.cli_utils import CLIConfig, print_header, print_success


def main():
    """Main CLI entry point"""
    parser = argparse.ArgumentParser(
        prog='auto_clip',
        description='OpenFang Auto Clip - Automated video short creation',
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  # Initialize configuration
  auto_clip init

  # Process a transcript
  auto_clip process transcript.srt

  # Process with validation
  auto_clip process transcript.srt --validate

  # List all jobs
  auto_clip jobs

  # Show system status
  auto_clip status

  # Validate a package
  auto_clip validate package.json
        """
    )

    parser.add_argument('--version', action='version', version='%(prog)s 0.5.0')
    parser.add_argument('-v', '--verbose', action='store_true', help='Verbose output')
    parser.add_argument('-q', '--quiet', action='store_true', help='Quiet mode')
    parser.add_argument('--no-color', action='store_true', help='Disable colored output')
    parser.add_argument('--no-progress', action='store_true', help='Disable progress bars')

    # Add subcommands
    subparsers = parser.add_subparsers(dest='command', help='Available commands')
    subparsers.required = False

    # Add enhanced commands
    add_enhanced_commands(subparsers)

    # Parse arguments
    args = parser.parse_args()

    # Create CLI config
    config = CLIConfig.from_args(args)

    # Setup logging
    logging.basicConfig(
        level=logging.DEBUG if config.verbose else logging.INFO,
        format='%(asctime)s - %(name)s - %(levelname)s - %(message)s' if config.verbose else '%(message)s'
    )

    # Execute command
    if hasattr(args, 'func'):
        return args.func(args)
    else:
        # No command specified, show help
        parser.print_help()
        return 0


if __name__ == '__main__':
    sys.exit(main())
