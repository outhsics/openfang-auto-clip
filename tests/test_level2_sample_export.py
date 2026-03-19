import tempfile
import unittest
from pathlib import Path

from scripts import export_level2_demo_samples


class Level2SampleExportTests(unittest.TestCase):
    def test_export_samples_writes_index_and_case_files(self):
        with tempfile.TemporaryDirectory() as tmp_dir:
            output_dir = Path(tmp_dir) / "level2_samples"
            report = export_level2_demo_samples.export_samples(output_dir, duration=45)

            self.assertEqual(len(report["cases"]), 2)
            self.assertTrue((output_dir / "index.json").exists())
            self.assertTrue((output_dir / "README.md").exists())
            self.assertTrue((output_dir / "README_ZH.md").exists())
            self.assertTrue((output_dir / "en" / "script_package.json").exists())
            self.assertTrue((output_dir / "zh" / "review_report.md").exists())


if __name__ == "__main__":
    unittest.main()
