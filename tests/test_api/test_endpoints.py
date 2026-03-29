"""
Test API Endpoints
"""

import pytest
from fastapi.testclient import TestClient
import tempfile
from pathlib import Path

from api.main import app
from api.database import get_db, Session
from api.models import Job, UploadedFile


@pytest.fixture
def api_client():
    """Create test API client"""
    return TestClient(app)


@pytest.fixture
def test_db():
    """Create test database session"""
    # Use in-memory database for tests
    from sqlalchemy import create_engine
    from api.models import Base

    engine = create_engine("sqlite:///:memory:")
    Base.metadata.create_all(bind=engine)

    from sqlalchemy.orm import sessionmaker
    TestingSessionLocal = sessionmaker(bind=engine)

    db = TestingSessionLocal()

    try:
        yield db
    finally:
        db.close()


class TestHealthEndpoint:
    """Test health check endpoint"""

    def test_health_check(self, api_client):
        """Test health check returns healthy status"""
        response = api_client.get("/api/v1/health")

        assert response.status_code == 200
        data = response.json()
        assert data["status"] == "healthy"
        assert "version" in data


class TestJobsEndpoint:
    """Test jobs management endpoints"""

    def test_list_jobs_empty(self, api_client, test_db):
        """Test listing jobs when none exist"""
        response = api_client.get("/api/v1/jobs")

        assert response.status_code == 200
        data = response.json()
        assert isinstance(data, list)
        assert len(data) == 0

    def test_list_jobs_with_jobs(self, api_client, test_db):
        """Test listing jobs with existing jobs"""
        # Create test job
        job = Job(
            id="test-job-1",
            status="pending",
            level=2,
            progress=0.0,
            created_at="2026-03-29T12:00:00",
            updated_at="2026-03-29T12:00:00"
        )
        test_db.add(job)
        test_db.commit()

        response = api_client.get("/api/v1/jobs")

        assert response.status_code == 200
        data = response.json()
        assert len(data) == 1
        assert data[0]["id"] == "test-job-1"

    def test_get_job_success(self, api_client, test_db):
        """Test getting existing job"""
        job = Job(
            id="test-job-1",
            status="completed",
            level=2,
            progress=100.0,
            created_at="2026-03-29T12:00:00",
            updated_at="2026-03-29T12:01:00",
            result={"output_path": "/test.json"}
        )
        test_db.add(job)
        test_db.commit()

        response = api_client.get("/api/v1/jobs/test-job-1")

        assert response.status_code == 200
        data = response.json()
        assert data["id"] == "test-job-1"
        assert data["status"] == "completed"

    def test_get_job_not_found(self, api_client, test_db):
        """Test getting non-existent job"""
        response = api_client.get("/api/v1/jobs/nonexistent")

        assert response.status_code == 404

    def test_delete_job(self, api_client, test_db):
        """Test deleting a job"""
        job = Job(
            id="test-job-1",
            status="pending",
            level=2,
            progress=0.0,
            created_at="2026-03-29T12:00:00",
            updated_at="2026-03-29T12:00:00"
        )
        test_db.add(job)
        test_db.commit()

        response = api_client.delete("/api/v1/jobs/test-job-1")

        assert response.status_code == 204

        # Verify job is deleted
        response = api_client.get("/api/v1/jobs/test-job-1")
        assert response.status_code == 404


class TestProcessEndpoint:
    """Test processing endpoint"""

    def test_process_no_input(self, api_client):
        """Test process without any input"""
        response = api_client.post("/api/v1/process", json={
            "level": 2
        })

        assert response.status_code == 400

    def test_process_invalid_level(self, api_client):
        """Test process with invalid level"""
        response = api_client.post("/api/v1/process", json={
            "level": 5,
            "transcript_path": "/test/file.srt"
        })

        assert response.status_code == 422  # Validation error

    def test_process_with_local_path(self, api_client, sample_transcript):
        """Test process with local file path"""
        response = api_client.post("/api/v1/process", json={
            "level": 2,
            "transcript_path": str(sample_transcript),
            "config": {"content_type": "auto"}
        })

        # Should accept the request (processing happens in background)
        assert response.status_code in [202, 200]
        data = response.json()
        assert "job_id" in data


class TestValidationEndpoint:
    """Test validation endpoint"""

    def test_validate_package(self, api_client, sample_package):
        """Test validating a package"""
        response = api_client.post("/api/v1/validate", json={
            "package_path": str(sample_package),
            "original_transcript": "Test transcript"
        })

        # Validation should complete
        assert response.status_code == 200
        data = response.json()
        assert "overall_score" in data
        assert "grade" in data
        assert "scores" in data

    def test_validate_missing_package(self, api_client):
        """Test validating non-existent package"""
        response = api_client.post("/api/v1/validate", json={
            "package_path": "/nonexistent/package.json"
        })

        assert response.status_code == 404


class TestUploadEndpoint:
    """Test file upload endpoint"""

    def test_upload_file(self, api_client, sample_transcript):
        """Test uploading a file"""
        with open(sample_transcript, "rb") as f:
            response = api_client.post(
                "/api/v1/upload",
                files={"file": ("sample.srt", f, "text/plain")}
            )

        assert response.status_code == 201
        data = response.json()
        assert "file_id" in data
        assert data["filename"] == "sample.srt"

    def test_upload_invalid_type(self, api_client, temp_dir):
        """Test uploading invalid file type"""
        invalid_file = temp_dir / "invalid.exe"
        invalid_file.write_text("test")

        with open(invalid_file, "rb") as f:
            response = api_client.post(
                "/api/v1/upload",
                files={"file": ("invalid.exe", f, "application/octet-stream")}
            )

        assert response.status_code == 400
