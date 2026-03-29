"""
CLI Utilities

Utilities for enhanced command-line interface.
"""

import sys
from typing import Optional, Callable, Any
from enum import Enum
from dataclasses import dataclass
import logging

try:
    from tqdm import tqdm
    TQDM_AVAILABLE = True
except ImportError:
    TQDM_AVAILABLE = False

try:
    from rich.console import Console
    from rich.progress import Progress
    from rich.table import Table
    from rich.panel import Panel
    from rich.text import Text
    from rich import print as rprint
    RICH_AVAILABLE = True
except ImportError:
    RICH_AVAILABLE = False


logger = logging.getLogger(__name__)


class Color(Enum):
    """ANSI color codes"""
    RESET = "\033[0m"
    RED = "\033[91m"
    GREEN = "\033[92m"
    YELLOW = "\033[93m"
    BLUE = "\033[94m"
    MAGENTA = "\033[95m"
    CYAN = "\033[96m"
    WHITE = "\033[97m"
    BOLD = "\033[1m"


class Status(Enum):
    """Status indicators"""
    SUCCESS = "✅"
    ERROR = "❌"
    WARNING = "⚠️ "
    INFO = "ℹ️ "
    PROCESSING = "⏳"
    ROCKET = "🚀"


def print_colored(text: str, color: Color = Color.RESET):
    """Print colored text to console"""
    print(f"{color.value}{text}{Color.RESET.value}")


def print_success(text: str):
    """Print success message"""
    if RICH_AVAILABLE:
        rprint(f"[green]{Status.SUCCESS.value} {text}[/green]")
    else:
        print_colored(f"{Status.SUCCESS.value} {text}", Color.GREEN)


def print_error(text: str):
    """Print error message"""
    if RICH_AVAILABLE:
        rprint(f"[red]{Status.ERROR.value} {text}[/red]")
    else:
        print_colored(f"{Status.ERROR.value} {text}", Color.RED)


def print_warning(text: str):
    """Print warning message"""
    if RICH_AVAILABLE:
        rprint(f"[yellow]{Status.WARNING.value} {text}[/yellow]")
    else:
        print_colored(f"{Status.WARNING.value} {text}", Color.YELLOW)


def print_info(text: str):
    """Print info message"""
    if RICH_AVAILABLE:
        rprint(f"[blue]{Status.INFO.value} {text}[/blue]")
    else:
        print_colored(f"{Status.INFO.value} {text}", Color.BLUE)


def print_header(text: str, width: int = 70):
    """Print section header"""
    if RICH_AVAILABLE:
        console = Console()
        console.print(Panel(text, style="bold blue"))
    else:
        print()
        print_colored("=" * width, Color.BOLD)
        print_colored(text, Color.BOLD)
        print_colored("=" * width, Color.BOLD)
        print()


def print_table(headers: list, rows: list, title: Optional[str] = None):
    """Print data table"""
    if RICH_AVAILABLE:
        console = Console()
        table = Table(title=title, show_header=True, header_style="bold magenta")

        for header in headers:
            table.add_column(header)

        for row in rows:
            table.add_row(*row)

        console.print(table)
    else:
        # Simple table fallback
        if title:
            print(f"\n{title}")
            print("-" * len(title))

        # Print header
        print(" | ".join(headers))
        print("-" * len(" | ".join(headers)))

        # Print rows
        for row in rows:
            print(" | ".join(str(cell) for cell in row))


class ProgressBar:
    """Progress bar for long operations"""

    def __init__(self, total: int, description: str = "Processing"):
        """
        Initialize progress bar.

        Args:
            total: Total items to process
            description: Description of operation
        """
        self.total = total
        self.description = description
        self.current = 0

        if TQDM_AVAILABLE:
            self.pbar = tqdm(total=total, desc=description)
        elif RICH_AVAILABLE:
            self.console = Console()
            self.progress = Progress()
            self.task = self.progress.add_task(description, total=total)
        else:
            self.pbar = None

    def update(self, n: int = 1, description: Optional[str] = None):
        """
        Update progress.

        Args:
            n: Number of items completed
            description: Optional new description
        """
        self.current += n

        if TQDM_AVAILABLE:
            self.pbar.update(n)
            if description:
                self.pbar.set_description(description)
        elif RICH_AVAILABLE:
            self.progress.update(self.task, advance=n)

    def close(self):
        """Close progress bar"""
        if TQDM_AVAILABLE:
            self.pbar.close()
        elif RICH_AVAILABLE:
            self.console.print(self.progress)


def run_with_progress(
    items: list,
    description: str,
    func: Callable,
    show_progress: bool = True
) -> list:
    """
    Run function on items with progress bar.

    Args:
        items: List of items to process
        description: Description of operation
        func: Function to apply to each item
        show_progress: Whether to show progress bar

    Returns:
        List of results
    """
    results = []

    if show_progress and (TQDM_AVAILABLE or RICH_AVAILABLE):
        pbar = ProgressBar(len(items), description)

        try:
            for item in items:
                result = func(item)
                results.append(result)
                pbar.update()
        finally:
            pbar.close()
    else:
        for item in items:
            result = func(item)
            results.append(result)

    return results


@dataclass
class CLIConfig:
    """CLI configuration"""
    use_colors: bool = True
    use_progress_bars: bool = True
    verbose: bool = False
    quiet: bool = False

    @classmethod
    def from_args(cls, args) -> 'CLIConfig':
        """Create config from command-line arguments"""
        return cls(
            use_colors=not args.no_color if hasattr(args, 'no_color') else True,
            use_progress_bars=not args.no_progress if hasattr(args, 'no_progress') else True,
            verbose=getattr(args, 'verbose', False),
            quiet=getattr(args, 'quiet', False)
        )


def confirm_action(message: str, default: bool = False) -> bool:
    """
    Ask user for confirmation.

    Args:
        message: Confirmation message
        default: Default response if user just presses Enter

    Returns:
        True if user confirms, False otherwise
    """
    prompt = f"{message} [{'Y/n' if default else 'y/N'}] "

    try:
        response = input(prompt).strip().lower()

        if not response:
            return default

        if response in ['y', 'yes']:
            return True
        elif response in ['n', 'no']:
            return False

        # Invalid response
        print_warning("Please enter 'y' or 'n'")
        return confirm_action(message, default)

    except (EOFError, KeyboardInterrupt):
        print()  # New line after Ctrl-C
        return False


def format_duration(seconds: float) -> str:
    """
    Format duration in human-readable format.

    Args:
        seconds: Duration in seconds

    Returns:
        Formatted duration string
    """
    if seconds < 60:
        return f"{seconds:.1f}s"
    elif seconds < 3600:
        minutes = seconds / 60
        return f"{minutes:.1f}m"
    else:
        hours = seconds / 3600
        return f"{hours:.1f}h"


def format_file_size(bytes_size: int) -> str:
    """
    Format file size in human-readable format.

    Args:
        bytes_size: Size in bytes

    Returns:
        Formatted size string
    """
    for unit in ['B', 'KB', 'MB', 'GB']:
        if bytes_size < 1024.0:
            return f"{bytes_size:.1f} {unit}"
        bytes_size /= 1024.0
    return f"{bytes_size:.1f} TB"


def truncate(text: str, max_length: int = 50, suffix: str = "...") -> str:
    """
    Truncate text to max length.

    Args:
        text: Text to truncate
        max_length: Maximum length
        suffix: Suffix to add if truncated

    Returns:
        Truncated text
    """
    if len(text) <= max_length:
        return text

    return text[:max_length - len(suffix)] + suffix
