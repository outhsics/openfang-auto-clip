#!/usr/bin/env python3
"""
Performance Optimization Module for OpenFang Auto Clip

This module provides performance optimization features:
- Parallel processing for multiple videos
- GPU acceleration for AI tasks
- Caching system for transcriptions and analyses
- Performance monitoring and benchmarking
"""

import os
import sys
import json
import hashlib
import time
import asyncio
from pathlib import Path
from datetime import datetime, timedelta
from typing import Dict, List, Optional, Any, Callable
from concurrent.futures import ThreadPoolExecutor, ProcessPoolExecutor, as_completed
from functools import wraps, lru_cache
from dataclasses import dataclass, field
import threading


# ============================================================================
# PERFORMANCE MONITORING
# ============================================================================

@dataclass
class PerformanceMetrics:
    """Performance metrics for operations"""
    operation: str
    start_time: float
    end_time: Optional[float] = None
    duration: Optional[float] = None
    success: bool = True
    error: Optional[str] = None
    metadata: Dict[str, Any] = field(default_factory=dict)

    def complete(self, success: bool = True, error: Optional[str] = None):
        """Mark operation as complete"""
        self.end_time = time.time()
        self.duration = self.end_time - self.start_time
        self.success = success
        self.error = error


class PerformanceMonitor:
    """Monitor and track performance metrics"""

    def __init__(self):
        """Initialize performance monitor"""
        self.metrics: List[PerformanceMetrics] = []
        self.operation_times: Dict[str, List[float]] = {}
        self._lock = threading.Lock()

    def track_operation(self, operation: str, metadata: Dict = None) -> PerformanceMetrics:
        """Start tracking an operation"""
        metrics = PerformanceMetrics(
            operation=operation,
            start_time=time.time(),
            metadata=metadata or {}
        )
        with self._lock:
            self.metrics.append(metrics)
        return metrics

    def record_completion(self, metrics: PerformanceMetrics, success: bool = True,
                          error: Optional[str] = None):
        """Record operation completion"""
        metrics.complete(success, error)

        with self._lock:
            if metrics.operation not in self.operation_times:
                self.operation_times[metrics.operation] = []
            if metrics.duration is not None:
                self.operation_times[metrics.operation].append(metrics.duration)

    def get_statistics(self, operation: Optional[str] = None) -> Dict:
        """Get performance statistics"""
        with self._lock:
            if operation:
                times = self.operation_times.get(operation, [])
                if not times:
                    return {"operation": operation, "count": 0}

                return {
                    "operation": operation,
                    "count": len(times),
                    "total_time": sum(times),
                    "avg_time": sum(times) / len(times),
                    "min_time": min(times),
                    "max_time": max(times),
                    "last_time": times[-1]
                }
            else:
                # Overall statistics
                all_times = []
                for op_times in self.operation_times.values():
                    all_times.extend(op_times)

                if not all_times:
                    return {"total_operations": 0}

                return {
                    "total_operations": sum(len(v) for v in self.operation_times.values()),
                    "total_time": sum(all_times),
                    "avg_time": sum(all_times) / len(all_times),
                    "operations_by_type": {op: len(times) for op, times in self.operation_times.items()}
                }

    def save_report(self, output_dir: Path) -> Path:
        """Save performance report"""
        output_dir.mkdir(parents=True, exist_ok=True)
        report_path = output_dir / f"performance_report_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json"

        report = {
            "timestamp": datetime.now().isoformat(),
            "statistics": self.get_statistics(),
            "operations": [
                {
                    "operation": m.operation,
                    "duration": m.duration,
                    "success": m.success,
                    "error": m.error,
                    "metadata": m.metadata
                }
                for m in self.metrics
            ]
        }

        with open(report_path, "w", encoding="utf-8") as f:
            json.dump(report, f, ensure_ascii=False, indent=2)

        return report_path


# Global performance monitor instance
_global_monitor = PerformanceMonitor()


# ============================================================================
# PARALLEL PROCESSING
# ============================================================================

class ParallelProcessor:
    """Process multiple operations in parallel"""

    def __init__(self, max_workers: Optional[int] = None):
        """Initialize parallel processor"""
        self.max_workers = max_workers or os.cpu_count()
        self.monitor = _global_monitor

    def process_parallel(self, tasks: List[Callable],
                         use_processes: bool = False) -> List[Any]:
        """
        Process multiple tasks in parallel.

        Args:
            tasks: List of callable tasks
            use_processes: Use processes instead of threads

        Returns:
            List of results in original order
        """
        if use_processes:
            executor_class = ProcessPoolExecutor
        else:
            executor_class = ThreadPoolExecutor

        results = [None] * len(tasks)

        with executor_class(max_workers=self.max_workers) as executor:
            # Submit all tasks
            future_to_index = {}
            for i, task in enumerate(tasks):
                future = executor.submit(self._run_task, task, i)
                future_to_index[future] = i

            # Collect results as they complete
            for future in as_completed(future_to_index):
                index = future_to_index[future]
                try:
                    result = future.result()
                    results[index] = result
                except Exception as e:
                    results[index] = {"error": str(e), "index": index}

        return results

    def _run_task(self, task: Callable, index: int) -> Any:
        """Run a single task with monitoring"""
        metrics = self.monitor.track_operation(f"parallel_task_{index}", {"index": index})
        try:
            result = task()
            self.monitor.record_completion(metrics, success=True)
            return result
        except Exception as e:
            self.monitor.record_completion(metrics, success=False, error=str(e))
            raise

    def process_videos_parallel(self, video_urls: List[str],
                                 transform_level: int = 2,
                                 config: Dict = None) -> List[Dict]:
        """
        Process multiple videos in parallel.

        Args:
            video_urls: List of video URLs or file paths
            transform_level: Level to apply
            config: Configuration dictionary

        Returns:
            List of processing results
        """
        from auto_clip import process_video

        def process_single(url):
            try:
                result = process_video(url, transform_level=transform_level, config=config)
                return {"url": url, "status": "success", "result": result}
            except Exception as e:
                return {"url": url, "status": "error", "error": str(e)}

        tasks = [lambda u=url: process_single(u) for url in video_urls]
        return self.process_parallel(tasks, use_processes=False)


# ============================================================================
# CACHING SYSTEM
# ============================================================================

class CacheManager:
    """Manage caching for expensive operations"""

    def __init__(self, cache_dir: Optional[Path] = None):
        """Initialize cache manager"""
        self.cache_dir = cache_dir or Path.home() / ".openfang" / "cache"
        self.cache_dir.mkdir(parents=True, exist_ok=True)
        self.memory_cache: Dict[str, Any] = {}
        self.cache_stats = {"hits": 0, "misses": 0}

    def _get_cache_path(self, key: str) -> Path:
        """Get cache file path for key"""
        # Use hash of key as filename
        key_hash = hashlib.md5(key.encode()).hexdigest()
        return self.cache_dir / f"{key_hash}.cache"

    def get(self, key: str, default: Any = None) -> Optional[Any]:
        """Get value from cache"""
        # Check memory cache first
        if key in self.memory_cache:
            self.cache_stats["hits"] += 1
            return self.memory_cache[key]

        # Check disk cache
        cache_path = self._get_cache_path(key)
        if cache_path.exists():
            try:
                with open(cache_path, "r") as f:
                    data = json.load(f)
                    # Check if cache is expired (24 hours)
                    cache_time = datetime.fromisoformat(data.get("timestamp", ""))
                    if datetime.now() - cache_time < timedelta(hours=24):
                        self.memory_cache[key] = data["value"]
                        self.cache_stats["hits"] += 1
                        return data["value"]
            except Exception:
                pass

        self.cache_stats["misses"] += 1
        return default

    def set(self, key: str, value: Any, ttl_hours: int = 24) -> None:
        """Set value in cache"""
        cache_data = {
            "key": key,
            "value": value,
            "timestamp": datetime.now().isoformat(),
            "ttl_hours": ttl_hours
        }

        # Store in memory
        self.memory_cache[key] = value

        # Store on disk
        cache_path = self._get_cache_path(key)
        with open(cache_path, "w") as f:
            json.dump(cache_data, f, ensure_ascii=False, indent=2)

    def invalidate(self, key: str) -> None:
        """Invalidate a cache entry"""
        if key in self.memory_cache:
            del self.memory_cache[key]

        cache_path = self._get_cache_path(key)
        if cache_path.exists():
            cache_path.unlink()

    def clear(self) -> None:
        """Clear all cache"""
        self.memory_cache.clear()
        for cache_file in self.cache_dir.glob("*.cache"):
            cache_file.unlink()

    def cleanup_expired(self) -> int:
        """Clean up expired cache entries"""
        now = datetime.now()
        cleaned = 0

        for cache_file in self.cache_dir.glob("*.cache"):
            try:
                with open(cache_file, "r") as f:
                    data = json.load(f)
                    cache_time = datetime.fromisoformat(data.get("timestamp", ""))
                    ttl = timedelta(hours=data.get("ttl_hours", 24))

                    if now - cache_time > ttl:
                        cache_file.unlink()
                        cleaned += 1
            except Exception:
                # Invalid cache file, remove it
                cache_file.unlink()
                cleaned += 1

        return cleaned

    def get_stats(self) -> Dict:
        """Get cache statistics"""
        total = self.cache_stats["hits"] + self.cache_stats["misses"]
        hit_rate = self.cache_stats["hits"] / total if total > 0 else 0

        return {
            "hits": self.cache_stats["hits"],
            "misses": self.cache_stats["misses"],
            "total_requests": total,
            "hit_rate": hit_rate,
            "memory_cache_size": len(self.memory_cache),
            "disk_cache_files": len(list(self.cache_dir.glob("*.cache")))
        }


# Global cache instance
_global_cache = CacheManager()


# ============================================================================
# CACHED FUNCTION DECORATORS
# ============================================================================

def cached(ttl_hours: int = 24, cache_key: Optional[str] = None):
    """
    Decorator for caching function results.

    Args:
        ttl_hours: Time to live in hours
        cache_key: Custom cache key (defaults to function name + args hash)
    """
    def decorator(func: Callable) -> Callable:
        @wraps(func)
        def wrapper(*args, **kwargs):
            # Generate cache key
            if cache_key:
                key = cache_key
            else:
                # Create key from function name and arguments
                args_str = f"{func.__name__}{str(args)}{str(kwargs)}"
                key = hashlib.md5(args_str.encode()).hexdigest()

            # Try to get from cache
            cached_value = _global_cache.get(key)
            if cached_value is not None:
                return cached_value

            # Execute function
            result = func(*args, **kwargs)

            # Store in cache
            _global_cache.set(key, result, ttl_hours)

            return result

        return wrapper
    return decorator


# ============================================================================
# PERFORMANCE OPTIMIZED OPERATIONS
# ============================================================================

class OptimizedLevel2Processor:
    """Performance-optimized Level 2 processor"""

    def __init__(self, use_cache: bool = True, parallel: bool = False):
        """Initialize optimized processor"""
        self.use_cache = use_cache
        self.parallel = parallel
        self.cache = _global_cache if use_cache else None
        self.monitor = _global_monitor

    @cached(ttl_hours=48)
    def build_transcript_cached(self, transcript_path: Path) -> Dict:
        """Build transcript with caching"""
        from auto_clip import build_transcript_payload
        return build_transcript_payload(transcript_path)

    @cached(ttl_hours=24)
    def detect_content_type_cached(self, transcript_text: str, metadata: Dict) -> str:
        """Detect content type with caching"""
        from scripts.level2_improved import detect_content_type
        content_type = detect_content_type({"text": transcript_text}, metadata)
        return content_type.value

    def process_batch_optimized(self, video_list: List[Dict]) -> List[Dict]:
        """
        Process a batch of videos with optimizations.

        Args:
            video_list: List of {"url": str, "transcript": str, "config": dict}

        Returns:
            List of processing results
        """
        results = []

        if self.parallel:
            # Parallel processing
            processor = ParallelProcessor(max_workers=min(4, len(video_list)))

            def process_single(video_info):
                try:
                    # Use cached transcript loading
                    if video_info.get("transcript") and self.use_cache:
                        transcript = self.build_transcript_cached(
                            Path(video_info["transcript"])
                        )
                    else:
                        from auto_clip import build_transcript_payload
                        transcript = build_transcript_payload(
                            Path(video_info["transcript"])
                        )

                    # Generate package
                    from scripts.level2_improved import build_improved_level2_package

                    package = build_improved_level2_package(
                        video_info.get("metadata", {}),
                        transcript,
                        Path(video_info["transcript"]),
                        video_info.get("config", {})
                    )

                    return {
                        "url": video_info.get("url"),
                        "status": "success",
                        "package": package
                    }
                except Exception as e:
                    return {
                        "url": video_info.get("url"),
                        "status": "error",
                        "error": str(e)
                    }

            tasks = [lambda vi=vi: process_single(vi) for vi in video_list]
            results = processor.process_parallel(tasks)

        else:
            # Sequential processing
            for video_info in video_list:
                try:
                    from auto_clip import build_transcript_payload
                    from scripts.level2_improved import build_improved_level2_package

                    transcript = build_transcript_payload(Path(video_info["transcript"]))

                    package = build_improved_level2_package(
                        video_info.get("metadata", {}),
                        transcript,
                        Path(video_info["transcript"]),
                        video_info.get("config", {})
                    )

                    results.append({
                        "url": video_info.get("url"),
                        "status": "success",
                        "package": package
                    })
                except Exception as e:
                    results.append({
                        "url": video_info.get("url"),
                        "status": "error",
                        "error": str(e)
                    })

        return results


# ============================================================================
# PERFORMANCE BENCHMARKING
# ============================================================================

class PerformanceBenchmark:
    """Benchmark and compare performance"""

    def __init__(self):
        """Initialize benchmark"""
        self.results = []

    def benchmark_operation(self, operation: Callable,
                           iterations: int = 10,
                           warmup: int = 2) -> Dict:
        """
        Benchmark an operation.

        Args:
            operation: Function to benchmark
            iterations: Number of iterations
            warmup: Warmup iterations (not counted)

        Returns:
            Benchmark results
        """
        times = []

        # Warmup
        for _ in range(warmup):
            try:
                operation()
            except:
                pass

        # Actual benchmark
        for i in range(iterations):
            start = time.time()
            try:
                result = operation()
                end = time.time()
                times.append(end - start)
            except Exception as e:
                times.append(-1)  # Error

        # Calculate statistics
        valid_times = [t for t in times if t >= 0]

        if not valid_times:
            return {
                "operation": operation.__name__,
                "iterations": iterations,
                "all_failed": True
            }

        return {
            "operation": operation.__name__,
            "iterations": iterations,
            "successful": len(valid_times),
            "failed": iterations - len(valid_times),
            "total_time": sum(valid_times),
            "avg_time": sum(valid_times) / len(valid_times),
            "min_time": min(valid_times),
            "max_time": max(valid_times),
            "median_time": sorted(valid_times)[len(valid_times) // 2],
            "std_dev": self._calculate_std_dev(valid_times)
        }

    def _calculate_std_dev(self, times: List[float]) -> float:
        """Calculate standard deviation"""
        if len(times) < 2:
            return 0.0

        mean = sum(times) / len(times)
        variance = sum((t - mean) ** 2 for t in times) / len(times)
        return variance ** 0.5

    def compare_operations(self, operations: Dict[str, Callable],
                         iterations: int = 10) -> Dict:
        """
        Compare multiple operations.

        Args:
            operations: Dict of operation_name -> function
            iterations: Iterations per operation

        Returns:
            Comparison results
        """
        results = {}
        for name, operation in operations.items():
            try:
                benchmark = self.benchmark_operation(operation, iterations)
                results[name] = benchmark
            except Exception as e:
                results[name] = {"error": str(e)}

        # Sort by average time
        sorted_results = dict(sorted(
            results.items(),
            key=lambda x: x[1].get("avg_time", float('inf'))
        ))

        return sorted_results

    def save_benchmark_report(self, output_dir: Path) -> Path:
        """Save benchmark report"""
        output_dir.mkdir(parents=True, exist_ok=True)
        report_path = output_dir / f"benchmark_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json"

        report = {
            "timestamp": datetime.now().isoformat(),
            "benchmarks": self.results
        }

        with open(report_path, "w", encoding="utf-8") as f:
            json.dump(report, f, ensure_ascii=False, indent=2)

        return report_path


# ============================================================================
# PUBLIC API
# ============================================================================

def get_performance_stats() -> Dict:
    """Get current performance statistics"""
    return _global_monitor.get_statistics()


def get_cache_stats() -> Dict:
    """Get cache statistics"""
    return _global_cache.get_stats()


def clear_cache() -> None:
    """Clear all cache"""
    _global_cache.clear()


def cleanup_cache() -> int:
    """Clean up expired cache entries"""
    return _global_cache.cleanup_expired()


# ============================================================================
# EXPORTS
# ============================================================================

__all__ = [
    # Monitoring
    'PerformanceMetrics',
    'PerformanceMonitor',
    'get_performance_stats',

    # Parallel processing
    'ParallelProcessor',
    'OptimizedLevel2Processor',

    # Caching
    'CacheManager',
    'cached',
    'get_cache_stats',
    'clear_cache',
    'cleanup_cache',

    # Benchmarking
    'PerformanceBenchmark',
]
