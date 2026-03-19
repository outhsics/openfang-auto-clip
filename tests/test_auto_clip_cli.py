import tempfile
import unittest
from datetime import datetime
from pathlib import Path
from unittest import mock
from types import SimpleNamespace

import auto_clip


class AutoClipCliTests(unittest.TestCase):
    def test_build_processing_plan_contains_expected_fields(self):
        config = {"default_duration": 45, "target_platforms": ["tiktok", "shorts"]}
        plan = auto_clip.build_processing_plan(
            "https://example.com/video",
            1,
            config,
            now=datetime(2026, 3, 8, 12, 0, 0),
        )

        self.assertEqual(plan["transform_label"], "visual")
        self.assertEqual(plan["default_duration"], 45)
        self.assertIn("20260308_120000", plan["projected_output_dir"])

    def test_build_processing_plan_marks_level2_readiness(self):
        config = {"default_duration": 45, "target_platforms": ["tiktok", "shorts"]}

        with tempfile.TemporaryDirectory() as tmp_dir:
            transcript_path = Path(tmp_dir) / "sample.srt"
            transcript_path.write_text(
                "1\n00:00:00,000 --> 00:00:02,000\nFresh angles matter.\n",
                encoding="utf-8",
            )
            plan = auto_clip.build_processing_plan(
                "https://example.com/video",
                2,
                config,
                transcript_path=str(transcript_path),
                now=datetime(2026, 3, 8, 12, 0, 0),
            )

            self.assertTrue(plan["script_package_ready"])
            self.assertEqual(
                plan["transcript_path"],
                str(auto_clip.resolve_explicit_transcript_path(str(transcript_path))),
            )
            self.assertEqual(plan["transform_label"], "script")

    def test_save_dry_run_plan_writes_json_file(self):
        plan = {"url": "https://example.com/video", "transform_level": 1}

        with tempfile.TemporaryDirectory() as tmp_dir:
            with mock.patch.object(auto_clip, "OUTPUT_DIR", Path(tmp_dir)):
                plan_path = auto_clip.save_dry_run_plan(plan)

            self.assertTrue(plan_path.exists())
            self.assertEqual(plan_path.parent.name, "dry_runs")

    def test_build_doctor_report_marks_required_tools_missing(self):
        with mock.patch.object(auto_clip, "command_exists", side_effect=lambda cmd: cmd == "ffmpeg"):
            with mock.patch("auto_clip.shutil.which", side_effect=lambda cmd: f"/usr/bin/{cmd}" if cmd == "ffmpeg" else None):
                report = auto_clip.build_doctor_report()

        statuses = {check["name"]: check["status"] for check in report["checks"]}
        self.assertEqual(statuses["ffmpeg"], "ok")
        self.assertEqual(statuses["yt-dlp"], "error")
        self.assertIn(statuses["openfang"], {"warn", "ok"})

    def test_create_clips_creates_output_directory(self):
        with tempfile.TemporaryDirectory() as tmp_dir:
            tmp_path = Path(tmp_dir)
            source_path = tmp_path / "source.mp4"
            source_path.write_bytes(b"source")
            output_dir = tmp_path / "nested" / "clips"

            def fake_run(command, capture_output=True, text=True):
                Path(command[-1]).write_bytes(b"x" * 2048)
                return SimpleNamespace(returncode=0, stderr="")

            with mock.patch.object(auto_clip.subprocess, "run", side_effect=fake_run):
                clips = auto_clip.create_clips(
                    str(source_path),
                    [{"start": 0, "end": 5, "reason": "demo", "score": 5}],
                    output_dir,
                    {"target_platforms": ["tiktok"]},
                )

            self.assertEqual(len(clips), 1)
            self.assertTrue(output_dir.exists())

    def test_read_transcript_text_parses_srt(self):
        with tempfile.TemporaryDirectory() as tmp_dir:
            transcript_path = Path(tmp_dir) / "sample.srt"
            transcript_path.write_text(
                "1\n00:00:00,000 --> 00:00:02,000\nThis is the first point.\n\n"
                "2\n00:00:02,000 --> 00:00:04,000\nAnd this is the second point.\n",
                encoding="utf-8",
            )

            transcript_text = auto_clip.read_transcript_text(transcript_path)

        self.assertIn("This is the first point.", transcript_text)
        self.assertNotIn("-->", transcript_text)

    def test_build_transcript_payload_keeps_timed_segments(self):
        with tempfile.TemporaryDirectory() as tmp_dir:
            transcript_path = Path(tmp_dir) / "sample.srt"
            transcript_path.write_text(
                "1\n00:00:00,000 --> 00:00:02,000\nFresh angle first.\n\n"
                "2\n00:00:02,000 --> 00:00:05,000\nThen support it with new visuals.\n",
                encoding="utf-8",
            )

            payload = auto_clip.build_transcript_payload(transcript_path)

        self.assertEqual(len(payload["segments"]), 2)
        self.assertEqual(payload["segments"][0]["start"], 0.0)
        self.assertEqual(payload["segments"][1]["end"], 5.0)
        self.assertIn("new visuals", payload["text"])

    def test_build_transcript_payload_parses_json_segments(self):
        with tempfile.TemporaryDirectory() as tmp_dir:
            transcript_path = Path(tmp_dir) / "sample.json"
            transcript_path.write_text(
                auto_clip.json.dumps(
                    {
                        "text": "Hook first. Then prove it.",
                        "segments": [
                            {"start": 0, "end": 2, "text": "Hook first."},
                            {"start": 2, "end": 4, "text": "Then prove it."},
                        ],
                    }
                ),
                encoding="utf-8",
            )

            payload = auto_clip.build_transcript_payload(transcript_path)

        self.assertEqual(len(payload["segments"]), 2)
        self.assertEqual(payload["segments"][0]["start"], 0.0)
        self.assertIn("Then prove it.", payload["text"])

    def test_build_transcript_payload_parses_vtt_segments(self):
        with tempfile.TemporaryDirectory() as tmp_dir:
            transcript_path = Path(tmp_dir) / "sample.vtt"
            transcript_path.write_text(
                "WEBVTT\n\n"
                "00:00:00.000 --> 00:00:02.000\n先讲结论。\n\n"
                "00:00:02.000 --> 00:00:04.000\n再补充新的论据。\n",
                encoding="utf-8",
            )

            payload = auto_clip.build_transcript_payload(transcript_path)

        self.assertEqual(len(payload["segments"]), 2)
        self.assertEqual(payload["segments"][1]["end"], 4.0)
        self.assertIn("新的论据", payload["text"])

    def test_transform_script_generates_level2_package(self):
        config = {"default_duration": 36}

        with tempfile.TemporaryDirectory() as tmp_dir:
            tmp_path = Path(tmp_dir)
            video_path = tmp_path / "source.mp4"
            video_path.write_bytes(b"video")
            transcript_path = tmp_path / "source.txt"
            transcript_path.write_text(
                (
                    "Strong hooks keep people watching. "
                    "Clear structure helps the message land. "
                    "Visual changes should support the new voiceover. "
                    "The final takeaway needs its own call to action."
                ),
                encoding="utf-8",
            )

            with mock.patch.object(auto_clip, "OUTPUT_DIR", tmp_path / "output"):
                transformer = auto_clip.CopyrightTransformer(config)
                result = transformer.transform(
                    str(video_path),
                    auto_clip.TransformLevel.SCRIPT,
                    video_info={"title": "Demo Source", "path": str(video_path)},
                    transcript_path=str(transcript_path),
                )

            self.assertEqual(result["status"], "success")
            package_dir = Path(result["package_dir"])
            self.assertTrue((package_dir / "script_package.json").exists())
            self.assertTrue((package_dir / "script_draft.md").exists())
            self.assertTrue((package_dir / "production_blueprint.json").exists())
            self.assertTrue((package_dir / "operator_handoff.json").exists())
            self.assertTrue((package_dir / "review_report.json").exists())
            self.assertTrue((package_dir / "review_report.md").exists())

            package = auto_clip.json.loads((package_dir / "script_package.json").read_text(encoding="utf-8"))
            self.assertTrue(package["shot_plan"])
            self.assertTrue(package["asset_requests"])
            self.assertTrue(package["voiceover_notes"])
            self.assertTrue(package["review_rubric"])
            self.assertIn("source_anchor", package["script_sections"][0])

    def test_run_level2_script_demo_creates_report_and_package(self):
        config = {"default_duration": 30}

        with tempfile.TemporaryDirectory() as tmp_dir:
            tmp_path = Path(tmp_dir)
            transcript_path = tmp_path / "demo.srt"
            transcript_path.write_text(
                "1\n00:00:00,000 --> 00:00:03,000\nLead with the strongest claim.\n\n"
                "2\n00:00:03,000 --> 00:00:06,000\nSupport it with a fresh visual beat.\n",
                encoding="utf-8",
            )

            with mock.patch.object(auto_clip, "OUTPUT_DIR", tmp_path / "output"):
                report = auto_clip.run_level2_script_demo(config, transcript_path=str(transcript_path))

            package_dir = Path(report["output_dir"])
            self.assertEqual(report["mode"], "script_package_demo")
            self.assertTrue((package_dir / "script_package.json").exists())
            self.assertTrue((package_dir / "script_draft.md").exists())
            self.assertTrue((package_dir / "production_blueprint.json").exists())
            self.assertTrue((package_dir / "operator_handoff.json").exists())
            self.assertTrue((package_dir / "report.json").exists())
            self.assertTrue((package_dir / "review_report.json").exists())
            self.assertTrue((package_dir / "review_report.md").exists())

    def test_run_level2_package_review_accepts_directory(self):
        package = {
            "language": "en",
            "milestone": "level2_transcript_to_script_package",
            "source": {
                "title": "Demo Review",
                "segment_count": 2,
            },
            "source_outline": [
                {"index": 1, "summary": "Hook", "source_anchor": "00:00:00.000 - 00:00:03.000"},
                {"index": 2, "summary": "Support", "source_anchor": "00:00:03.000 - 00:00:06.000"},
            ],
            "script_sections": [
                {"section": "Hook", "duration": 10, "source_anchor": "00:00:00.000 - 00:00:03.000"},
                {"section": "Point 1", "duration": 10, "source_anchor": "00:00:03.000 - 00:00:06.000"},
                {"section": "Close", "duration": 10, "source_anchor": None},
            ],
            "shot_plan": [
                {"shot": 1, "section": "Hook", "duration": 10},
                {"shot": 2, "section": "Point 1", "duration": 10},
                {"shot": 3, "section": "Close", "duration": 10},
            ],
            "asset_requests": [
                {"shot": 1},
                {"shot": 2},
                {"shot": 3},
            ],
            "voiceover_notes": ["One", "Two", "Three", "Four"],
            "review_rubric": ["One", "Two", "Three", "Four"],
            "production_checklist": ["One", "Two", "Three", "Four"],
        }

        with tempfile.TemporaryDirectory() as tmp_dir:
            package_dir = Path(tmp_dir) / "package"
            package_dir.mkdir()
            (package_dir / "script_package.json").write_text(auto_clip.json.dumps(package), encoding="utf-8")

            review = auto_clip.run_level2_package_review(str(package_dir))

            self.assertEqual(review["status"], "ready_for_operator_review")
            self.assertTrue((package_dir / "review_report.json").exists())
            self.assertTrue((package_dir / "review_report.md").exists())


if __name__ == "__main__":
    unittest.main()
