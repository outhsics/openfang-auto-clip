import tempfile
import unittest
from pathlib import Path

from scripts import generate_launch_kit


class LaunchKitTests(unittest.TestCase):
    def test_build_launch_markdown_contains_key_metrics(self):
        report = {
            "benchmark": {"duration_seconds": 18, "transform_level": 1},
            "timings": {"total_seconds": 5.4},
            "artifacts": {
                "clip_count": 3,
                "storyboard_path": "tmp/storyboard.png",
                "preview_path": "tmp/preview.png",
            },
            "transform_result": {"status": "success"},
        }

        markdown = generate_launch_kit.build_launch_markdown(report)

        self.assertIn("3 clips", markdown)
        self.assertIn("tmp/storyboard.png", markdown)
        self.assertIn("5.4s", markdown)

    def test_build_launch_markdown_supports_chinese_copy(self):
        report = {
            "benchmark": {"duration_seconds": 18, "transform_level": 1},
            "timings": {"total_seconds": 5.4},
            "artifacts": {
                "clip_count": 3,
                "storyboard_path": "tmp/storyboard.png",
                "preview_path": "tmp/preview.png",
            },
            "transform_result": {"status": "success"},
        }

        markdown = generate_launch_kit.build_launch_markdown(report, language="zh")

        self.assertIn("发布素材包", markdown)
        self.assertIn("生成片段数：3", markdown)
        self.assertIn("总耗时：5.4s", markdown)

    def test_write_launch_kit_creates_markdown_file(self):
        with tempfile.TemporaryDirectory() as tmp_dir:
            output_path = generate_launch_kit.write_launch_kit("# Demo", Path(tmp_dir))

            self.assertTrue(output_path.exists())
            self.assertEqual(output_path.read_text(), "# Demo")

    def test_write_launch_kit_creates_language_specific_file(self):
        with tempfile.TemporaryDirectory() as tmp_dir:
            output_path = generate_launch_kit.write_launch_kit("# Demo", Path(tmp_dir), "zh")

            self.assertTrue(output_path.exists())
            self.assertEqual(output_path.name, "launch_post_zh.md")


if __name__ == "__main__":
    unittest.main()
