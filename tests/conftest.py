"""
Pytest configuration and fixtures
"""

import sys
from pathlib import Path
import pytest
import tempfile
import shutil
from typing import Dict

# Add project root to path
project_root = Path(__file__).parent.parent
sys.path.insert(0, str(project_root))


@pytest.fixture
def temp_dir():
    """Create a temporary directory for tests"""
    temp_path = tempfile.mkdtemp()
    yield Path(temp_path)
    # Cleanup
    shutil.rmtree(temp_path, ignore_errors=True)


@pytest.fixture
def sample_transcript(temp_dir):
    """Create a sample transcript file"""
    transcript_file = temp_dir / "sample.srt"
    content = """1
00:00:00,000 --> 00:00:05,000
This is the first subtitle.

2
00:00:05,000 --> 00:00:10,000
This is the second subtitle.

3
00:00:10,000 --> 00:00:15,000
This is the third subtitle.
"""
    transcript_file.write_text(content, encoding='utf-8')
    return transcript_file


@pytest.fixture
def sample_package(temp_dir):
    """Create a sample Level 2 package"""
    package_file = temp_dir / "package.json"
    content = {
        "script_sections": [
            {
                "section": "Hook",
                "duration": 10,
                "narration": "Engaging hook text",
                "on_screen_text": "Hook Text",
                "visual_direction": "Test direction"
            },
            {
                "section": "Body",
                "duration": 30,
                "narration": "Main content",
                "on_screen_text": "Body Text",
                "visual_direction": "Test direction"
            },
            {
                "section": "Close",
                "duration": 10,
                "narration": "Closing statement",
                "on_screen_text": "CTA",
                "visual_direction": "Test direction"
            }
        ]
    }

    import json
    package_file.write_text(json.dumps(content, indent=2), encoding='utf-8')
    return package_file


@pytest.fixture
def mock_api_response():
    """Mock API response data"""
    return {
        "job_id": "test-job-id",
        "status": "pending",
        "message": "Job created successfully",
        "created_at": "2026-03-29T12:00:00"
    }


@pytest.fixture
def mock_job_data():
    """Mock job data"""
    return {
        "id": "test-job-id",
        "status": "completed",
        "level": 2,
        "progress": 100.0,
        "created_at": "2026-03-29T12:00:00",
        "updated_at": "2026-03-29T12:01:00",
        "result": {
            "level": 2,
            "output_path": "/output/package.json"
        }
    }


@pytest.fixture
def api_base_url():
    """Get API base URL for tests"""
    return "http://localhost:8000"


@pytest.fixture
def test_config():
    """Test configuration"""
    return {
        "content_type": "auto",
        "default_duration": 60
    }


# Asyncio configuration
def pytest_configure(config):
    """Configure pytest"""
    config.addinivalue_line(
        "markers",
        "asyncio: mark test as async"
    )
    config.addinivalue_line(
        "markers",
        "integration: mark test as integration test"
    )
    config.addinivalue_line(
        "markers",
        "slow: mark test as slow running"
    )
