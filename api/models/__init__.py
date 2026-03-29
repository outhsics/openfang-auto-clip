"""
Database Models

SQLAlchemy models for job persistence.
"""

from sqlalchemy import Column, String, Integer, Float, DateTime, Text, JSON
from sqlalchemy.ext.declarative import declarative_base
from datetime import datetime

Base = declarative_base()


class Job(Base):
    """Job model for storing processing jobs"""

    __tablename__ = "jobs"

    id = Column(String, primary_key=True, index=True)
    status = Column(String, nullable=False, index=True)  # pending, processing, completed, failed
    level = Column(Integer, nullable=False)
    progress = Column(Float, default=0.0)
    created_at = Column(String, nullable=False)
    updated_at = Column(String, nullable=False)
    result = Column(JSON, nullable=True)
    error = Column(Text, nullable=True)

    # Input parameters
    transcript_path = Column(String, nullable=True)
    video_url = Column(String, nullable=True)
    uploaded_file_id = Column(String, nullable=True)
    config = Column(JSON, nullable=True)

    # Additional metadata
    metadata = Column(JSON, nullable=True)

    def to_dict(self) -> dict:
        """Convert model to dictionary"""
        return {
            "id": self.id,
            "status": self.status,
            "level": self.level,
            "progress": self.progress,
            "created_at": self.created_at,
            "updated_at": self.updated_at,
            "result": self.result,
            "error": self.error
        }


class UploadedFile(Base):
    """Uploaded file model"""

    __tablename__ = "uploaded_files"

    file_id = Column(String, primary_key=True, index=True)
    filename = Column(String, nullable=False)
    path = Column(String, nullable=False)
    size = Column(Integer, nullable=False)
    uploaded_at = Column(String, nullable=False)
    metadata = Column(JSON, nullable=True)

    def to_dict(self) -> dict:
        """Convert model to dictionary"""
        return {
            "file_id": self.file_id,
            "filename": self.filename,
            "path": self.path,
            "size": self.size,
            "uploaded_at": self.uploaded_at
        }
