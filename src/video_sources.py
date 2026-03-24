"""
Video source downloaders for OpenFang Auto Clip.

Supports multiple video platforms and sources.
"""

import os
import re
import json
import subprocess
from pathlib import Path
from typing import Dict, List, Optional, Tuple
from urllib.parse import urlparse, parse_qs


class VideoSource:
    """Base class for video sources"""

    def __init__(self, url: str):
        self.url = url
        self.parsed = urlparse(url)

    def validate(self) -> bool:
        """Check if URL is valid for this source"""
        raise NotImplementedError

    def download(self, output_dir: Path) -> Dict:
        """Download video and return metadata"""
        raise NotImplementedError

    def extract_info(self) -> Dict:
        """Extract video metadata without downloading"""
        raise NotImplementedError


class YouTubeSource(VideoSource):
    """YouTube video source"""

    def validate(self) -> bool:
        return 'youtube.com' in self.parsed.netloc or 'youtu.be' in self.parsed.netloc

    def extract_info(self) -> Dict:
        """Extract YouTube video ID and info"""
        if 'youtu.be' in self.parsed.netloc:
            video_id = self.parsed.path.strip('/')
        else:
            query = parse_qs(self.parsed.query)
            video_id = query.get('v', [None])[0]

        if not video_id:
            raise ValueError(f"Could not extract YouTube video ID from: {self.url}")

        return {
            'platform': 'youtube',
            'video_id': video_id,
            'url': self.url,
            'thumbnail': f"https://img.youtube.com/vi/{video_id}/maxresdefault.jpg"
        }

    def download(self, output_dir: Path) -> Dict:
        info = self.extract_info()

        cmd = [
            'yt-dlp',
            '-f', 'best[ext=mp4]',
            '-o', str(output_dir / '%(title)s.%(ext)s'),
            '--print', 'json',
            '--remote-components', 'ejs:github',
            '--newline',
            self.url
        ]

        result = subprocess.run(cmd, capture_output=True, text=True, timeout=300)

        if result.returncode != 0:
            raise Exception(f"YouTube download failed: {result.stderr}")

        video_info = json.loads(result.stdout)

        # Sanitize filename
        safe_title = self._sanitize_filename(video_info.get('title', 'video'))
        video_path = output_dir / f"{safe_title}.mp4"

        # Rename if needed
        original_path = output_dir / f"{video_info['title']}.mp4"
        if original_path.exists() and original_path != video_path:
            original_path.rename(video_path)

        return {
            'path': str(video_path),
            'title': video_info.get('title', safe_title),
            'duration': video_info.get('duration', 0),
            'id': video_info.get('id', info['video_id']),
            'uploader': video_info.get('uploader', 'unknown'),
            'upload_date': video_info.get('upload_date', 'unknown'),
            'platform': 'youtube',
            'thumbnail': info['thumbnail']
        }

    @staticmethod
    def _sanitize_filename(filename: str) -> str:
        """Sanitize filename for safe file system operations"""
        safe = re.sub(r'[<>:"/\\|?*]', '', filename)
        safe = re.sub(r'[\s\|]+', '_', safe)
        if len(safe) > 100:
            safe = safe[:97] + "..."
        return safe.strip()


class BilibiliSource(VideoSource):
    """Bilibili video source"""

    def validate(self) -> bool:
        return 'bilibili.com' in self.parsed.netloc

    def extract_info(self) -> Dict:
        """Extract Bilibili video info"""
        # Extract BV ID or AV ID
        bv_match = re.search(r'BV[\w]+', self.url)
        av_match = re.search(r'av(\d+)', self.url)

        if bv_match:
            video_id = bv_match.group(0)
        elif av_match:
            video_id = f"av{av_match.group(1)}"
        else:
            raise ValueError(f"Could not extract Bilibili video ID from: {self.url}")

        return {
            'platform': 'bilibili',
            'video_id': video_id,
            'url': self.url
        }

    def download(self, output_dir: Path) -> Dict:
        info = self.extract_info()

        # Bilibili requires cookies for some videos
        cmd = [
            'yt-dlp',
            '-f', 'best[ext=mp4]',
            '-o', str(output_dir / '%(title)s.%(ext)s'),
            '--print', 'json',
            '--cookies', '/dev/null',  # Optional: add cookie file
            self.url
        ]

        result = subprocess.run(cmd, capture_output=True, text=True, timeout=600)

        if result.returncode != 0:
            raise Exception(f"Bilibili download failed: {result.stderr}")

        video_info = json.loads(result.stdout)
        safe_title = YouTubeSource._sanitize_filename(video_info.get('title', 'bilibili_video'))
        video_path = output_dir / f"{safe_title}.mp4"

        return {
            'path': str(video_path),
            'title': video_info.get('title', safe_title),
            'duration': video_info.get('duration', 0),
            'id': info['video_id'],
            'uploader': video_info.get('uploader', 'unknown'),
            'platform': 'bilibili'
        }


class DouyinSource(VideoSource):
    """Douyin (TikTok China) video source"""

    def validate(self) -> bool:
        return 'douyin.com' in self.parsed.netloc

    def extract_info(self) -> Dict:
        return {
            'platform': 'douyin',
            'url': self.url
        }

    def download(self, output_dir: Path) -> Dict:
        cmd = [
            'yt-dlp',
            '-f', 'best[ext=mp4]',
            '-o', str(output_dir / '%(title)s.%(ext)s'),
            '--print', 'json',
            '--no-check-certificate',  # Douyin may require this
            self.url
        ]

        result = subprocess.run(cmd, capture_output=True, text=True, timeout=300)

        if result.returncode != 0:
            raise Exception(f"Douyin download failed: {result.stderr}")

        video_info = json.loads(result.stdout)
        safe_title = YouTubeSource._sanitize_filename(video_info.get('title', 'douyin_video'))
        video_path = output_dir / f"{safe_title}.mp4"

        return {
            'path': str(video_path),
            'title': video_info.get('title', safe_title),
            'duration': video_info.get('duration', 0),
            'id': video_info.get('id', 'unknown'),
            'uploader': video_info.get('uploader', 'unknown'),
            'platform': 'douyin'
        }


class LocalFileSource(VideoSource):
    """Local video file source"""

    def validate(self) -> bool:
        """Check if path exists and is a video file"""
        path = Path(self.url)

        # Handle file:// URLs
        if self.parsed.scheme == 'file':
            path = Path(self.parsed.path)

        # Check if file exists
        if not path.exists():
            return False

        # Check file extension
        video_extensions = {'.mp4', '.avi', '.mov', '.mkv', '.flv', '.wmv', '.webm'}
        return path.suffix.lower() in video_extensions

    def extract_info(self) -> Dict:
        """Extract local file info"""
        path = Path(self.url)
        if self.parsed.scheme == 'file':
            path = Path(self.parsed.path)

        if not path.exists():
            raise FileNotFoundError(f"File not found: {path}")

        return {
            'platform': 'local',
            'path': str(path.resolve()),
            'filename': path.name,
            'size': path.stat().st_size
        }

    def download(self, output_dir: Path) -> Dict:
        """"Download" local file (copy to output)"""
        info = self.extract_info()
        source_path = Path(info['path'])

        # Copy file to output directory
        import shutil
        dest_path = output_dir / source_path.name
        shutil.copy2(source_path, dest_path)

        # Get duration using ffprobe
        duration = self._get_video_duration(str(dest_path))

        return {
            'path': str(dest_path),
            'title': source_path.stem,
            'duration': duration,
            'id': source_path.stem,
            'uploader': 'local',
            'platform': 'local'
        }

    @staticmethod
    def _get_video_duration(video_path: str) -> float:
        """Get video duration using ffprobe"""
        cmd = [
            'ffprobe',
            '-v', 'error',
            '-show_entries', 'format=duration',
            '-of', 'default=noprint_wrappers=1:nokey=1',
            video_path
        ]

        result = subprocess.run(cmd, capture_output=True, text=True, timeout=30)

        if result.returncode == 0:
            try:
                return float(result.stdout.strip())
            except ValueError:
                pass

        return 0


class DirectURLSource(VideoSource):
    """Direct video URL source"""

    def validate(self) -> bool:
        """Check if URL points directly to a video file"""
        # Check for common video extensions in path
        video_extensions = {'.mp4', '.avi', '.mov', '.mkv', '.flv', '.wmv', '.webm'}
        path = self.parsed.path.lower()
        return any(path.endswith(ext) for ext in video_extensions)

    def extract_info(self) -> Dict:
        return {
            'platform': 'direct',
            'url': self.url,
            'filename': Path(self.parsed.path).name
        }

    def download(self, output_dir: Path) -> Dict:
        """Download video from direct URL"""
        import urllib.request

        info = self.extract_info()
        filename = info['filename']
        output_path = output_dir / filename

        # Download file
        urllib.request.urlretrieve(self.url, output_path)

        # Get duration
        duration = LocalFileSource._get_video_duration(str(output_path))

        return {
            'path': str(output_path),
            'title': filename.stem,
            'duration': duration,
            'id': filename.stem,
            'uploader': 'direct',
            'platform': 'direct'
        }


def get_video_source(url: str) -> VideoSource:
    """
    Factory function to get appropriate video source for URL

    Args:
        url: Video URL or file path

    Returns:
        VideoSource instance
    """
    # Try local file first
    local_source = LocalFileSource(url)
    if local_source.validate():
        return local_source

    # Try direct URL
    direct_source = DirectURLSource(url)
    if direct_source.validate():
        return direct_source

    # Parse URL for platform detection
    parsed = urlparse(url)
    netloc = parsed.netloc.lower()

    # Platform-specific sources
    if 'youtube.com' in netloc or 'youtu.be' in netloc:
        return YouTubeSource(url)
    elif 'bilibili.com' in netloc:
        return BilibiliSource(url)
    elif 'douyin.com' in netloc:
        return DouyinSource(url)
    else:
        # Default to yt-dlp for other platforms
        return GenericSource(url)


class GenericSource(VideoSource):
    """Generic video source using yt-dlp auto-detection"""

    def validate(self) -> bool:
        return True  # Accepts any URL

    def extract_info(self) -> Dict:
        return {
            'platform': 'generic',
            'url': self.url
        }

    def download(self, output_dir: Path) -> Dict:
        """Download using yt-dlp auto-detection"""
        cmd = [
            'yt-dlp',
            '-f', 'best[ext=mp4]',
            '-o', str(output_dir / '%(title)s.%(ext)s'),
            '--print', 'json',
            '--no-playlist',
            self.url
        ]

        result = subprocess.run(cmd, capture_output=True, text=True, timeout=600)

        if result.returncode != 0:
            raise Exception(f"Generic download failed: {result.stderr}")

        video_info = json.loads(result.stdout)
        safe_title = YouTubeSource._sanitize_filename(video_info.get('title', 'video'))
        video_path = output_dir / f"{safe_title}.mp4"

        return {
            'path': str(video_path),
            'title': video_info.get('title', safe_title),
            'duration': video_info.get('duration', 0),
            'id': video_info.get('id', 'unknown'),
            'uploader': video_info.get('uploader', 'unknown'),
            'platform': video_info.get('extractor', 'generic'),
            'extractor_key': video_info.get('extractor_key', 'unknown')
        }


def download_video(url: str, output_dir: Path) -> Dict:
    """
    Download video from URL using appropriate source

    Args:
        url: Video URL or file path
        output_dir: Output directory path

    Returns:
        Video metadata dict
    """
    source = get_video_source(url)
    return source.download(output_dir)


# Supported platforms
SUPPORTED_PLATFORMS = {
    'youtube': 'YouTube',
    'bilibili': 'Bilibili',
    'douyin': 'Douyin (TikTok China)',
    'local': 'Local File',
    'direct': 'Direct URL',
    'generic': 'Generic (yt-dlp)'
}


def print_supported_platforms():
    """Print list of supported platforms"""
    print("Supported video platforms:")
    for key, name in SUPPORTED_PLATFORMS.items():
        print(f"  • {name}")
