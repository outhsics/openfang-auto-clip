"""
Upload Router

File upload handling with database persistence.
"""

from fastapi import APIRouter, HTTPException, status, UploadFile, File, Depends
from typing import Dict
import logging
import os
import uuid
from pathlib import Path
from datetime import datetime
from sqlalchemy.orm import Session

from ..config import settings
from ..database import get_db
from ..repositories import UploadedFileRepository

logger = logging.getLogger(__name__)

router = APIRouter()

# Create upload directory
UPLOAD_DIR = settings.OUTPUT_DIR / "uploads"
UPLOAD_DIR.mkdir(parents=True, exist_ok=True)


@router.post("/upload", status_code=status.HTTP_201_CREATED)
async def upload_file(
    file: UploadFile = File(...),
    db: Session = Depends(get_db)
) -> Dict[str, str]:
    """
    Upload a transcript file.

    Supports: .srt, .vtt, .txt
    Max size: 100MB

    Args:
        file: Uploaded file
        db: Database session

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

        # Save to database
        uploaded_at = datetime.now().isoformat()
        file_data = {
            "file_id": file_id,
            "filename": file.filename,
            "path": str(file_path),
            "size": file_size,
            "uploaded_at": uploaded_at
        }

        with UploadedFileRepository(db) as repo:
            repo.create(file_data)

        logger.info(f"File uploaded: {file.filename} -> {filename} ({file_size} bytes)")

        return {
            "file_id": file_id,
            "filename": file.filename,
            "path": str(file_path),
            "size": file_size,
            "uploaded_at": uploaded_at
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
async def get_upload_info(
    file_id: str,
    db: Session = Depends(get_db)
) -> Dict[str, str]:
    """
    Get upload file information.

    Args:
        file_id: File ID
        db: Database session

    Returns:
        File information
    """
    with UploadedFileRepository(db) as repo:
        uploaded_file = repo.get_by_id(file_id)
        if not uploaded_file:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"File {file_id} not found"
            )

        return uploaded_file.to_dict()


@router.delete("/uploads/{file_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_upload(
    file_id: str,
    db: Session = Depends(get_db)
) -> None:
    """
    Delete an uploaded file.

    Args:
        file_id: File ID
        db: Database session
    """
    # Get file info from database
    with UploadedFileRepository(db) as repo:
        uploaded_file = repo.get_by_id(file_id)
        if not uploaded_file:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"File {file_id} not found"
            )

        file_path = Path(uploaded_file.path)

        # Delete from filesystem
        if file_path.exists():
            file_path.unlink()

        # Delete from database
        repo.delete(file_id)

        logger.info(f"File deleted: {file_id}")
