#!/usr/bin/env python3
"""
Test transform effects module
"""

import sys
import unittest
from pathlib import Path
from unittest.mock import Mock, patch, MagicMock

# Add parent directory to path
sys.path.insert(0, str(Path(__file__).parent.parent))

from src.transform_effects import (
    EffectPreset,
    get_preset,
    list_presets,
    apply_preset,
    create_custom_preset,
    EFFECT_PRESETS
)


class TestEffectPreset(unittest.TestCase):
    """Test EffectPreset enum"""

    def test_all_presets_defined(self):
        """Test that all presets are defined in enum"""
        expected_presets = [
            "default", "mild", "strong",
            "cinematic", "retro", "cyberpunk", "vintage", "noir",
            "tiktok", "instagram", "youtube",
            "dramatic", "dreamy", "intense"
        ]

        for preset in expected_presets:
            self.assertIn(preset, [e.value for e in EffectPreset])


class TestGetPreset(unittest.TestCase):
    """Test get_preset function"""

    def test_get_existing_preset(self):
        """Test getting an existing preset"""
        preset = get_preset("default")

        self.assertIsNotNone(preset)
        self.assertIn("video_filter", preset)
        self.assertIn("audio_filter", preset)
        self.assertIn("speed_factor", preset)

    def test_get_nonexistent_preset(self):
        """Test getting a nonexistent preset"""
        preset = get_preset("nonexistent")

        self.assertIsNone(preset)

    def test_case_insensitive(self):
        """Test case-insensitive preset lookup"""
        preset1 = get_preset("Cinematic")
        preset2 = get_preset("cinematic")

        self.assertIsNotNone(preset1)
        self.assertIsNotNone(preset2)


class TestListPresets(unittest.TestCase):
    """Test list_presets function"""

    def test_list_all_presets(self):
        """Test listing all presets"""
        presets = list_presets()

        self.assertGreater(len(presets), 0)
        self.assertIn("name", presets[0])

    def test_list_by_category_basic(self):
        """Test listing basic presets"""
        presets = list_presets(category="basic")

        preset_names = [p["name"] for p in presets]
        self.assertIn("default", preset_names)
        self.assertIn("mild", preset_names)
        self.assertIn("strong", preset_names)

    def test_list_by_category_style(self):
        """Test listing style presets"""
        presets = list_presets(category="style")

        preset_names = [p["name"] for p in presets]
        self.assertIn("cinematic", preset_names)
        self.assertIn("retro", preset_names)
        self.assertIn("cyberpunk", preset_names)

    def test_list_by_category_social(self):
        """Test listing social media presets"""
        presets = list_presets(category="social")

        preset_names = [p["name"] for p in presets]
        self.assertIn("tiktok", preset_names)
        self.assertIn("instagram", preset_names)
        self.assertIn("youtube", preset_names)

    def test_list_by_category_mood(self):
        """Test listing mood presets"""
        presets = list_presets(category="mood")

        preset_names = [p["name"] for p in presets]
        self.assertIn("dramatic", preset_names)
        self.assertIn("dreamy", preset_names)
        self.assertIn("intense", preset_names)


class TestCreateCustomPreset(unittest.TestCase):
    """Test create_custom_preset function"""

    def test_create_custom_preset(self):
        """Test creating a custom preset"""
        preset = create_custom_preset(
            name="My Preset",
            video_filter="scale=1920:1080",
            audio_filter="atempo=1.0",
            speed_factor=1.0,
            protection_level="medium"
        )

        self.assertEqual(preset["name"], "My Preset")
        self.assertEqual(preset["video_filter"], "scale=1920:1080")
        self.assertEqual(preset["audio_filter"], "atempo=1.0")


class TestApplyPreset(unittest.TestCase):
    """Test apply_preset function"""

    @patch('src.transform_effects.subprocess.run')
    def test_apply_preset_success(self, mock_run):
        """Test successful preset application"""
        mock_run.return_value = MagicMock(
            returncode=0,
            stderr=""
        )

        # Create a dummy input file
        import tempfile
        with tempfile.NamedTemporaryFile(suffix=".mp4", delete=False) as f:
            input_path = f.name

        try:
            output_path = input_path.replace(".mp4", "_output.mp4")

            result = apply_preset(
                input_path=input_path,
                output_path=output_path,
                preset_name="mild"
            )

            self.assertTrue(result)
        finally:
            Path(input_path).unlink()

    @patch('src.transform_effects.subprocess.run')
    def test_apply_preset_failure(self, mock_run):
        """Test preset application failure"""
        mock_run.return_value = MagicMock(
            returncode=1,
            stderr="Error processing video"
        )

        import tempfile
        with tempfile.NamedTemporaryFile(suffix=".mp4", delete=False) as f:
            input_path = f.name

        try:
            output_path = input_path.replace(".mp4", "_output.mp4")

            result = apply_preset(
                input_path=input_path,
                output_path=output_path,
                preset_name="mild"
            )

            self.assertFalse(result)
        finally:
            Path(input_path).unlink()


class TestPresetStructure(unittest.TestCase):
    """Test preset structure and content"""

    def test_all_presets_have_required_fields(self):
        """Test that all presets have required fields"""
        required_fields = ["name", "description", "video_filter", "audio_filter", "speed_factor", "protection_level"]

        for preset_name, preset in EFFECT_PRESETS.items():
            for field in required_fields:
                self.assertIn(field, preset, f"Preset {preset_name} missing field {field}")

    def test_speed_factors_are_positive(self):
        """Test that all speed factors are positive"""
        for preset_name, preset in EFFECT_PRESETS.items():
            speed_factor = preset["speed_factor"]
            self.assertGreater(speed_factor, 0, f"Preset {preset_name} has invalid speed factor")
            self.assertLess(speed_factor, 2.0, f"Preset {preset_name} has excessive speed factor")

    def test_protection_levels_are_valid(self):
        """Test that all protection levels are valid"""
        valid_levels = ["low", "medium", "high", "very_high"]

        for preset_name, preset in EFFECT_PRESETS.items():
            protection_level = preset["protection_level"]
            self.assertIn(protection_level, valid_levels,
                            f"Preset {preset_name} has invalid protection level")


if __name__ == "__main__":
    unittest.main()
