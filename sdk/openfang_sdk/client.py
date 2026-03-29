"""
OpenFang SDK Client

Main client for interacting with OpenFang API.
"""

import time
from typing import Dict, List, Optional, Any, BinaryIO
from pathlib import Path
import httpx

from .exceptions import (
    APIError,
    ValidationError,
    UploadError,
    JobNotFoundError,
    AuthenticationError,
    RateLimitError,
    ProcessingError
)


class Client:
    """
    OpenFang Auto Clip API Client

    Example:
        >>> from openfang_sdk import Client
        >>> client = Client(api_key="your-api-key")
        >>>
        >>> # Process a transcript
        >>> job = client.process(
        ...     transcript_path="transcript.srt",
        ...     level=2,
        ...     config={"content_type": "auto"}
        ... )
        >>>
        >>> # Wait for completion
        >>> result = client.wait_for_job(job["job_id"])
        >>> print(f"Status: {result['status']}")
    """

    def __init__(
        self,
        api_key: Optional[str] = None,
        base_url: str = "http://localhost:8000",
        timeout: float = 30.0,
        max_retries: int = 3
    ):
        """
        Initialize the client.

        Args:
            api_key: API key for authentication (optional for now)
            base_url: Base URL of the API
            timeout: Request timeout in seconds
            max_retries: Maximum number of retries for failed requests
        """
        self.api_key = api_key
        self.base_url = base_url.rstrip("/")
        self.timeout = timeout
        self.max_retries = max_retries

        # Create HTTP client
        self.client = httpx.Client(
            base_url=self.base_url,
            timeout=self.timeout,
            headers=self._get_headers()
        )

    def _get_headers(self) -> Dict[str, str]:
        """Get default headers for requests"""
        headers = {
            "Content-Type": "application/json",
            "User-Agent": f"OpenFang-SDK/0.5.0"
        }

        if self.api_key:
            headers["Authorization"] = f"Bearer {self.api_key}"

        return headers

    def _request(
        self,
        method: str,
        endpoint: str,
        **kwargs
    ) -> Dict[str, Any]:
        """
        Make an API request with retry logic.

        Args:
            method: HTTP method
            endpoint: API endpoint
            **kwargs: Additional arguments for httpx.request

        Returns:
            Response data as dictionary

        Raises:
            APIError: If request fails
        """
        url = f"{self.base_url}{endpoint}"
        last_error = None

        for attempt in range(self.max_retries):
            try:
                response = self.client.request(method, endpoint, **kwargs)

                # Handle rate limiting
                if response.status_code == 429:
                    retry_after = int(response.headers.get("Retry-After", 5))
                    raise RateLimitError(retry_after=retry_after)

                # Handle authentication errors
                if response.status_code == 401:
                    raise AuthenticationError("Invalid API key")

                # Handle other errors
                if response.status_code >= 400:
                    error_data = response.json() if response.headers.get("content-type") == "application/json" else {}
                    raise APIError(
                        error_data.get("detail", "Request failed"),
                        status_code=response.status_code,
                        response=error_data
                    )

                return response.json()

            except RateLimitError as e:
                if attempt < self.max_retries - 1:
                    time.sleep(e.retry_after or 5)
                    continue
                raise

            except (httpx.TimeoutException, httpx.NetworkError) as e:
                last_error = e
                if attempt < self.max_retries - 1:
                    time.sleep(2 ** attempt)  # Exponential backoff
                    continue
                raise APIError(f"Request failed: {str(e)}")

            except APIError:
                raise

        raise APIError(f"Request failed after {self.max_retries} retries: {last_error}")

    def health_check(self) -> Dict[str, str]:
        """
        Check API health.

        Returns:
            Health status

        Raises:
            APIError: If health check fails
        """
        return self._request("GET", "/api/v1/health")

    def upload_file(
        self,
        file_path: str,
        chunk_size: int = 8192
    ) -> Dict[str, Any]:
        """
        Upload a transcript file.

        Args:
            file_path: Path to file to upload
            chunk_size: Upload chunk size in bytes

        Returns:
            Upload info with file_id and path

        Raises:
            UploadError: If upload fails
            ValidationError: If file type is invalid
        """
        file_path = Path(file_path)

        if not file_path.exists():
            raise ValidationError(f"File not found: {file_path}")

        # Validate file type
        allowed_extensions = {".srt", ".vtt", ".txt"}
        if file_path.suffix.lower() not in allowed_extensions:
            raise ValidationError(
                f"Invalid file type. Allowed: {', '.join(allowed_extensions)}"
            )

        try:
            with open(file_path, "rb") as f:
                files = {"file": (file_path.name, f, "application/octet-stream")}
                response = self._request("POST", "/api/v1/upload", files=files)
                return response

        except APIError as e:
            raise UploadError(f"Upload failed: {e.message}")

    def process(
        self,
        level: int = 2,
        transcript_path: Optional[str] = None,
        video_url: Optional[str] = None,
        uploaded_file_id: Optional[str] = None,
        config: Optional[Dict[str, Any]] = None
    ) -> Dict[str, Any]:
        """
        Process a video or transcript.

        Args:
            level: Transformation level (1, 2, or 3)
            transcript_path: Path to transcript file
            video_url: URL to video (YouTube, etc.)
            uploaded_file_id: ID of previously uploaded file
            config: Processing configuration

        Returns:
            Job info with job_id

        Raises:
            ValidationError: If parameters are invalid
            ProcessingError: If processing fails to start

        Example:
            >>> job = client.process(
            ...     level=2,
            ...     transcript_path="transcript.srt",
            ...     config={"content_type": "auto", "default_duration": 60}
            ... )
            >>> print(job["job_id"])
        """
        # Validate level
        if level not in [1, 2, 3]:
            raise ValidationError(f"Invalid level: {level}. Must be 1, 2, or 3")

        # Validate input
        if not any([transcript_path, video_url, uploaded_file_id]):
            raise ValidationError(
                "Either transcript_path, video_url, or uploaded_file_id must be provided"
            )

        # Build request data
        data = {
            "level": level,
            "config": config or {}
        }

        if transcript_path:
            data["transcript_path"] = transcript_path
        if video_url:
            data["video_url"] = video_url
        if uploaded_file_id:
            data["uploaded_file_id"] = uploaded_file_id

        try:
            return self._request("POST", "/api/v1/process", json=data)
        except APIError as e:
            raise ProcessingError(f"Failed to start processing: {e.message}")

    def list_jobs(
        self,
        status: Optional[str] = None,
        limit: int = 50
    ) -> List[Dict[str, Any]]:
        """
        List all jobs.

        Args:
            status: Filter by status (pending, processing, completed, failed)
            limit: Maximum number of jobs to return

        Returns:
            List of jobs

        Example:
            >>> jobs = client.list_jobs(status="completed", limit=10)
            >>> for job in jobs:
            ...     print(f"{job['id']}: {job['status']}")
        """
        params = {"limit": limit}
        if status:
            params["status"] = status

        return self._request("GET", "/api/v1/jobs", params=params)

    def get_job(self, job_id: str) -> Dict[str, Any]:
        """
        Get job details.

        Args:
            job_id: Job ID

        Returns:
            Job details

        Raises:
            JobNotFoundError: If job not found

        Example:
            >>> job = client.get_job("abc123")
            >>> print(f"Status: {job['status']}, Progress: {job['progress']}%")
        """
        try:
            return self._request("GET", f"/api/v1/jobs/{job_id}")
        except APIError as e:
            if e.status_code == 404:
                raise JobNotFoundError(job_id)
            raise

    def delete_job(self, job_id: str) -> None:
        """
        Delete/cancel a job.

        Args:
            job_id: Job ID

        Raises:
            JobNotFoundError: If job not found

        Example:
            >>> client.delete_job("abc123")
        """
        try:
            self._request("DELETE", f"/api/v1/jobs/{job_id}")
        except APIError as e:
            if e.status_code == 404:
                raise JobNotFoundError(job_id)
            raise

    def wait_for_job(
        self,
        job_id: str,
        check_interval: float = 2.0,
        timeout: Optional[float] = None
    ) -> Dict[str, Any]:
        """
        Wait for a job to complete.

        Args:
            job_id: Job ID
            check_interval: Time between checks in seconds
            timeout: Maximum time to wait in seconds (None = no timeout)

        Returns:
            Completed job details

        Raises:
            JobNotFoundError: If job not found
            ProcessingError: If job fails or timeout occurs

        Example:
            >>> result = client.wait_for_job("abc123", check_interval=1.0)
            >>> print(f"Result: {result['result']}")
        """
        start_time = time.time()

        while True:
            job = self.get_job(job_id)

            # Check if complete
            if job["status"] == "completed":
                return job

            # Check if failed
            if job["status"] == "failed":
                raise ProcessingError(
                    f"Job {job_id} failed: {job.get('error', 'Unknown error')}"
                )

            # Check timeout
            if timeout and (time.time() - start_time) > timeout:
                raise ProcessingError(
                    f"Job {job_id} timed out after {timeout} seconds"
                )

            # Wait before next check
            time.sleep(check_interval)

    def validate_package(
        self,
        package_path: str,
        original_transcript: Optional[str] = None
    ) -> Dict[str, Any]:
        """
        Validate a Level 2 package.

        Args:
            package_path: Path to Level 2 package JSON
            original_transcript: Original transcript text for copyright check

        Returns:
            Validation results with scores and recommendations

        Raises:
            ValidationError: If validation fails

        Example:
            >>> result = client.validate_package("package.json")
            >>> print(f"Score: {result['overall_score']}/10 ({result['grade']})")
            >>> print(f"Production Ready: {result['production_ready']}")
        """
        data = {
            "package_path": package_path,
            "original_transcript": original_transcript or ""
        }

        try:
            return self._request("POST", "/api/v1/validate", json=data)
        except APIError as e:
            raise ValidationError(f"Validation failed: {e.message}")

    def close(self):
        """Close the HTTP client"""
        self.client.close()

    def __enter__(self):
        """Context manager entry"""
        return self

    def __exit__(self, exc_type, exc_val, exc_tb):
        """Context manager exit"""
        self.close()
