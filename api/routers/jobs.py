"""
Jobs Router

Job management endpoints.
"""

from fastapi import APIRouter, HTTPException, status
from typing import List, Dict, Optional
from pydantic import BaseModel
import logging

logger = logging.getLogger(__name__)

router = APIRouter()


# In-memory job storage (will be replaced with database later)
_jobs: Dict[str, Dict] = {}


class JobStatus(BaseModel):
    """Job status model"""
    id: str
    status: str  # pending, processing, completed, failed
    level: int
    progress: float  # 0-100
    created_at: str
    updated_at: str
    result: Optional[Dict] = None
    error: Optional[str] = None


@router.get("", response_model=List[JobStatus])
async def list_jobs(
    status: Optional[str] = None,
    limit: int = 50
) -> List[JobStatus]:
    """
    List all jobs.

    Args:
        status: Filter by status (pending, processing, completed, failed)
        limit: Maximum number of jobs to return

    Returns:
        List of jobs
    """
    jobs = list(_jobs.values())

    # Filter by status if provided
    if status:
        jobs = [j for j in jobs if j["status"] == status]

    # Sort by created_at (newest first)
    jobs.sort(key=lambda j: j["created_at"], reverse=True)

    # Apply limit
    jobs = jobs[:limit]

    return [JobStatus(**j) for j in jobs]


@router.get("/{job_id}", response_model=JobStatus)
async def get_job(job_id: str) -> JobStatus:
    """
    Get job details by ID.

    Args:
        job_id: Job ID

    Returns:
        Job details

    Raises:
        HTTPException: If job not found
    """
    if job_id not in _jobs:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Job {job_id} not found"
        )

    return JobStatus(**_jobs[job_id])


@router.delete("/{job_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_job(job_id: str) -> None:
    """
    Cancel or delete a job.

    Args:
        job_id: Job ID

    Raises:
        HTTPException: If job not found
    """
    if job_id not in _jobs:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Job {job_id} not found"
        )

    # In a real implementation, you would:
    # 1. Cancel the job if it's running
    # 2. Clean up resources
    # 3. Delete from database

    del _jobs[job_id]

    logger.info(f"Job {job_id} deleted")
