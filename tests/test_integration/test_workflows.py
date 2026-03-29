"""
Integration Tests
"""

import pytest
import tempfile
from pathlib import Path
import time

from openfang_sdk import Client


@pytest.mark.integration
class TestSDKAPIIntegration:
    """Integration tests between SDK and API"""

    @pytest.fixture
    def api_server(self):
        """Start API server for integration tests"""
        # This would start the actual API server
        # For now, we'll skip this
        pytest.skip("Requires running API server")

    @pytest.fixture
    def client(self):
        """Create SDK client for testing"""
        return Client(base_url="http://localhost:8000")

    def test_full_workflow(self, client, sample_transcript):
        """Test complete workflow: upload -> process -> validate"""
        # Note: This test requires API server to be running
        pytest.skip("Requires running API server")


@pytest.mark.integration
class TestDatabasePersistence:
    """Test database persistence across operations"""

    def test_job_persistence(self, test_db):
        """Test that jobs persist in database"""
        from api.models import Job

        # Create a job
        job = Job(
            id="persist-test",
            status="pending",
            level=2,
            progress=0.0,
            created_at="2026-03-29T12:00:00",
            updated_at="2026-03-29T12:00:00"
        )
        test_db.add(job)
        test_db.commit()

        # Retrieve job
        retrieved = test_db.query(Job).filter(Job.id == "persist-test").first()

        assert retrieved is not None
        assert retrieved.status == "pending"
        assert retrieved.level == 2

    def test_job_update(self, test_db):
        """Test updating job in database"""
        from api.models import Job

        job = Job(
            id="update-test",
            status="pending",
            level=2,
            progress=0.0,
            created_at="2026-03-29T12:00:00",
            updated_at="2026-03-29T12:00:00"
        )
        test_db.add(job)
        test_db.commit()

        # Update job
        job.status = "processing"
        job.progress = 50.0
        test_db.commit()

        # Retrieve and verify
        test_db.refresh(job)
        assert job.status == "processing"
        assert job.progress == 50.0


@pytest.mark.integration
class TestEndToEndWorkflows:
    """Test end-to-end workflows"""

    @pytest.mark.slow
    def test_complete_processing_workflow(self, sample_transcript, sample_package):
        """Test complete workflow from transcript to validated package"""
        # This would test the entire pipeline
        pytest.skip("Requires full system setup")

    def test_validation_workflow(self, sample_package):
        """Test validation workflow"""
        from scripts.level2_validation import calculate_quality_scores

        # Load package
        import json
        with open(sample_package, 'r') as f:
            package = json.load(f)

        # Validate
        scores = calculate_quality_scores(package, "Test transcript")

        assert "overall" in scores
        assert 0 <= scores["overall"] <= 10
        assert "grade" in scores
