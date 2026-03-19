import tempfile
import unittest
from pathlib import Path
from unittest import mock

from scripts import run_level2_demo_suite


class Level2DemoSuiteTests(unittest.TestCase):
    def test_run_suite_writes_summary_and_case_outputs(self):
        with tempfile.TemporaryDirectory() as tmp_dir:
            output_dir = Path(tmp_dir)

            cases = [
                {
                    "id": "en_srt",
                    "label_en": "English SRT transcript",
                    "label_zh": "英文 SRT transcript",
                    "language": "en",
                    "transcript_format": "srt",
                    "transcript_path": "en.srt",
                    "package_dir": str(output_dir / "pkg_en"),
                    "score": 90,
                    "status": "ready_for_operator_review",
                    "status_label_en": "Ready for operator review",
                    "status_label_zh": "可进入人工审阅",
                    "metrics": {
                        "script_section_count": 3,
                        "timed_segment_count": 2,
                        "section_anchor_count": 2,
                    },
                    "saved_files": [],
                },
                {
                    "id": "zh_srt",
                    "label_en": "Chinese SRT transcript",
                    "label_zh": "中文 SRT transcript",
                    "language": "zh",
                    "transcript_format": "srt",
                    "transcript_path": "zh.srt",
                    "package_dir": str(output_dir / "pkg_zh"),
                    "score": 100,
                    "status": "ready_for_operator_review",
                    "status_label_en": "Ready for operator review",
                    "status_label_zh": "可进入人工审阅",
                    "metrics": {
                        "script_section_count": 3,
                        "timed_segment_count": 2,
                        "section_anchor_count": 2,
                    },
                    "saved_files": [],
                },
                {
                    "id": "en_json",
                    "label_en": "English JSON transcript",
                    "label_zh": "英文 JSON transcript",
                    "language": "en",
                    "transcript_format": "json",
                    "transcript_path": "en.json",
                    "package_dir": str(output_dir / "pkg_en_json"),
                    "score": 92,
                    "status": "ready_for_operator_review",
                    "status_label_en": "Ready for operator review",
                    "status_label_zh": "可进入人工审阅",
                    "metrics": {
                        "script_section_count": 3,
                        "timed_segment_count": 3,
                        "section_anchor_count": 2,
                    },
                    "saved_files": [],
                },
                {
                    "id": "zh_vtt",
                    "label_en": "Chinese VTT transcript",
                    "label_zh": "中文 VTT transcript",
                    "language": "zh",
                    "transcript_format": "vtt",
                    "transcript_path": "zh.vtt",
                    "package_dir": str(output_dir / "pkg_zh_vtt"),
                    "score": 98,
                    "status": "ready_for_operator_review",
                    "status_label_en": "Ready for operator review",
                    "status_label_zh": "可进入人工审阅",
                    "metrics": {
                        "script_section_count": 3,
                        "timed_segment_count": 3,
                        "section_anchor_count": 2,
                    },
                    "saved_files": [],
                },
            ]

            with mock.patch.object(run_level2_demo_suite, "run_case", side_effect=cases):
                report = run_level2_demo_suite.run_suite(output_dir, duration=45)

            self.assertEqual(report["average_score"], 95)
            self.assertTrue((output_dir / "level2_demo_suite_report.json").exists())
            self.assertTrue((output_dir / "level2_demo_suite_report.md").exists())

    def test_render_suite_markdown_includes_bilingual_labels(self):
        report = {
            "created_at": "2026-03-19T12:00:00",
            "output_dir": "tmp/level2-demo-suite",
            "average_score": 95,
            "cases": [
                {
                    "label_en": "English transcript",
                    "label_zh": "英文 transcript",
                    "status_label_en": "Ready for operator review",
                    "status_label_zh": "可进入人工审阅",
                    "score": 95,
                    "transcript_format": "json",
                    "package_dir": "tmp/pkg",
                    "transcript_path": "examples/demo/sample_level2_transcript.srt",
                    "metrics": {
                        "script_section_count": 3,
                        "timed_segment_count": 4,
                        "section_anchor_count": 2,
                    },
                }
            ],
            "notes_en": ["First note"],
            "notes_zh": ["第一条说明"],
        }

        markdown = run_level2_demo_suite.render_suite_markdown(report)
        self.assertIn("Level 2 Demo Suite / Level 2 演示套件", markdown)
        self.assertIn("Format / 格式: json", markdown)
        self.assertIn("First note / 第一条说明", markdown)


if __name__ == "__main__":
    unittest.main()
