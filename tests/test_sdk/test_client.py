"""
Test SDK Client
"""

import pytest
from unittest.mock import Mock, patch, AsyncMock
import httpx

from openfang_sdk import Client
from openfang_sdk.exceptions import (
    APIError,
    ValidationError,
    JobNotFoundError,
    ProcessingError
)


class TestClientInitialization:
    """Test client initialization"""

    def test_init_default(self):
        """Test default initialization"""
        client = Client()
        assert client.base_url == "http://localhost:8000"
        assert client.api_key is None
        assert client.timeout == 30.0
        assert client.max_retries == 3

    def test_init_with_api_key(self):
        """Test initialization with API key"""
        client = Client(api_key="test-key")
        assert client.api_key == "test-key"

    def test_init_with_custom_url(self):
        """Test initialization with custom URL"""
        client = Client(base_url="http://custom:9000")
        assert client.base_url == "http://custom:9000"

    def test_headers_without_api_key(self):
        """Test headers without API key"""
        client = Client()
        headers = client._get_headers()
        assert "Authorization" not in headers
        assert headers["Content-Type"] == "application/json"

    def test_headers_with_api_key(self):
        """Test headers with API key"""
        client = Client(api_key="test-key")
        headers = client._get_headers()
        assert headers["Authorization"] == "Bearer test-key"


class TestHealthCheck:
    """Test health check endpoint"""

    @patch('openfang_sdk.client.httpx.Client')
    def test_health_check_success(self, mock_httpx):
        """Test successful health check"""
        mock_response = Mock()
        mock_response.json.return_value = {
            "status": "healthy",
            "version": "0.5.0"
        }
        mock_response.status_code = 200

        mock_client = Mock()
        mock_client.request.return_value = mock_response
        mock_httpx.return_value = mock_client

        client = Client()
        result = client.health_check()

        assert result["status"] == "healthy"
        assert result["version"] == "0.5.0"


class TestProcess:
    """Test process endpoint"""

    def test_process_success(self, sample_transcript):
        """Test successful processing request"""
        with patch('openfang_sdk.client.httpx.Client') as mock_httpx:
            mock_response = Mock()
            mock_response.json.return_value = {
                "job_id": "test-job-id",
                "status": "pending"
            }
            mock_response.status_code = 202

            mock_client = Mock()
            mock_client.request.return_value = mock_response
            mock_httpx.return_value = mock_client

            client = Client()
            result = client.process(
                level=2,
                transcript_path=str(sample_transcript)
            )

            assert result["job_id"] == "test-job-id"
            assert result["status"] == "pending"

    def test_process_invalid_level(self):
        """Test process with invalid level"""
        client = Client()
        with pytest.raises(ValidationError):
            client.process(level=5)

    def test_process_no_input(self):
        """Test process without any input"""
        client = Client()
        with pytest.raises(ValidationError):
            client.process(level=2)


class TestJobs:
    """Test job management endpoints"""

    def test_list_jobs(self):
        """Test listing jobs"""
        with patch('openfang_sdk.client.httpx.Client') as mock_httpx:
            mock_response = Mock()
            mock_response.json.return_value = [
                {"id": "job1", "status": "completed"},
                {"id": "job2", "status": "processing"}
            ]
            mock_response.status_code = 200

            mock_client = Mock()
            mock_client.request.return_value = mock_response
            mock_httpx.return_value = mock_client

            client = Client()
            jobs = client.list_jobs()

            assert len(jobs) == 2

    def test_get_job_success(self):
        """Test getting job details"""
        with patch('openfang_sdk.client.httpx.Client') as mock_httpx:
            mock_response = Mock()
            mock_response.json.return_value = {
                "id": "test-job",
                "status": "completed",
                "progress": 100.0
            }
            mock_response.status_code = 200

            mock_client = Mock()
            mock_client.request.return_value = mock_response
            mock_httpx.return_value = mock_client

            client = Client()
            job = client.get_job("test-job")

            assert job["status"] == "completed"

    def test_get_job_not_found(self):
        """Test getting non-existent job"""
        with patch('openfang_sdk.client.httpx.Client') as mock_httpx:
            mock_response = Mock()
            mock_response.json.return_value = {"detail": "Job not found"}
            mock_response.status_code = 404

            mock_client = Mock()
            mock_client.request.return_value = mock_response
            mock_httpx.return_value = mock_client

            client = Client()
            with pytest.raises(JobNotFoundError):
                client.get_job("nonexistent")

    def test_delete_job(self):
        """Test deleting a job"""
        with patch('openfang_sdk.client.httpx.Client') as mock_httpx:
            mock_response = Mock()
            mock_response.status_code = 204

            mock_client = Mock()
            mock_client.request.return_value = mock_response
            mock_httpx.return_value = mock_client

            client = Client()
            # Should not raise exception
            client.delete_job("test-job")


class TestWaitForJob:
    """Test wait_for_job method"""

    @patch('openfang_sdk.client.time.sleep')
    @patch('openfang_sdk.client.Client.get_job')
    def test_wait_for_completion(self, mock_get_job, mock_sleep):
        """Test waiting for job completion"""
        # Mock job progression
        mock_get_job.side_effect = [
            {"id": "test-job", "status": "processing", "progress": 50.0},
            {"id": "test-job", "status": "completed", "progress": 100.0}
        ]

        client = Client()
        result = client.wait_for_job("test-job", check_interval=0.1)

        assert result["status"] == "completed"
        assert mock_get_job.call_count == 2

    @patch('openfang_sdk.client.time.sleep')
    @patch('openfang_sdk.client.Client.get_job')
    def test_wait_for_failure(self, mock_get_job, mock_sleep):
        """Test waiting for failed job"""
        mock_get_job.return_value = {
            "id": "test-job",
            "status": "failed",
            "error": "Processing failed"
        }

        client = Client()
        with pytest.raises(ProcessingError):
            client.wait_for_job("test-job", check_interval=0.1)


class TestValidation:
    """Test validation endpoint"""

    def test_validate_package(self, sample_package):
        """Test package validation"""
        with patch('openfang_sdk.client.httpx.Client') as mock_httpx:
            mock_response = Mock()
            mock_response.json.return_value = {
                "overall_score": 9.5,
                "grade": "A",
                "scores": {
                    "coherence": 9.8,
                    "actionability": 9.5
                },
                "copyright_risk": {
                    "risk_level": "Safe"
                },
                "production_ready": True,
                "issues": [],
                "recommendations": []
            }
            mock_response.status_code = 200

            mock_client = Mock()
            mock_client.request.return_value = mock_response
            mock_httpx.return_value = mock_client

            client = Client()
            result = client.validate_package(str(sample_package))

            assert result["overall_score"] == 9.5
            assert result["grade"] == "A"
            assert result["production_ready"] is True


class TestContextManager:
    """Test context manager support"""

    @patch('openfang_sdk.client.httpx.Client')
    def test_context_manager(self, mock_httpx):
        """Test using client as context manager"""
        mock_response = Mock()
        mock_response.json.return_value = {"status": "healthy"}
        mock_response.status_code = 200

        mock_client = Mock()
        mock_client.request.return_value = mock_response
        mock_httpx.return_value = mock_client

        with Client() as client:
            result = client.health_check()
            assert result["status"] == "healthy"

        # Client should be closed after context
        assert mock_client.close.called


class TestErrorHandling:
    """Test error handling"""

    def test_api_error_propagation(self):
        """Test API errors are properly propagated"""
        with patch('openfang_sdk.client.httpx.Client') as mock_httpx:
            mock_response = Mock()
            mock_response.json.return_value = {"detail": "Bad request"}
            mock_response.status_code = 400
            mock_response.headers = {"content-type": "application/json"}

            mock_client = Mock()
            mock_client.request.return_value = mock_response
            mock_httpx.return_value = mock_client

            client = Client()
            with pytest.raises(APIError):
                client.process(level=2, transcript_path="test")

    @patch('openfang_sdk.client.time.sleep')
    def test_retry_logic(self, mock_sleep):
        """Test retry logic on transient errors"""
        with patch('openfang_sdk.client.httpx.Client') as mock_httpx:
            # First two calls fail, third succeeds
            call_count = [0]

            def side_effect(*args, **kwargs):
                call_count[0] += 1
                if call_count[0] < 3:
                    raise httpx.NetworkError("Connection error")

                mock_response = Mock()
                mock_response.json.return_value = {"status": "healthy"}
                mock_response.status_code = 200
                return mock_response

            mock_client = Mock()
            mock_client.request = side_effect
            mock_httpx.return_value = mock_client

            client = Client(max_retries=3)
            result = client.health_check()

            assert result["status"] == "healthy"
            assert call_count[0] == 3
