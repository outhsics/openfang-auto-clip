import tempfile
import unittest
from pathlib import Path

from scripts import generate_social_preview


class SocialPreviewTests(unittest.TestCase):
    def setUp(self):
        self.report = {
            "benchmark": {"duration_seconds": 18, "transform_level": 1},
            "timings": {"total_seconds": 5.4},
            "artifacts": {"clip_count": 3},
        }

    def test_build_social_preview_svg_contains_metrics(self):
        svg = generate_social_preview.build_social_preview_svg(self.report)

        self.assertIn('width="1280"', svg)
        self.assertIn("Local-first video repurposing pipeline", svg)
        self.assertIn("18s synthetic", svg)
        self.assertIn(">3</text>", svg)

    def test_build_social_preview_svg_supports_chinese_copy(self):
        svg = generate_social_preview.build_social_preview_svg(self.report, language="zh")

        self.assertIn("本地优先的视频切条与再分发流水线", svg)
        self.assertIn("演示时长", svg)
        self.assertIn("总耗时", svg)

    def test_write_social_preview_creates_language_specific_file(self):
        with tempfile.TemporaryDirectory() as tmp_dir:
            output_path = generate_social_preview.write_social_preview("<svg />", Path(tmp_dir), "zh")

            self.assertTrue(output_path.exists())
            self.assertEqual(output_path.name, "github_social_preview_zh.svg")
            self.assertEqual(output_path.read_text(), "<svg />")


if __name__ == "__main__":
    unittest.main()
