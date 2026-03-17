import tempfile
import unittest
from pathlib import Path
from unittest import mock

from scripts import release_prep


class ReleasePrepTests(unittest.TestCase):
    def test_validate_version_accepts_plain_and_prefixed_versions(self):
        self.assertEqual(release_prep.validate_version("0.3.0"), "0.3.0")
        self.assertEqual(release_prep.validate_version("v0.3.0"), "0.3.0")

    def test_validate_version_rejects_invalid_versions(self):
        with self.assertRaises(ValueError):
            release_prep.validate_version("0.3")

    def test_extract_changelog_section_prefers_matching_version(self):
        with tempfile.TemporaryDirectory() as tmp_dir:
            repo_root = Path(tmp_dir)
            (repo_root / "CHANGELOG.md").write_text(
                "# Changelog\n\n## [Unreleased]\n- future\n\n## [0.3.0]\n- shipped\n\n## [0.2.0]\n- older\n"
            )
            with mock.patch.object(release_prep, "REPO_ROOT", repo_root):
                section = release_prep.extract_changelog_section("0.3.0")

        self.assertIn("shipped", section)
        self.assertNotIn("older", section)

    def test_write_release_bundle_creates_notes_file(self):
        with tempfile.TemporaryDirectory() as tmp_dir:
            output_dir = Path(tmp_dir)
            notes_path = release_prep.write_release_bundle("0.3.0", "# Demo", output_dir)

            self.assertTrue(notes_path.exists())
            self.assertEqual(notes_path.read_text(), "# Demo")

    def test_build_release_notes_can_include_benchmark_metrics(self):
        notes = release_prep.build_release_notes(
            "0.3.0",
            "## [0.3.0]\n- shipped",
            report={
                "benchmark": {"duration_seconds": 18, "transform_level": 1},
                "timings": {"total_seconds": 5.4},
                "artifacts": {"clip_count": 3},
            },
        )

        self.assertIn("## Benchmark Proof", notes)
        self.assertIn("Clips generated: 3", notes)

    def test_build_showcase_bundle_generates_release_assets(self):
        with tempfile.TemporaryDirectory() as tmp_dir:
            repo_root = Path(tmp_dir)
            report_path = repo_root / "benchmark_report.json"
            preview_path = repo_root / "preview.png"
            storyboard_path = repo_root / "storyboard.png"
            preview_path.write_text("preview")
            storyboard_path.write_text("storyboard")
            report_path.write_text(
                """
{
  "benchmark": {"duration_seconds": 18, "transform_level": 1},
  "timings": {"total_seconds": 5.4},
  "artifacts": {
    "clip_count": 3,
    "preview_path": "preview.png",
    "storyboard_path": "storyboard.png"
  },
  "transform_result": {"status": "success"}
}
                """.strip()
            )
            target_dir = repo_root / "dist" / "releases" / "v0.3.0"

            with mock.patch.object(release_prep, "REPO_ROOT", repo_root):
                report = release_prep.load_report(report_path)
                created_paths = release_prep.build_showcase_bundle(report, report_path, target_dir)

        created_names = {path.name for path in created_paths}
        self.assertIn("benchmark_report.json", created_names)
        self.assertIn("preview.png", created_names)
        self.assertIn("storyboard.png", created_names)
        self.assertIn("launch_post.md", created_names)
        self.assertIn("github_social_preview.svg", created_names)
        self.assertIn("github_social_preview_zh.svg", created_names)
        self.assertIn("bundle_manifest.json", created_names)


if __name__ == "__main__":
    unittest.main()
