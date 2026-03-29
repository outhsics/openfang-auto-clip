"""
Job Repository

Database operations for Job model.
"""

from typing import List, Optional, Dict
from datetime import datetime
from sqlalchemy.orm import Session
from sqlalchemy import desc

from ..models import Job, UploadedFile
from ..database import get_database_manager


class JobRepository:
    """Repository for Job database operations"""

    def __init__(self, db: Optional[Session] = None):
        """
        Initialize job repository.

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

    def create(self, job_data: Dict) -> Job:
        """
        Create a new job.

        Args:
            job_data: Job data dictionary

        Returns:
            Created Job model
        """
        job = Job(
            id=job_data["id"],
            status=job_data.get("status", "pending"),
            level=job_data.get("level", 2),
            progress=job_data.get("progress", 0.0),
            created_at=job_data.get("created_at", datetime.now().isoformat()),
            updated_at=job_data.get("updated_at", datetime.now().isoformat()),
            result=job_data.get("result"),
            error=job_data.get("error"),
            transcript_path=job_data.get("transcript_path"),
            video_url=job_data.get("video_url"),
            uploaded_file_id=job_data.get("uploaded_file_id"),
            config=job_data.get("config"),
            metadata=job_data.get("metadata")
        )

        self.db.add(job)
        self.db.commit()
        self.db.refresh(job)

        return job

    def get_by_id(self, job_id: str) -> Optional[Job]:
        """
        Get job by ID.

        Args:
            job_id: Job ID

        Returns:
            Job model or None if not found
        """
        return self.db.query(Job).filter(Job.id == job_id).first()

    def list_all(
        self,
        status: Optional[str] = None,
        limit: int = 50,
        offset: int = 0
    ) -> List[Job]:
        """
        List all jobs with optional filtering.

        Args:
            status: Filter by status
            limit: Maximum number of results
            offset: Number of results to skip

        Returns:
            List of Job models
        """
        query = self.db.query(Job)

        if status:
            query = query.filter(Job.status == status)

        return query.order_by(desc(Job.created_at)).limit(limit).offset(offset).all()

    def update(self, job_id: str, updates: Dict) -> Optional[Job]:
        """
        Update a job.

        Args:
            job_id: Job ID
            updates: Dictionary of fields to update

        Returns:
            Updated Job model or None if not found
        """
        job = self.get_by_id(job_id)
        if not job:
            return None

        # Update fields
        for key, value in updates.items():
            if hasattr(job, key):
                setattr(job, key, value)

        # Always update updated_at
        job.updated_at = datetime.now().isoformat()

        self.db.commit()
        self.db.refresh(job)

        return job

    def delete(self, job_id: str) -> bool:
        """
        Delete a job.

        Args:
            job_id: Job ID

        Returns:
            True if deleted, False if not found
        """
        job = self.get_by_id(job_id)
        if not job:
            return False

        self.db.delete(job)
        self.db.commit()

        return True

    def count_by_status(self, status: Optional[str] = None) -> int:
        """
        Count jobs by status.

        Args:
            status: Status to filter by (None = all)

        Returns:
            Number of jobs
        """
        query = self.db.query(Job)

        if status:
            query = query.filter(Job.status == status)

        return query.count()

    def get_stats(self) -> Dict:
        """
        Get job statistics.

        Returns:
            Dictionary with job counts by status
        """
        return {
            "total": self.count_by_status(),
            "pending": self.count_by_status("pending"),
            "processing": self.count_by_status("processing"),
            "completed": self.count_by_status("completed"),
            "failed": self.count_by_status("failed")
        }
