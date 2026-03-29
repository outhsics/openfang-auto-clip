#!/usr/bin/env python3
"""
Automated Testing and Quality Validation System

This module provides comprehensive automated testing and quality validation
for the OpenFang Auto Clip Level 2 pipeline.

Features:
- Automated test suite
- Quality benchmarking
- Regression testing
- Continuous integration support
"""

import os
import sys
import json
import subprocess
from pathlib import Path
from datetime import datetime
from typing import Dict, List, Optional, Tuple
from dataclasses import dataclass, field
import traceback


# ============================================================================
# TEST FRAMEWORK
# ============================================================================

@dataclass
class TestCase:
    """Test case definition"""
    name: str
    description: str
    category: str
    test_func: callable
    timeout: int = 300  # seconds

    def __post_init__(self):
        self.result = None
        self.error = None


@dataclass
class TestResult:
    """Test result"""
    test_name: str
    passed: bool
    duration: float
    output: str
    error: Optional[str] = None
    metadata: Dict = field(default_factory=dict)


class TestSuite:
    """Test suite for running tests"""

    def __init__(self, name: str):
        """Initialize test suite"""
        self.name = name
        self.tests: List[TestCase] = []
        self.results: List[TestResult] = []

    def add_test(self, name: str, description: str, category: str,
                test_func: callable, timeout: int = 300):
        """Add a test to the suite"""
        test = TestCase(name, description, category, test_func, timeout)
        self.tests.append(test)

    def run(self) -> Dict:
        """Run all tests in the suite"""
        self.results = []
        passed = 0
        failed = 0
        skipped = 0

        print(f"\n{'='*70}")
        print(f"Running Test Suite: {self.name}")
        print(f"Total Tests: {len(self.tests)}")
        print('='*70)

        for test in self.tests:
            print(f"\n📋 Test: {test.name}")
            print(f"   {test.description}")
            print(f"   Category: {test.category}")

            start_time = __import__('time').time()
            try:
                # Run test with timeout
                import signal

                def timeout_handler(signum, frame):
                    raise TimeoutError(f"Test timed out after {test.timeout}s")

                signal.signal(signal.SIGALRM, timeout_handler)
                signal.alarm(test.timeout)

                try:
                    test_output = test.test_func()
                    duration = __import__('time').time() - start_time
                    self.results.append(TestResult(
                        test_name=test.name,
                        passed=True,
                        duration=duration,
                        output=str(test_output)
                    ))
                    passed += 1
                    print(f"   ✅ PASSED ({duration:.2f}s)")
                finally:
                    signal.alarm(0)  # Disable alarm

            except TimeoutError as e:
                duration = __import__('time').time() - start_time
                self.results.append(TestResult(
                    test_name=test.name,
                    passed=False,
                    duration=duration,
                    output="",
                    error=str(e)
                ))
                failed += 1
                print(f"   ❌ FAILED: {e}")

            except Exception as e:
                duration = __import__('time').time() - start_time
                error_str = traceback.format_exc()
                self.results.append(TestResult(
                    test_name=test.name,
                    passed=False,
                    duration=duration,
                    output="",
                    error=error_str
                ))
                failed += 1
                print(f"   ❌ FAILED: {e}")

        print(f"\n{'='*70}")
        print(f"Test Suite Results: {self.name}")
        print('='*70)
        print(f"✅ Passed: {passed}")
        print(f"❌ Failed: {failed}")
        print(f"⏭️  Skipped: {skipped}")
        print(f"📊 Pass Rate: {passed/(passed+failed)*100:.1f}%")

        return {
            "suite_name": self.name,
            "total_tests": len(self.tests),
            "passed": passed,
            "failed": failed,
            "skipped": skipped,
            "pass_rate": passed/(passed+failed) if (passed+failed) > 0 else 0,
            "results": [r.__dict__ for r in self.results]
        }


# ============================================================================
# LEVEL 2 SPECIFIC TESTS
# ============================================================================

class Level2TestSuite(TestSuite):
    """Test suite for Level 2 functionality"""

    def __init__(self):
        """Initialize Level 2 test suite"""
        super().__init__("Level 2 Tests")
        self._setup_tests()

    def _setup_tests(self):
        """Setup all tests"""
        self._add_unit_tests()
        self._add_integration_tests()
        self._add_quality_tests()

    def _add_unit_tests(self):
        """Add unit tests"""

        def test_transcript_parsing():
            """Test transcript parsing"""
            from auto_clip import build_transcript_payload
            from pathlib import Path

            # Find demo transcript
            repo_root = Path(__file__).parent.parent
            demo_file = repo_root / "examples" / "demo" / "sample_level2_transcript.srt"

            if not demo_file.exists():
                return "Demo file not found"

            payload = build_transcript_payload(demo_file)

            assert payload is not None, "Payload should not be None"
            assert "text" in payload, "Payload should have text"
            assert len(payload["text"]) > 0, "Text should not be empty"

            return f"Parsed {len(payload['text'])} characters"

        self.add_test(
            "transcript_parsing",
            "Test transcript parsing from SRT files",
            "unit",
            test_transcript_parsing
        )

        def test_content_type_detection():
            """Test content type detection"""
            from scripts.level2_improved import detect_content_type, ContentType

            # Educational content
            edu_transcript = {
                "text": "This tutorial will teach you how to learn Python programming effectively.",
                "metadata": {"title": "Python Tutorial"}
            }
            content_type = detect_content_type(edu_transcript, edu_transcript["metadata"])
            assert content_type == ContentType.TUTORIAL, f"Expected TUTORIAL, got {content_type}"

            return "Content type detection works"

        self.add_test(
            "content_type_detection",
            "Test automatic content type detection",
            "unit",
            test_content_type_detection
        )

    def _add_integration_tests(self):
        """Add integration tests"""

        def test_level2_generation():
            """Test Level 2 package generation"""
            from scripts.level2_improved import build_improved_level2_package
            from auto_clip import build_transcript_payload, OUTPUT_DIR
            from pathlib import Path

            repo_root = Path(__file__).parent.parent
            demo_file = repo_root / "examples" / "demo" / "sample_level2_transcript.srt"

            if not demo_file.exists():
                return "Demo file not found"

            transcript = build_transcript_payload(demo_file)
            video_info = {"title": "Test Video", "path": str(demo_file)}

            package = build_improved_level2_package(
                video_info,
                transcript,
                demo_file,
                {"default_duration": 60}
            )

            assert package is not None, "Package should not be None"
            assert "script_sections" in package, "Package should have sections"
            assert len(package["script_sections"]) > 0, "Should have at least one section"

            return f"Generated {len(package['script_sections'])} sections"

        self.add_test(
            "level2_generation",
            "Test complete Level 2 package generation",
            "integration",
            test_level2_generation
        )

    def _add_quality_tests(self):
        """Add quality validation tests"""

        def test_quality_scoring():
            """Test quality scoring system"""
            from scripts.level2_validation import calculate_quality_scores

            # Create test package
            test_package = {
                "script_sections": [
                    {
                        "section": "Hook",
                        "duration": 10,
                        "narration": "Test hook for engagement",
                        "on_screen_text": "Hook Text",
                        "visual_direction": "Test direction"
                    },
                    {
                        "section": "Body",
                        "duration": 30,
                        "narration": "Test body content",
                        "on_screen_text": "Body Text",
                        "visual_direction": "Test direction"
                    },
                    {
                        "section": "Close",
                        "duration": 10,
                        "narration": "Test closing statement",
                        "on_screen_text": "CTA Text",
                        "visual_direction": "Test direction"
                    }
                ]
            }

            scores = calculate_quality_scores(test_package, "Original transcript text for testing")

            assert scores is not None, "Scores should not be None"
            assert "overall" in scores, "Should have overall score"
            assert 0 <= scores["overall"] <= 10, "Score should be 0-10"

            return f"Overall score: {scores['overall']}/10"

        self.add_test(
            "quality_scoring",
            "Test multi-dimensional quality scoring",
            "quality",
            test_quality_scoring
        )


# ============================================================================
# REGRESSION TESTING
# ============================================================================

class RegressionTester:
    """Test for regressions compared to baseline"""

    def __init__(self, baseline_dir: Optional[Path] = None):
        """Initialize regression tester"""
        self.baseline_dir = baseline_dir or Path.home() / ".openfang" / "baselines"
        self.baseline_dir.mkdir(parents=True, exist_ok=True)

    def create_baseline(self, name: str, data: Dict) -> Path:
        """Create a baseline"""
        baseline_path = self.baseline_dir / f"{name}.baseline.json"
        baseline_data = {
            "name": name,
            "timestamp": datetime.now().isoformat(),
            "data": data
        }
        with open(baseline_path, "w", encoding="utf-8") as f:
            json.dump(baseline_data, f, ensure_ascii=False, indent=2)
        return baseline_path

    def load_baseline(self, name: str) -> Optional[Dict]:
        """Load a baseline"""
        baseline_path = self.baseline_dir / f"{name}.baseline.json"
        if not baseline_path.exists():
            return None
        with open(baseline_path, "r", encoding="utf-8") as f:
            return json.load(f)

    def compare_with_baseline(self, name: str, current_data: Dict,
                            tolerance: float = 0.1) -> Dict:
        """
        Compare current data with baseline.

        Args:
            name: Baseline name
            current_data: Current data to compare
            tolerance: Acceptable difference (10% default)

        Returns:
            Comparison results
        """
        baseline = self.load_baseline(name)
        if not baseline:
            return {"status": "no_baseline", "message": "No baseline found"}

        baseline_data = baseline["data"]
        results = {
            "name": name,
            "status": "ok",
            "differences": []
        }

        # Compare numeric values
        for key in set(list(baseline_data.keys()) + list(current_data.keys())):
            baseline_val = baseline_data.get(key)
            current_val = current_data.get(key)

            if isinstance(baseline_val, (int, float)) and isinstance(current_val, (int, float)):
                diff = abs(current_val - baseline_val)
                baseline_val = baseline_val or 1  # Avoid division by zero
                pct_diff = diff / abs(baseline_val)

                if pct_diff > tolerance:
                    results["differences"].append({
                        "metric": key,
                        "baseline": baseline_val,
                        "current": current_val,
                        "difference": diff,
                        "percent_difference": pct_diff
                    })

        if results["differences"]:
            results["status"] = "regression"

        return results


# ============================================================================
# AUTOMATED TEST RUNNER
# ============================================================================

class AutomatedTestRunner:
    """Automated test runner with reporting"""

    def __init__(self):
        """Initialize test runner"""
        self.suites: List[TestSuite] = []
        self.all_results = []

    def add_suite(self, suite: TestSuite):
        """Add a test suite"""
        self.suites.append(suite)

    def run_all(self) -> Dict:
        """Run all test suites"""
        print("\n" + "="*70)
        print("🧪 Automated Test Runner")
        print("🧪 自动化测试运行器")
        print("="*70)

        all_results = []
        total_passed = 0
        total_failed = 0

        for suite in self.suites:
            result = suite.run()
            all_results.append(result)
            total_passed += result["passed"]
            total_failed += result["failed"]

        # Overall summary
        print(f"\n{'='*70}")
        print("📊 Overall Test Results")
        print('='*70)
        print(f"Total Suites: {len(self.suites)}")
        print(f"Total Tests: {sum(s['total_tests'] for s in all_results)}")
        print(f"✅ Passed: {total_passed}")
        print(f"❌ Failed: {total_failed}")
        print(f"📊 Pass Rate: {total_passed/(total_passed+total_failed)*100:.1f}%")

        return {
            "timestamp": datetime.now().isoformat(),
            "total_suites": len(self.suites),
            "total_tests": sum(s['total_tests'] for s in all_results),
            "total_passed": total_passed,
            "total_failed": total_failed,
            "pass_rate": total_passed/(total_passed+total_failed) if (total_passed+total_failed) > 0 else 0,
            "suite_results": all_results
        }

    def save_report(self, output_dir: Path) -> Path:
        """Save test report"""
        output_dir.mkdir(parents=True, exist_ok=True)
        report_path = output_dir / f"test_report_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json"

        report = {
            "timestamp": datetime.now().isoformat(),
            "results": self.all_results
        }

        with open(report_path, "w", encoding="utf-8") as f:
            json.dump(report, f, ensure_ascii=False, indent=2)

        return report_path


# ============================================================================
# QUALITY BENCHMARKS
# ============================================================================

class QualityBenchmark:
    """Benchmark and validate quality standards"""

    def __init__(self):
        """Initialize quality benchmark"""
        self.benchmarks = {}

    def run_level2_quality_benchmark(self) -> Dict:
        """
        Run comprehensive Level 2 quality benchmark.

        Tests:
        - Processing speed
        - Quality scores
        - Resource usage
        """
        print("\n" + "="*70)
        print("📊 Level 2 Quality Benchmark")
        print("📊 Level 2 质量基准测试")
        print("="*70)

        results = {}

        # Test 1: Processing Speed
        print("\n📈 Test 1: Processing Speed")
        results["processing_speed"] = self._benchmark_processing_speed()

        # Test 2: Quality Scores
        print("\n📈 Test 2: Quality Scores")
        results["quality_scores"] = self._benchmark_quality_scores()

        # Test 3: Resource Usage
        print("\n📈 Test 3: Resource Usage")
        results["resource_usage"] = self._benchmark_resource_usage()

        # Overall assessment
        print(f"\n{'='*70}")
        print("📊 Benchmark Summary")
        print('='*70)

        for test_name, test_results in results.items():
            status = "✅ PASS" if test_results.get("passed") else "❌ FAIL"
            print(f"{status} {test_name}")

        return results

    def _benchmark_processing_speed(self) -> Dict:
        """Benchmark processing speed"""
        import time
        from scripts.level2_improved import build_improved_level2_package
        from auto_clip import build_transcript_payload, OUTPUT_DIR
        from pathlib import Path

        repo_root = Path(__file__).parent.parent
        demo_file = repo_root / "examples" / "demo" / "sample_level2_transcript.srt"

        if not demo_file.exists():
            return {"passed": False, "error": "Demo file not found"}

        # Test processing speed
        start = time.time()
        transcript = build_transcript_payload(demo_file)
        video_info = {"title": "Benchmark Test", "path": str(demo_file)}
        package = build_improved_level2_package(video_info, transcript, demo_file, {"default_duration": 60})
        duration = time.time() - start

        # Target: <5 seconds for demo
        target = 5.0
        passed = duration < target

        print(f"   Duration: {duration:.2f}s")
        print(f"   Target: <{target}s")
        print(f"   Status: {'✅ PASS' if passed else '❌ FAIL'}")

        return {
            "passed": passed,
            "duration": duration,
            "target": target,
            "within_tolerance": duration < target * 1.2  # 20% tolerance
        }

    def _benchmark_quality_scores(self) -> Dict:
        """Benchmark quality scores"""
        from scripts.level2_validation import calculate_quality_scores

        # Create test package
        test_package = {
            "script_sections": [
                {
                    "section": "Hook",
                    "duration": 10,
                    "narration": "Engaging hook that captures attention",
                    "on_screen_text": "Hook Text",
                    "visual_direction": "Test visual direction"
                },
                {
                    "section": "Body",
                    "duration": 30,
                    "narration": "Main content with supporting details",
                    "on_screen_text": "Body Text",
                    "visual_direction": "Test direction"
                },
                {
                    "section": "Close",
                    "duration": 10,
                    "narration": "Strong closing with call to action",
                    "on_screen_text": "CTA Text",
                    "visual_direction": "Test direction"
                }
            ]
        }

        scores = calculate_quality_scores(test_package, "Test transcript")

        # Target: 8/10 overall
        target = 8.0
        passed = scores["overall"] >= target

        print(f"   Overall Score: {scores['overall']}/10")
        print(f"   Target: ≥{target}/10")
        print(f"   Status: {'✅ PASS' if passed else '❌ FAIL'}")

        return {
            "passed": passed,
            "scores": scores,
            "target": target
        }

    def _benchmark_resource_usage(self) -> Dict:
        """Benchmark resource usage"""
        import psutil

        # Get current process info
        process = psutil.Process()

        # Memory usage
        memory_info = process.memory_info()
        memory_mb = memory_info.rss / 1024 / 1024

        # CPU usage
        cpu_percent = process.cpu_percent(interval=1)

        print(f"   Memory Usage: {memory_mb:.1f} MB")
        print(f"   CPU Usage: {cpu_percent}%")

        # Check if within reasonable limits
        memory_ok = memory_mb < 500  # < 500MB
        cpu_ok = cpu_percent < 80  # < 80%

        passed = memory_ok and cpu_ok

        print(f"   Status: {'✅ PASS' if passed else '❌ FAIL'}")

        return {
            "passed": passed,
            "memory_mb": memory_mb,
            "cpu_percent": cpu_percent,
            "memory_ok": memory_ok,
            "cpu_ok": cpu_ok
        }


# ============================================================================
# PUBLIC API
# ============================================================================

def run_all_tests() -> Dict:
    """Run all automated tests"""
    runner = AutomatedTestRunner()

    # Add Level 2 test suite
    level2_suite = Level2TestSuite()
    runner.add_suite(level2_suite)

    # Run all tests
    results = runner.run_all()

    # Save report
    from auto_clip import OUTPUT_DIR
    report_path = runner.save_report(OUTPUT_DIR)

    print(f"\n📄 Report saved to: {report_path}")

    return results


def run_quality_benchmark() -> Dict:
    """Run quality benchmarks"""
    benchmark = QualityBenchmark()
    return benchmark.run_level2_quality_benchmark()


# ============================================================================
# EXPORTS
# ============================================================================

__all__ = [
    # Test framework
    'TestCase',
    'TestResult',
    'TestSuite',
    'Level2TestSuite',
    'AutomatedTestRunner',

    # Regression testing
    'RegressionTester',

    # Benchmarking
    'QualityBenchmark',

    # Public API
    'run_all_tests',
    'run_quality_benchmark',
]
