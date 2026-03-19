import tempfile
import unittest
from pathlib import Path
from unittest import mock

from scripts import run_local_evaluation


class LocalEvaluationTests(unittest.TestCase):
    def test_run_local_evaluation_writes_reports(self):
        with tempfile.TemporaryDirectory() as tmp_dir:
            output_dir = Path(tmp_dir)
            doctor_report = {
                "checks": [
                    {"name": "python", "status": "ok"},
                    {"name": "ffmpeg", "status": "ok"},
                ]
            }
            benchmark_report = {
                "artifacts": {
                    "clip_count": 3,
                    "storyboard_path": str(output_dir / "benchmark" / "storyboard.png"),
                }
            }
            suite_report = {
                "average_score": 100,
                "report_json_path": str(output_dir / "level2_suite" / "level2_demo_suite_report.json"),
                "report_markdown_path": str(output_dir / "level2_suite" / "level2_demo_suite_report.md"),
            }

            with mock.patch.object(run_local_evaluation.auto_clip, "build_doctor_report", return_value=doctor_report):
                with mock.patch.object(run_local_evaluation.run_demo_benchmark, "run_benchmark", return_value=benchmark_report):
                    with mock.patch.object(run_local_evaluation.run_level2_demo_suite, "run_suite", return_value=suite_report):
                        report = run_local_evaluation.run_local_evaluation(output_dir, 18, 6, 45)

            self.assertEqual(report["status_en"], "Ready for deeper evaluation")
            self.assertTrue((output_dir / "local_evaluation_report.json").exists())
            self.assertTrue((output_dir / "local_evaluation_report.md").exists())

    def test_run_local_evaluation_skips_benchmark_without_ffmpeg(self):
        with tempfile.TemporaryDirectory() as tmp_dir:
            output_dir = Path(tmp_dir)
            doctor_report = {
                "checks": [
                    {"name": "python", "status": "ok"},
                    {"name": "ffmpeg", "status": "error"},
                ]
            }
            suite_report = {
                "average_score": 95,
                "report_json_path": str(output_dir / "level2_suite" / "level2_demo_suite_report.json"),
                "report_markdown_path": str(output_dir / "level2_suite" / "level2_demo_suite_report.md"),
            }

            with mock.patch.object(run_local_evaluation.auto_clip, "build_doctor_report", return_value=doctor_report):
                with mock.patch.object(run_local_evaluation.run_demo_benchmark, "run_benchmark") as mocked_benchmark:
                    with mock.patch.object(run_local_evaluation.run_level2_demo_suite, "run_suite", return_value=suite_report):
                        report = run_local_evaluation.run_local_evaluation(output_dir, 18, 6, 45)

            mocked_benchmark.assert_not_called()
            self.assertEqual(report["benchmark"]["status"], "skipped")
            self.assertEqual(report["status_en"], "Needs environment fixes")


if __name__ == "__main__":
    unittest.main()
