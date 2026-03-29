"""
Process Router

Video/transcript processing endpoints.
"""

from fastapi import APIRouter, HTTPException, status, BackgroundTasks
from pydantic import BaseModel, Field
from typing import Optional, Dict, List
import logging
import uuid
from datetime import datetime
from pathlib import Path

logger = logging.getLogger(__name__)

router = APIRouter()


class ProcessRequest(BaseModel):
    """Request to process a video/transcript"""
    level: int = Field(..., ge=1, le=3, description="Transform level (1, 2, or 3)")
    transcript_path: Optional[str] = Field(None, description="Path to transcript file")
    video_url: Optional[str] = Field(None, description="URL to video (YouTube, etc.)")
    uploaded_file_id: Optional[str] = Field(None, description="Uploaded file ID")
    config: Optional[Dict] = Field(default_factory=dict, description="Processing configuration")

    class Config:
        json_schema_extra = {
            "example": {
                "level": 2,
                "transcript_path": "/path/to/transcript.srt",
                "config": {
                    "default_duration": 60,
                    "content_type": "auto"
                }
            }
        }


class ProcessResponse(BaseModel):
    """Response from process request"""
    job_id: str
    status: str
    message: str
    created_at: str


@router.post("/process", response_model=ProcessResponse, status_code=status.HTTP_202_ACCEPTED)
async def process_video(
    request: ProcessRequest,
    background_tasks: BackgroundTasks
) -> ProcessResponse:
    """
    Process a video or transcript.

    Creates a new processing job and returns immediately with a job ID.

    Args:
        request: Process request with level and input
        background_tasks: FastAPI background tasks

    Returns:
        Job ID and status
    """
    # Validate request
    if not request.transcript_path and not request.video_url and not request.uploaded_file_id:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Either transcript_path, video_url, or uploaded_file_id must be provided"
        )

    # Resolve transcript path from uploaded file
    transcript_path = request.transcript_path
    if request.uploaded_file_id:
        from .upload import UPLOAD_DIR
        import glob
        matching_files = list(UPLOAD_DIR.glob(f"{request.uploaded_file_id}.*"))
        if not matching_files:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"Uploaded file {request.uploaded_file_id} not found"
            )
        transcript_path = str(matching_files[0])

    # Create job
    job_id = str(uuid.uuid4())
    created_at = datetime.now().isoformat()

    # Store job (in a real implementation, use database)
    from .jobs import _jobs
    _jobs[job_id] = {
        "id": job_id,
        "status": "pending",
        "level": request.level,
        "progress": 0.0,
        "created_at": created_at,
        "updated_at": created_at,
        "result": None,
        "error": None
    }

    # Add background task to process
    background_tasks.add_task(
        _process_job,
        job_id,
        request.level,
        transcript_path,
        request.video_url,
        request.config
    )

    logger.info(f"Job {job_id} created for level {request.level} processing")

    return ProcessResponse(
        job_id=job_id,
        status="pending",
        message="Job created successfully",
        created_at=created_at
    )


async def _process_job(
    job_id: str,
    level: int,
    transcript_path: Optional[str],
    video_url: Optional[str],
    config: Dict
):
    """
    Background task to process a job.

    This performs actual processing using the OpenFang pipeline.
    """
    from .jobs import _jobs
    from ..services import get_processing_service

    try:
        # Update status to processing
        _jobs[job_id]["status"] = "processing"
        _jobs[job_id]["updated_at"] = datetime.now().isoformat()

        logger.info(f"Job {job_id} starting processing...")

        # Get processing service
        service = get_processing_service()

        # Progress callback
        async def update_progress(percent, message):
            _jobs[job_id]["progress"] = float(percent)
            _jobs[job_id]["updated_at"] = datetime.now().isoformat()
            logger.info(f"Job {job_id} progress: {percent}% - {message}")

        # Process transcript
        if transcript_path:
            result = await service.process_transcript(
                transcript_path=transcript_path,
                level=level,
                config=config,
                progress_callback=update_progress
            )

            # Complete job
            _jobs[job_id]["status"] = "completed"
            _jobs[job_id]["progress"] = 100.0
            _jobs[job_id]["updated_at"] = datetime.now().isoformat()
            _jobs[job_id]["result"] = result

            logger.info(f"Job {job_id} completed successfully")

        elif video_url:
            # TODO: Implement video download and processing
            # For now, mark as failed
            raise NotImplementedError("Video URL processing not yet implemented")

        else:
            raise ValueError("Either transcript_path or video_url must be provided")

    except Exception as e:
        logger.error(f"Job {job_id} failed: {e}", exc_info=True)
        _jobs[job_id]["status"] = "failed"
        _jobs[job_id]["error"] = str(e)
        _jobs[job_id]["updated_at"] = datetime.now().isoformat()
