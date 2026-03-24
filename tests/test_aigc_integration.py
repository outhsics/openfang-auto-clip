#!/usr/bin/env python3
"""
Test AIGC Integration

Tests for AI image and video generation functionality.
"""

import sys
import unittest
from pathlib import Path
from unittest.mock import Mock, patch, MagicMock

# Add parent directory to path
sys.path.insert(0, str(Path(__file__).parent.parent))

from src.aigc.providers import (
    AIProvider,
    StableDiffusionProvider,
    OpenAIDALLEProvider,
    ReplicateProvider,
    get_provider,
    load_provider_config,
    ProviderType
)
from src.aigc.image_generator import (
    ImageGenerator,
    ImageStyle,
    generate_image,
    PRESET_PROMPTS
)
from src.aigc.video_generator import (
    VideoGenerator,
    VideoStyle,
    generate_video,
    VIDEO_PRESETS
)


class TestAIProviders(unittest.TestCase):
    """Test AI provider implementations"""

    def test_get_provider_stable_diffusion(self):
        """Test getting Stable Diffusion provider"""
        provider = get_provider("stable_diffusion", base_url="http://127.0.0.1:7860")
        self.assertIsInstance(provider, StableDiffusionProvider)
        self.assertEqual(provider.base_url, "http://127.0.0.1:7860")

    def test_get_provider_sd_alias(self):
        """Test 'sd' alias for Stable Diffusion"""
        provider = get_provider("sd")
        self.assertIsInstance(provider, StableDiffusionProvider)

    def test_get_provider_invalid(self):
        """Test invalid provider raises error"""
        with self.assertRaises(ValueError):
            get_provider("invalid_provider")

    def test_load_provider_config_default(self):
        """Test loading default provider config"""
        config = load_provider_config()
        self.assertIn("default_provider", config)
        self.assertIn("providers", config)
        self.assertEqual(config["default_provider"], "stable_diffusion")

    @patch('src.aigc.providers.requests.get')
    def test_stable_diffusion_check_status(self, mock_get):
        """Test Stable Diffusion status check"""
        mock_response = Mock()
        mock_response.status_code = 200
        mock_get.return_value = mock_response

        provider = StableDiffusionProvider(base_url="http://127.0.0.1:7860")
        self.assertTrue(provider.check_status())

    @patch('src.aigc.providers.requests.post')
    def test_stable_diffusion_generate_image(self, mock_post):
        """Test Stable Diffusion image generation"""
        mock_response = Mock()
        mock_response.raise_for_status = Mock()
        mock_response.json.return_value = {
            "images": ["base64encodeddata"],
            "parameters": {},
            "info": "{}"
        }
        mock_post.return_value = mock_response

        provider = StableDiffusionProvider(base_url="http://127.0.0.1:7860")
        result = provider.generate_image(
            prompt="Test prompt",
            width=512,
            height=512
        )

        self.assertTrue(result["success"])
        self.assertIn("image_base64", result)


class TestImageGenerator(unittest.TestCase):
    """Test image generator"""

    def setUp(self):
        """Set up test fixtures"""
        self.mock_provider = Mock(spec=AIProvider)
        self.mock_provider.provider_type = ProviderType.STABLE_DIFFUSION
        self.mock_provider.api_key = "test_key"

    @patch('src.aigc.image_generator.ImageGenerator._save_image')
    def test_generate_image_success(self, mock_save):
        """Test successful image generation"""
        # Mock provider response
        self.mock_provider.generate_image.return_value = {
            "success": True,
            "image_base64": "base64data"
        }

        generator = ImageGenerator(provider=self.mock_provider)
        result = generator.generate(
            prompt="Test prompt",
            width=1024,
            height=1024
        )

        self.assertTrue(result["success"])
        self.assertIn("save_path", result)
        self.assertEqual(len(generator._generation_history), 1)

    def test_image_styles_exist(self):
        """Test all image styles are defined"""
        expected_styles = [
            ImageStyle.REALISTIC,
            ImageStyle.ANIME,
            ImageStyle.OIL_PAINTING,
            ImageStyle.WATERCOLOR,
            ImageStyle.CYBERPUNK,
            ImageStyle.FANTASY,
            ImageStyle.MINIMALIST,
            ImageStyle.VINTAGE,
            ImageStyle.POP_ART,
            ImageStyle.CINEMATIC
        ]

        for style in expected_styles:
            self.assertIn(style.value, ImageStyle._value2member_map_)

    def test_preset_prompts_exist(self):
        """Test preset prompts are defined"""
        expected_presets = [
            "youtube_thumbnail",
            "video_background",
            "social_media_post",
            "character_design",
            "landscape"
        ]

        for preset in expected_presets:
            self.assertIn(preset, PRESET_PROMPTS)
            self.assertIn("prompt", PRESET_PROMPTS[preset])

    @patch('src.aigc.image_generator.ImageGenerator._save_image')
    def test_generate_with_style(self, mock_save):
        """Test generating image with style"""
        self.mock_provider.generate_image.return_value = {
            "success": True,
            "image_base64": "data"
        }

        generator = ImageGenerator(provider=self.mock_provider)
        result = generator.generate(
            prompt="Test",
            style=ImageStyle.CINEMATIC
        )

        # Check that style was applied to prompt
        call_args = self.mock_provider.generate_image.call_args
        prompt = call_args[1]["prompt"]
        self.assertIn("cinematic", prompt.lower())

    @patch('src.aigc.image_generator.ImageGenerator._save_image')
    def test_generate_batch(self, mock_save):
        """Test batch image generation"""
        self.mock_provider.generate_image.return_value = {
            "success": True,
            "image_base64": "data"
        }

        generator = ImageGenerator(provider=self.mock_provider)
        prompts = ["Test 1", "Test 2", "Test 3"]

        results = generator.generate_batch(prompts)

        self.assertEqual(len(results), 3)
        self.assertTrue(all(r["success"] for r in results))


class TestVideoGenerator(unittest.TestCase):
    """Test video generator"""

    def setUp(self):
        """Set up test fixtures"""
        self.mock_provider = Mock(spec=AIProvider)
        self.mock_provider.provider_type = ProviderType.STABLE_DIFFUSION

    @patch('src.aigc.video_generator.VideoGenerator._save_video')
    def test_generate_video_success(self, mock_save):
        """Test successful video generation"""
        self.mock_provider.generate_video.return_value = {
            "success": True,
            "video_base64": "base64data"
        }

        generator = VideoGenerator(provider=self.mock_provider)
        result = generator.generate(
            prompt="Test video",
            duration=4.0,
            fps=30
        )

        self.assertTrue(result["success"])
        self.assertIn("save_path", result)

    def test_video_styles_exist(self):
        """Test all video styles are defined"""
        expected_styles = [
            VideoStyle.CINEMATIC,
            VideoStyle.ANIME,
            VideoStyle.REALISTIC,
            VideoStyle.ABSTRACT,
            VideoStyle.NATURE,
            VideoStyle.SCI_FI,
            VideoStyle.VINTAGE,
            VideoStyle.SLOW_MOTION,
            VideoStyle.TIMELAPSE,
            VideoStyle.LOOP
        ]

        for style in expected_styles:
            self.assertIn(style.value, VideoStyle._value2member_map_)

    def test_video_presets_exist(self):
        """Test video presets are defined"""
        expected_presets = [
            "social_short",
            "youtube_intro",
            "background_loop",
            "product_showcase"
        ]

        for preset in expected_presets:
            self.assertIn(preset, VIDEO_PRESETS)

    @patch('src.aigc.video_generator.VideoGenerator._save_video')
    def test_generate_loop(self, mock_save):
        """Test generating looping video"""
        self.mock_provider.generate_video.return_value = {
            "success": True,
            "video_base64": "data"
        }

        generator = VideoGenerator(provider=self.mock_provider)
        result = generator.generate_loop(
            prompt="Looping animation",
            duration=5.0
        )

        self.assertTrue(result["success"])
        # Check that loop style was applied
        call_args = self.mock_provider.generate_video.call_args
        self.assertIn("loop", call_args[1]["prompt"].lower())


class TestIntegration(unittest.TestCase):
    """Integration tests for AIGC"""

    def test_image_generator_init(self):
        """Test ImageGenerator can be initialized"""
        generator = ImageGenerator()
        self.assertIsNotNone(generator.provider)

    def test_video_generator_init(self):
        """Test VideoGenerator can be initialized"""
        generator = VideoGenerator()
        self.assertIsNotNone(generator.provider)

    def test_get_history_empty(self):
        """Test getting history from new generator"""
        generator = ImageGenerator()
        history = generator.get_history()
        self.assertEqual(len(history), 0)

    def test_clear_history(self):
        """Test clearing history"""
        generator = ImageGenerator()
        generator._generation_history.append({"test": "data"})
        generator.clear_history()
        self.assertEqual(len(generator._generation_history), 0)


def run_tests():
    """Run all tests"""
    loader = unittest.TestLoader()
    suite = unittest.TestSuite()

    suite.addTests(loader.loadTestsFromTestCase(TestAIProviders))
    suite.addTests(loader.loadTestsFromTestCase(TestImageGenerator))
    suite.addTests(loader.loadTestsFromTestCase(TestVideoGenerator))
    suite.addTests(loader.loadTestsFromTestCase(TestIntegration))

    runner = unittest.TextTestRunner(verbosity=2)
    result = runner.run(suite)

    return result.wasSuccessful()


if __name__ == "__main__":
    success = run_tests()
    sys.exit(0 if success else 1)
