"""
OpenFang SDK Exceptions
"""

from typing import Optional, Dict, Any


class OpenFangError(Exception):
    """Base exception for OpenFang SDK"""

    def __init__(self, message: str, details: Optional[Dict[str, Any]] = None):
        super().__init__(message)
        self.message = message
        self.details = details or {}

    def __str__(self) -> str:
        if self.details:
            return f"{self.message} - {self.details}"
        return self.message


class APIError(OpenFangError):
    """API request failed"""

    def __init__(
        self,
        message: str,
        status_code: Optional[int] = None,
        response: Optional[Dict[str, Any]] = None
    ):
        super().__init__(message)
        self.status_code = status_code
        self.response = response


class ValidationError(OpenFangError):
    """Validation failed"""

    pass


class UploadError(OpenFangError):
    """File upload failed"""

    pass


class JobNotFoundError(OpenFangError):
    """Job not found"""

    def __init__(self, job_id: str):
        super().__init__(f"Job {job_id} not found")
        self.job_id = job_id


class AuthenticationError(OpenFangError):
    """Authentication failed"""

    pass


class RateLimitError(OpenFangError):
    """Rate limit exceeded"""

    def __init__(self, message: str = "Rate limit exceeded", retry_after: Optional[int] = None):
        super().__init__(message)
        self.retry_after = retry_after


class ProcessingError(OpenFangError):
    """Processing failed"""

    pass
