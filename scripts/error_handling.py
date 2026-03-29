"""
Error Handling and Recovery System for OpenFang Auto Clip

This module provides comprehensive error handling, recovery mechanisms,
and graceful degradation for the Level 2 pipeline.
"""

import os
import sys
import json
import traceback
import logging
from pathlib import Path
from datetime import datetime
from typing import Dict, List, Optional, Any, Callable
from enum import Enum
from contextlib import contextmanager
from dataclasses import dataclass, field
import time


# ============================================================================
# ERROR CLASSIFICATION
# ============================================================================

class ErrorSeverity(Enum):
    """Error severity levels"""
    WARNING = "warning"
    RECOVERABLE = "recoverable"
    CRITICAL = "critical"
    FATAL = "fatal"


class ErrorCategory(Enum):
    """Error categories for better handling"""
    FILE_IO = "file_io"
    NETWORK = "network"
    TRANSCRIPT = "transcript"
    API = "api"
    VALIDATION = "validation"
    RESOURCE = "resource"
    UNKNOWN = "unknown"


@dataclass
class ErrorInfo:
    """Structured error information"""
    category: ErrorCategory
    severity: ErrorSeverity
    message: str
    details: Dict[str, Any] = field(default_factory=dict)
    traceback_str: Optional[str] = None
    timestamp: str = field(default_factory=lambda: datetime.now().isoformat())
    recoverable: bool = True

    def to_dict(self) -> Dict:
        """Convert to dictionary"""
        return {
            "category": self.category.value,
            "severity": self.severity.value,
            "message": self.message,
            "details": self.details,
            "traceback": self.traceback_str,
            "timestamp": self.timestamp,
            "recoverable": self.recoverable
        }


class OpenFangError(Exception):
    """Base exception for OpenFang-specific errors"""

    def __init__(self, message: str, category: ErrorCategory = ErrorCategory.UNKNOWN,
                 severity: ErrorSeverity = ErrorSeverity.RECOVERABLE, **details):
        super().__init__(message)
        self.message = message
        self.category = category
        self.severity = severity
        self.details = details

    def to_error_info(self) -> ErrorInfo:
        """Convert to ErrorInfo"""
        return ErrorInfo(
            category=self.category,
            severity=self.severity,
            message=self.message,
            details=self.details,
            traceback_str=traceback.format_exc()
        )


class TranscriptError(OpenFangError):
    """Transcript-related errors"""
    def __init__(self, message: str, **details):
        super().__init__(message, ErrorCategory.TRANSCRIPT, ErrorSeverity.RECOVERABLE, **details)


class ResourceError(OpenFangError):
    """Resource unavailable errors"""
    def __init__(self, message: str, **details):
        super().__init__(message, ErrorCategory.RESOURCE, ErrorSeverity.CRITICAL, **details)


# ============================================================================
# ERROR HANDLERS
# ============================================================================

class ErrorHandler:
    """Centralized error handling and recovery"""

    def __init__(self, log_dir: Optional[Path] = None):
        """Initialize error handler"""
        self.log_dir = log_dir or Path.home() / ".openfang" / "logs"
        self.log_dir.mkdir(parents=True, exist_ok=True)
        self._setup_logging()
        self.errors: List[ErrorInfo] = []

    def _setup_logging(self):
        """Setup logging configuration"""
        log_file = self.log_dir / f"errors_{datetime.now().strftime('%Y%m%d')}.log"
        logging.basicConfig(
            level=logging.INFO,
            format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
            handlers=[
                logging.FileHandler(log_file),
                logging.StreamHandler(sys.stdout)
            ]
        )
        self.logger = logging.getLogger(__name__)

    def handle_error(self, error: Exception, context: Optional[Dict] = None) -> ErrorInfo:
        """Handle an error and create ErrorInfo"""
        context = context or {}
        if isinstance(error, OpenFangError):
            error_info = error.to_error_info()
        else:
            error_info = ErrorInfo(
                category=ErrorCategory.UNKNOWN,
                severity=ErrorSeverity.RECOVERABLE,
                message=str(error),
                traceback_str=traceback.format_exc(),
                details=context
            )
        self._log_error(error_info)
        self.errors.append(error_info)
        return error_info

    def _log_error(self, error_info: ErrorInfo):
        """Log error with appropriate level"""
        log_msg = f"[{error_info.category.value.upper()}] {error_info.message}"
        if error_info.severity == ErrorSeverity.FATAL:
            self.logger.critical(log_msg)
        elif error_info.severity == ErrorSeverity.CRITICAL:
            self.logger.error(log_msg)
        elif error_info.severity == ErrorSeverity.RECOVERABLE:
            self.logger.warning(log_msg)
        else:
            self.logger.info(log_msg)

    def get_error_summary(self) -> Dict:
        """Get summary of all errors"""
        by_category = {}
        by_severity = {}
        for error in self.errors:
            cat = error.category.value
            by_category[cat] = by_category.get(cat, 0) + 1
            sev = error.severity.value
            by_severity[sev] = by_severity.get(sev, 0) + 1
        return {
            "total_errors": len(self.errors),
            "by_category": by_category,
            "by_severity": by_severity,
            "recoverable": sum(1 for e in self.errors if e.recoverable),
            "not_recoverable": sum(1 for e in self.errors if not e.recoverable)
        }

    def save_error_report(self, output_dir: Path) -> Path:
        """Save detailed error report"""
        output_dir.mkdir(parents=True, exist_ok=True)
        report_path = output_dir / "error_report.json"
        report = {
            "timestamp": datetime.now().isoformat(),
            "summary": self.get_error_summary(),
            "errors": [e.to_dict() for e in self.errors]
        }
        with open(report_path, "w", encoding="utf-8") as f:
            json.dump(report, f, ensure_ascii=False, indent=2)
        return report_path


# ============================================================================
# CHECKPOINT SYSTEM
# ============================================================================

class CheckpointManager:
    """Manage checkpoints for long-running operations"""

    def __init__(self, checkpoint_dir: Optional[Path] = None):
        """Initialize checkpoint manager"""
        self.checkpoint_dir = checkpoint_dir or Path.home() / ".openfang" / "checkpoints"
        self.checkpoint_dir.mkdir(parents=True, exist_ok=True)

    def get_checkpoint_path(self, operation_id: str) -> Path:
        """Get checkpoint file path"""
        return self.checkpoint_dir / f"{operation_id}.checkpoint.json"

    def save_checkpoint(self, operation_id: str, data: Dict) -> None:
        """Save checkpoint data"""
        checkpoint_path = self.get_checkpoint_path(operation_id)
        checkpoint_data = {
            "operation_id": operation_id,
            "timestamp": datetime.now().isoformat(),
            "data": data
        }
        with open(checkpoint_path, "w", encoding="utf-8") as f:
            json.dump(checkpoint_data, f, ensure_ascii=False, indent=2)

    def load_checkpoint(self, operation_id: str) -> Optional[Dict]:
        """Load checkpoint data if exists"""
        checkpoint_path = self.get_checkpoint_path(operation_id)
        if not checkpoint_path.exists():
            return None
        with open(checkpoint_path, "r", encoding="utf-8") as f:
            return json.load(f)

    def has_checkpoint(self, operation_id: str) -> bool:
        """Check if checkpoint exists"""
        return self.get_checkpoint_path(operation_id).exists()

    def delete_checkpoint(self, operation_id: str) -> None:
        """Delete checkpoint after successful completion"""
        checkpoint_path = self.get_checkpoint_path(operation_id)
        if checkpoint_path.exists():
            checkpoint_path.unlink()

    def cleanup_old_checkpoints(self, max_age_hours: int = 24) -> int:
        """Clean up old checkpoint files"""
        now = time.time()
        max_age_seconds = max_age_hours * 3600
        cleaned = 0
        for checkpoint_file in self.checkpoint_dir.glob("*.checkpoint.json"):
            file_age = now - checkpoint_file.stat().st_mtime
            if file_age > max_age_seconds:
                checkpoint_file.unlink()
                cleaned += 1
        return cleaned


# ============================================================================
# RESUME SYSTEM
# ============================================================================

class ResumableOperation:
    """Base class for resumable operations"""

    def __init__(self, operation_id: str, checkpoint_manager: CheckpointManager):
        """Initialize resumable operation"""
        self.operation_id = operation_id
        self.checkpoint_manager = checkpoint_manager
        self.error_handler = ErrorHandler()
        self.current_step = 0
        self.total_steps = 0
        self.completed_steps = set()
        self.failed_steps = set()
        if self.checkpoint_manager.has_checkpoint(operation_id):
            self._load_state()

    def _load_state(self):
        """Load state from checkpoint"""
        checkpoint = self.checkpoint_manager.load_checkpoint(self.operation_id)
        if checkpoint:
            state = checkpoint.get("data", {})
            self.current_step = state.get("current_step", 0)
            self.total_steps = state.get("total_steps", 0)
            self.completed_steps = set(state.get("completed_steps", []))
            self.failed_steps = set(state.get("failed_steps", []))

    def _save_state(self):
        """Save current state to checkpoint"""
        state = {
            "current_step": self.current_step,
            "total_steps": self.total_steps,
            "completed_steps": list(self.completed_steps),
            "failed_steps": list(self.failed_steps)
        }
        self.checkpoint_manager.save_checkpoint(self.operation_id, state)

    def complete_step(self, step_id: str):
        """Mark a step as completed"""
        self.completed_steps.add(step_id)
        self.current_step += 1
        self._save_state()

    def fail_step(self, step_id: str, error: Exception):
        """Mark a step as failed"""
        self.failed_steps.add(step_id)
        self.error_handler.handle_error(error, {"step": step_id})
        self._save_state()

    def is_step_completed(self, step_id: str) -> bool:
        """Check if step is already completed"""
        return step_id in self.completed_steps

    def is_step_failed(self, step_id: str) -> bool:
        """Check if step previously failed"""
        return step_id in self.failed_steps

    def get_progress(self) -> Dict:
        """Get operation progress"""
        return {
            "operation_id": self.operation_id,
            "current_step": self.current_step,
            "total_steps": self.total_steps,
            "completed": len(self.completed_steps),
            "failed": len(self.failed_steps),
            "progress_percent": (self.current_step / self.total_steps * 100) if self.total_steps > 0 else 0
        }

    def cleanup(self):
        """Clean up checkpoint after successful completion"""
        self.checkpoint_manager.delete_checkpoint(self.operation_id)


# ============================================================================
# GRACEFUL DEGRADATION
# ============================================================================

class GracefulDegradation:
    """Handle failures gracefully with fallback strategies"""

    @staticmethod
    def with_fallback(primary_func: Callable, fallback_func: Callable,
                      error_types: tuple = (Exception,)) -> Any:
        """Execute primary function with fallback on failure"""
        try:
            return primary_func()
        except error_types as e:
            logging.warning(f"Primary function failed: {e}. Using fallback.")
            return fallback_func()

    @staticmethod
    def with_default(primary_func: Callable, default_value: Any,
                    error_types: tuple = (Exception,)) -> Any:
        """Execute primary function with default value on failure"""
        try:
            return primary_func()
        except error_types as e:
            logging.warning(f"Primary function failed: {e}. Using default value.")
            return default_value

    @staticmethod
    def retry_with_backoff(func: Callable, max_retries: int = 3,
                          backoff_factor: float = 2.0,
                          error_types: tuple = (Exception,)) -> Any:
        """Execute function with exponential backoff retry"""
        last_exception = None
        for attempt in range(max_retries + 1):
            try:
                if attempt > 0:
                    delay = backoff_factor ** (attempt - 1)
                    logging.info(f"Retry attempt {attempt + 1}/{max_retries} after {delay}s delay")
                    time.sleep(delay)
                return func()
            except error_types as e:
                last_exception = e
                if attempt < max_retries:
                    logging.warning(f"Attempt {attempt + 1} failed: {e}")
                else:
                    logging.error(f"All {max_retries} retries failed")
        raise last_exception


# ============================================================================
# DECORATORS
# ============================================================================

def handle_with_retry(func: Callable = None, max_retries: int = 3,
                       error_types: tuple = (Exception,)):
    """Decorator for automatic retry with backoff"""
    def decorator(f):
        def wrapper(*args, **kwargs):
            return GracefulDegradation.retry_with_backoff(
                lambda: f(*args, **kwargs),
                max_retries=max_retries,
                error_types=error_types
            )
        return wrapper
    if func is None:
        # Called with arguments
        return decorator
    else:
        # Called without arguments
        return decorator(func)


# ============================================================================
# VALIDATION
# ============================================================================

class ValidatedOperation:
    """Operation with input validation and recovery"""

    def __init__(self, error_handler: ErrorHandler):
        """Initialize validated operation"""
        self.error_handler = error_handler
        self.warnings = []
        self.fixes_applied = []

    def validate_transcript(self, transcript_path: Path) -> bool:
        """Validate transcript file with recovery attempts"""
        if not transcript_path.exists():
            self.error_handler.handle_error(
                TranscriptError(f"Transcript not found: {transcript_path}"),
                {"file": str(transcript_path)}
            )
            return self._try_find_alternative_transcript(transcript_path)

        file_size = transcript_path.stat().st_size
        if file_size == 0:
            self.error_handler.handle_error(
                TranscriptError(f"Transcript is empty: {transcript_path}"),
                {"file": str(transcript_path), "size": file_size}
            )
            return False

        if file_size < 50:
            self.warnings.append(f"Transcript is very small ({file_size} bytes)")

        try:
            from auto_clip import build_transcript_payload
            payload = build_transcript_payload(transcript_path)
            if not payload.get("text"):
                self.error_handler.handle_error(
                    TranscriptError(f"Transcript parsing failed: {transcript_path}"),
                    {"file": str(transcript_path)}
                )
                return False
            return True
        except Exception as e:
            self.error_handler.handle_error(e, {"file": str(transcript_path)})
            return False

    def _try_find_alternative_transcript(self, original_path: Path) -> bool:
        """Try to find alternative transcript file"""
        alternatives = [
            original_path.with_suffix(".txt"),
            original_path.with_suffix(".md"),
            original_path.with_suffix(".vtt"),
        ]
        for alt_path in alternatives:
            if alt_path.exists():
                self.warnings.append(f"Using alternative: {alt_path.name}")
                self.fixes_applied.append({
                    "type": "alternative_file",
                    "original": str(original_path),
                    "alternative": str(alt_path)
                })
                return True
        return False

    def validate_ffmpeg(self) -> bool:
        """Validate FFmpeg availability"""
        import shutil
        if not shutil.which("ffmpeg"):
            self.error_handler.handle_error(
                ResourceError("FFmpeg not found in PATH"),
                {"required": True}
            )
            return False
        return True

    def get_report(self) -> Dict:
        """Get validation report"""
        return {
            "warnings": self.warnings,
            "fixes_applied": self.fixes_applied,
            "errors_count": len(self.error_handler.errors),
            "can_proceed": len([e for e in self.error_handler.errors
                             if e.severity in [ErrorSeverity.CRITICAL, ErrorSeverity.FATAL]]) == 0
        }


# ============================================================================
# PARTIAL RECOVERY
# ============================================================================

class PartialRecoveryManager:
    """Manage partial recovery and save results even if some steps fail"""

    def __init__(self, output_dir: Path):
        """Initialize partial recovery manager"""
        self.output_dir = output_dir
        self.partial_results = {}
        self.failed_operations = []

    def save_partial_result(self, key: str, value: Any, metadata: Dict = None):
        """Save a partial result"""
        self.partial_results[key] = {
            "value": value,
            "metadata": metadata or {},
            "timestamp": datetime.now().isoformat()
        }

    def record_failure(self, operation: str, error: Exception):
        """Record a failed operation"""
        self.failed_operations.append({
            "operation": operation,
            "error": str(error),
            "timestamp": datetime.now().isoformat()
        })

    def has_partial_results(self) -> bool:
        """Check if any partial results exist"""
        return len(self.partial_results) > 0

    def save_partial_package(self) -> Path:
        """Save partial package even if some operations failed"""
        partial_dir = self.output_dir / "partial"
        partial_dir.mkdir(parents=True, exist_ok=True)

        partial_package = {
            "status": "partial",
            "timestamp": datetime.now().isoformat(),
            "succeeded": list(self.partial_results.keys()),
            "failed": [op["operation"] for op in self.failed_operations],
            "results": self.partial_results,
            "completion_rate": len(self.partial_results) / max(len(self.partial_results) + len(self.failed_operations), 1)
        }

        partial_file = partial_dir / f"partial_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json"
        with open(partial_file, "w", encoding="utf-8") as f:
            json.dump(partial_package, f, ensure_ascii=False, indent=2)

        return partial_file

    def get_recovery_summary(self) -> Dict:
        """Get summary of what was recovered"""
        total = len(self.partial_results) + len(self.failed_operations)
        return {
            "succeeded_count": len(self.partial_results),
            "failed_count": len(self.failed_operations),
            "total_operations": total,
            "completion_rate": len(self.partial_results) / max(total, 1),
            "can_use_partial": len(self.partial_results) >= 1
        }


# ============================================================================
# CONTEXT MANAGER
# ============================================================================

@contextmanager
def error_handling_context(operation_name: str,
                         output_dir: Optional[Path] = None,
                         save_on_error: bool = True):
    """Context manager for comprehensive error handling"""
    error_handler = ErrorHandler(output_dir)
    checkpoint_manager = CheckpointManager()
    partial_recovery = PartialRecoveryManager(output_dir) if output_dir else None

    try:
        yield {
            "error_handler": error_handler,
            "checkpoint_manager": checkpoint_manager,
            "partial_recovery": partial_recovery
        }
    except Exception as e:
        error_info = error_handler.handle_error(e, {"operation": operation_name})
        if partial_recovery and partial_recovery.has_partial_results():
            partial_file = partial_recovery.save_partial_package()
            logging.info(f"Partial results saved to: {partial_file}")
        if output_dir:
            error_file = error_handler.save_error_report(output_dir)
            logging.info(f"Error report saved to: {error_file}")
        if error_info.severity == ErrorSeverity.FATAL:
            raise
    finally:
        checkpoint_manager.cleanup_old_checkpoints()


# ============================================================================
# EXPORTS
# ============================================================================

__all__ = [
    'ErrorSeverity', 'ErrorCategory', 'ErrorInfo',
    'OpenFangError', 'TranscriptError', 'ResourceError',
    'ErrorHandler', 'CheckpointManager', 'ResumableOperation',
    'GracefulDegradation', 'ValidatedOperation', 'PartialRecoveryManager',
    'error_handling_context', 'handle_with_retry',
]
