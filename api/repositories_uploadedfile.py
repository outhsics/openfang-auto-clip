"""
Uploaded File Repository

Database operations for UploadedFile model.
"""

from typing import List, Optional, Dict
from datetime import datetime
from sqlalchemy.orm import Session

from ..models import UploadedFile
from ..database import get_database_manager


class UploadedFileRepository:
    """Repository for UploadedFile database operations"""

    def __init__(self, db: Optional[Session] = None):
        """
        Initialize uploaded file repository.

        Args:
            db: Database session (optional, creates new if not provided)
        """
        self.db_manager = get_database_manager()
        self.db = db
        self.should_close = False

        if self.db is None:
            self.db = self.db_manager.create_session()
            self.should_close = True

    def __enter__(self):
        """Context manager entry"""
        return self

    def __exit__(self, exc_type, exc_val, exc_tb):
        """Context manager exit"""
        if self.should_close:
            self.db.close()

    def create(self, file_data: Dict) -> UploadedFile:
        """
        Create a new uploaded file record.

        Args:
            file_data: File data dictionary

        Returns:
            Created UploadedFile model
        """
        uploaded_file = UploadedFile(
            file_id=file_data["file_id"],
            filename=file_data["filename"],
            path=file_data["path"],
            size=file_data["size"],
            uploaded_at=file_data["uploaded_at"],
            metadata=file_data.get("metadata")
        )

        self.db.add(uploaded_file)
        self.db.commit()
        self.db.refresh(uploaded_file)

        return uploaded_file

    def get_by_id(self, file_id: str) -> Optional[UploadedFile]:
        """
        Get uploaded file by ID.

        Args:
            file_id: File ID

        Returns:
            UploadedFile model or None if not found
        """
        return self.db.query(UploadedFile).filter(UploadedFile.file_id == file_id).first()

    def delete(self, file_id: str) -> bool:
        """
        Delete an uploaded file record.

        Args:
            file_id: File ID

        Returns:
            True if deleted, False if not found
        """
        uploaded_file = self.get_by_id(file_id)
        if not uploaded_file:
            return False

        self.db.delete(uploaded_file)
        self.db.commit()

        return True
