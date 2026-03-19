import tempfile
import unittest
from pathlib import Path
from unittest import mock

from scripts import refresh_demo_assets


class RefreshDemoAssetsTests(unittest.TestCase):
    def test_normalize_benchmark_report_rewrites_paths(self):
        report = {
            "artifacts": {
                "source_path": "/tmp/demo/synthetic_source.mp4",
                "processed_video_path": "/tmp/demo/synthetic_source_transformed.mp4",
                "clips_dir": "/tmp/demo/clips",
                "preview_path": "/tmp/demo/preview.png",
                "storyboard_path": "/tmp/demo/storyboard.png",
                "report_path": "/tmp/demo/benchmark_report.json",
                "summary_markdown_path": "/tmp/demo/benchmark_summary.md",
            },
            "transform_result": {"output_path": "/tmp/demo/synthetic_source_transformed.mp4"},
            "clips": [{"path": "/tmp/demo/clips/clip_01.mp4"}],
        }

        normalized = refresh_demo_assets.normalize_benchmark_report(report)
        self.assertEqual(normalized["artifacts"]["report_path"], "tmp/demo-benchmark/benchmark_report.json")
        self.assertEqual(normalized["clips"][0]["path"], "tmp/demo-benchmark/clips/clip_01.mp4")

    def test_refresh_assets_writes_sample_files(self):
        with tempfile.TemporaryDirectory() as tmp_dir:
            repo_root = Path(tmp_dir)
            (repo_root / "examples" / "benchmark").mkdir(parents=True)
            (repo_root / "examples" / "demo").mkdir(parents=True)
            benchmark_out = repo_root / "tmp" / "refresh-demo-assets"
            benchmark_out.mkdir(parents=True)
            (benchmark_out / "benchmark_summary.md").write_text("summary", encoding="utf-8")

            fake_report = {
                "artifacts": {
                    "source_path": str(benchmark_out / "synthetic_source.mp4"),
                    "processed_video_path": str(benchmark_out / "synthetic_source_transformed.mp4"),
                    "clips_dir": str(benchmark_out / "clips"),
                    "preview_path": str(benchmark_out / "preview.png"),
                    "storyboard_path": str(benchmark_out / "storyboard.png"),
                    "report_path": str(benchmark_out / "benchmark_report.json"),
                    "summary_markdown_path": str(benchmark_out / "benchmark_summary.md"),
                },
                "transform_result": {"output_path": str(benchmark_out / "synthetic_source_transformed.mp4")},
                "clips": [],
            }

            with mock.patch.object(refresh_demo_assets, "REPO_ROOT", repo_root):
                with mock.patch.object(refresh_demo_assets.run_demo_benchmark, "run_benchmark", return_value=fake_report):
                    with mock.patch.object(refresh_demo_assets.export_level2_demo_samples, "export_samples", return_value={"output_dir": "examples/demo/level2_samples"}):
                        result = refresh_demo_assets.refresh_assets(benchmark_out)

            self.assertTrue((repo_root / "examples" / "benchmark" / "sample_benchmark_report.json").exists())
            self.assertTrue((repo_root / "examples" / "benchmark" / "sample_benchmark_summary.md").exists())
            self.assertEqual(result["level2_output_dir"], "examples/demo/level2_samples")


if __name__ == "__main__":
    unittest.main()
