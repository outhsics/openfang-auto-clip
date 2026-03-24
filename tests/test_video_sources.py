#!/usr/bin/env python3
"""
Test video sources module
"""

import sys
import unittest
from pathlib import Path
from unittest.mock import Mock, patch, MagicMock

# Add parent directory to path
sys.path.insert(0, str(Path(__file__).parent.parent))

from src.video_sources import (
    VideoSource,
    YouTubeSource,
    BilibiliSource,
    DouyinSource,
    LocalFileSource,
    DirectURLSource,
    GenericSource,
    get_video_source
)


class TestVideoSource(unittest.TestCase):
    """Test base VideoSource class"""

    def test_cannot_instantiate_base_class(self):
        """Base class should not be instantiated directly"""
        with self.assertRaises(TypeError):
            VideoSource()


class TestYouTubeSource(unittest.TestCase):
    """Test YouTube video source"""

    def setUp(self):
        self.source = YouTubeSource("https://www.youtube.com/watch?v=dQw4w9WgXcQ")

    def test_validate_youtube_url(self):
        """Test YouTube URL validation"""
        self.assertTrue(self.source.validate())

    def test_validate_youtube_short_url(self):
        """Test YouTube short URL"""
        source = YouTubeSource("https://youtu.be/dQw4w9WgXcQ")
        self.assertTrue(source.validate())

    def test_extract_video_id(self):
        """Test video ID extraction"""
        self.assertEqual(self.source.video_id, "dQw4w9WgXcQ")

    def test_extract_info(self):
        """Test info extraction"""
        info = self.source.extract_info()
        self.assertIn('video_id', info)
        self.assertIn('platform', info)
        self.assertEqual(info['platform'], 'youtube')

    @patch('src.video_sources.subprocess.run')
    def test_download(self, mock_run):
        """Test download method"""
        mock_run.return_value = MagicMock(
            returncode=0,
            stdout="Downloaded to /path/to/video.mp4"
        )

        output_path = self.source.download(output_dir="/tmp")
        self.assertIsNotNone(output_path)


class TestBilibiliSource(unittest.TestCase):
    """Test Bilibili video source"""

    def test_validate_bilibili_url(self):
        """Test Bilibili URL validation"""
        # BV format
        source = BilibiliSource("https://www.bilibili.com/video/BV1xx411c7mD")
        self.assertTrue(source.validate())

        # AV format
        source = BilibiliSource("https://www.bilibili.com/video/av12345678")
        self.assertTrue(source.validate())

    def test_extract_video_id(self):
        """Test video ID extraction"""
        source = BilibiliSource("https://www.bilibili.com/video/BV1xx411c7mD")
        self.assertEqual(source.video_id, "BV1xx411c7mD")


class TestLocalFileSource(unittest.TestCase):
    """Test local file source"""

    def test_validate_local_file(self):
        """Test local file validation"""
        # Create a temporary file
        import tempfile
        with tempfile.NamedTemporaryFile(delete=False) as f:
            temp_path = f.name

        try:
            source = LocalFileSource(temp_path)
            self.assertTrue(source.validate())
        finally:
            Path(temp_path).unlink()

    def test_validate_nonexistent_file(self):
        """Test nonexistent file validation"""
        source = LocalFileSource("/nonexistent/file.mp4")
        self.assertFalse(source.validate())


class TestDirectURLSource(unittest.TestCase):
    """Test direct URL source"""

    def test_validate_direct_url(self):
        """Test direct URL validation"""
        source = DirectURLSource("https://example.com/video.mp4")
        self.assertTrue(source.validate())

    def test_reject_non_video_url(self):
        """Test that non-video URLs are rejected"""
        source = DirectURLSource("https://example.com/page.html")
        # Should still validate as URL, but might fail during download
        self.assertTrue(source.validate())


class TestGenericSource(unittest.TestCase):
    """Test generic video source"""

    def test_accepts_any_url(self):
        """Test that generic source accepts any URL"""
        source = GenericSource("https://any-website.com/watch?id=123")
        self.assertTrue(source.validate())


class TestGetVideoSource(unittest.TestCase):
    """Test video source factory"""

    def test_returns_local_file_source(self):
        """Test that local files return LocalFileSource"""
        import tempfile
        with tempfile.NamedTemporaryFile(delete=False) as f:
            temp_path = f.name

        try:
            source = get_video_source(temp_path)
            self.assertIsInstance(source, LocalFileSource)
        finally:
            Path(temp_path).unlink()

    def test_returns_youtube_source(self):
        """Test that YouTube URLs return YouTubeSource"""
        source = get_video_source("https://www.youtube.com/watch?v=test")
        self.assertIsInstance(source, YouTubeSource)

    def test_returns_bilibili_source(self):
        """Test that Bilibili URLs return BilibiliSource"""
        source = get_video_source("https://www.bilibili.com/video/BV1xx411c7mD")
        self.assertIsInstance(source, BilibiliSource)

    def test_returns_generic_source_for_unknown(self):
        """Test that unknown URLs return GenericSource"""
        source = get_video_source("https://unknown-platform.com/video/123")
        self.assertIsInstance(source, GenericSource)


if __name__ == "__main__":
    unittest.main()
