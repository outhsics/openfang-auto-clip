"""
Upload Router

File upload handling for transcripts and other files.
"""

from fastapi import APIRouter, HTTPException, status, UploadFile, File
from typing import Dict
import logging
import os
import uuid
from pathlib import Path
from datetime import datetime

from ..config import settings

logger = logging.getLogger(__name__)

router = APIRouter()

# Create upload directory
UPLOAD_DIR = settings.OUTPUT_DIR / "uploads"
UPLOAD_DIR.mkdir(parents=True, exist_ok=True)


@router.post("/upload", status_code=status.HTTP_201_CREATED)
async def upload_file(file: UploadFile = File(...)) -> Dict[str, str]:
    """
    Upload a transcript file.

    Supports: .srt, .vtt, .txt
    Max size: 100MB

    Args:
        file: Uploaded file

    Returns:
        File info with path and ID
    """
    try:
        # Validate file extension
        file_ext = Path(file.filename).suffix.lower()
        if file_ext not in settings.ALLOWED_EXTENSIONS:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=f"Invalid file type. Allowed: {', '.join(settings.ALLOWED_EXTENSIONS)}"
            )

        # Generate unique filename
        file_id = str(uuid.uuid4())
        filename = f"{file_id}{file_ext}"
        file_path = UPLOAD_DIR / filename

        # Save file
        content = await file.read()

        # Check file size
        file_size = len(content)
        if file_size > settings.MAX_UPLOAD_SIZE:
            raise HTTPException(
                status_code=status.HTTP_413_REQUEST_ENTITY_TOO_LARGE,
                detail=f"File too large. Max size: {settings.MAX_UPLOAD_SIZE / 1024 / 1024}MB"
            )

        with open(file_path, "wb") as f:
            f.write(content)

        logger.info(f"File uploaded: {file.filename} -> {filename} ({file_size} bytes)")

        return {
            "file_id": file_id,
            "filename": file.filename,
            "path": str(file_path),
            "size": file_size,
            "uploaded_at": datetime.now().isoformat()
        }

    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Upload failed: {e}", exc_info=True)
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Upload failed: {str(e)}"
        )


@router.get("/uploads/{file_id}")
async def get_upload_info(file_id: str) -> Dict[str, str]:
    """
    Get upload file information.

    Args:
        file_id: File ID

    Returns:
        File information
    """
    # Find file by ID
    matching_files = list(UPLOAD_DIR.glob(f"{file_id}.*"))

    if not matching_files:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"File {file_id} not found"
        )

    file_path = matching_files[0]
    file_stat = file_path.stat()

    return {
        "file_id": file_id,
        "path": str(file_path),
        "size": file_stat.st_size,
        "created_at": datetime.fromtimestamp(file_stat.st_ctime).isoformat()
    }


@router.delete("/uploads/{file_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_upload(file_id: str) -> None:
    """
    Delete an uploaded file.

    Args:
        file_id: File ID
    """
    matching_files = list(UPLOAD_DIR.glob(f"{file_id}.*"))

    if not matching_files:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"File {file_id} not found"
        )

    for file_path in matching_files:
        file_path.unlink()

    logger.info(f"File deleted: {file_id}")
