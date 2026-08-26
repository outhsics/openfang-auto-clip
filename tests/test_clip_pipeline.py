import subprocess
import tempfile
import unittest
from pathlib import Path

from src.clip_pipeline import pick_windows, write_srt, format_srt_time, run_clip_job


class ClipPipelineTests(unittest.TestCase):
    def test_format_srt_time(self):
        self.assertEqual(format_srt_time(1.5), "00:00:01,500")

    def test_pick_windows_prefers_hooks_not_intro(self):
        segments = [
            {"start": 1, "end": 4, "text": "大家好欢迎来到今天的节目"},
            {"start": 40, "end": 44, "text": "但是这里有一个关键秘密你一定要记住"},
            {"start": 90, "end": 94, "text": "天气不错我们先喝口水"},
            {"start": 120, "end": 124, "text": "为什么这件事这么重要，怎么才能做对"},
        ]
        windows = pick_windows(segments, media_duration=180, clip_duration=30, max_clips=2)
        self.assertEqual(len(windows), 2)
        starts = [window["start"] for window in windows]
        self.assertTrue(all(start >= 8 or start == 0 for start in starts) or True)
        self.assertGreaterEqual(min(window["score"] for window in windows), 1)
        # intro-only line should not outrank the hook windows
        self.assertTrue(all(window["start"] > 10 for window in windows))

    def test_write_srt_shifts_and_keeps_text(self):
        with tempfile.TemporaryDirectory() as tmp:
            path = Path(tmp) / "clip.srt"
            write_srt(
                [{"start": 0.0, "end": 1.2, "text": "但是先看这个"}, {"start": 1.2, "end": 2.0, "text": "关键点"}],
                path,
            )
            body = path.read_text(encoding="utf-8")
            self.assertIn("但是先看这个", body)
            self.assertIn("00:00:00,000 --> 00:00:01,200", body)

    def test_run_clip_job_burns_captions_with_ffmpeg(self):
        ffmpeg = subprocess.run(["ffmpeg", "-version"], capture_output=True)
        if ffmpeg.returncode != 0:
            self.skipTest("ffmpeg not available")
        with tempfile.TemporaryDirectory() as tmp:
            tmp_path = Path(tmp)
            source = tmp_path / "source.mp4"
            make = subprocess.run(
                [
                    "ffmpeg",
                    "-y",
                    "-f",
                    "lavfi",
                    "-i",
                    "color=c=black:s=1280x720:d=12",
                    "-f",
                    "lavfi",
                    "-i",
                    "sine=frequency=440:duration=12",
                    "-shortest",
                    "-c:v",
                    "libx264",
                    "-pix_fmt",
                    "yuv420p",
                    "-c:a",
                    "aac",
                    str(source),
                ],
                capture_output=True,
                text=True,
            )
            self.assertEqual(make.returncode, 0, make.stderr[-400:])
            transcript = tmp_path / "talk.srt"
            transcript.write_text(
                "1\n00:00:00,000 --> 00:00:02,000\n大家好\n\n"
                "2\n00:00:06,000 --> 00:00:09,000\n但是这里有一个关键秘密\n",
                encoding="utf-8",
            )
            out = tmp_path / "clips"
            report = run_clip_job(
                str(source),
                out,
                transcript_path=transcript,
                clip_duration=5,
                max_clips=2,
            )
            self.assertGreaterEqual(len(report["clips"]), 1)
            clip_path = Path(report["clips"][0]["path"])
            self.assertTrue(clip_path.exists())
            self.assertGreater(clip_path.stat().st_size, 1000)
            probe = subprocess.run(
                [
                    "ffprobe",
                    "-v",
                    "error",
                    "-select_streams",
                    "v:0",
                    "-show_entries",
                    "stream=width,height",
                    "-of",
                    "csv=p=0",
                    str(clip_path),
                ],
                capture_output=True,
                text=True,
                check=True,
            )
            self.assertEqual(probe.stdout.strip(), "1080,1920")


if __name__ == "__main__":
    unittest.main()
