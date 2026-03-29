"""
Database Configuration and Session Management

SQLAlchemy setup for database operations.
"""

from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker, Session
from sqlalchemy.pool import StaticPool
from pathlib import Path
import logging

from ..config import settings
from .models import Base

logger = logging.getLogger(__name__)


# Database directory
DB_DIR = Path.home() / ".openfang" / "data"
DB_DIR.mkdir(parents=True, exist_ok=True)

# Database URL
DATABASE_URL = f"sqlite:///{DB_DIR}/openfang.db"


# Create engine
engine = create_engine(
    DATABASE_URL,
    connect_args={"check_same_thread": False} if "sqlite" in DATABASE_URL else {},
    poolclass=StaticPool if "sqlite" in DATABASE_URL else None,
    echo=settings.DEBUG  # Log SQL queries in debug mode
)


# Create session factory
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)


def init_db():
    """Initialize database, create tables"""
    try:
        logger.info("Initializing database...")
        Base.metadata.create_all(bind=engine)
        logger.info(f"Database initialized: {DATABASE_URL}")
    except Exception as e:
        logger.error(f"Failed to initialize database: {e}", exc_info=True)
        raise


def get_db() -> Session:
    """
    Get database session.

    Yields:
        Database session

    Example:
        >>> db = get_db()
        >>> try:
        ...     # Use db
        ...     pass
        ... finally:
        ...     db.close()
    """
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()


class DatabaseManager:
    """High-level database operations manager"""

    def __init__(self):
        """Initialize database manager"""
        self.engine = engine
        self.SessionLocal = SessionLocal

    def create_session(self) -> Session:
        """Create a new database session"""
        return self.SessionLocal()

    def init_db(self):
        """Initialize database tables"""
        Base.metadata.create_all(bind=self.engine)

    def drop_all(self):
        """Drop all tables (use with caution!)"""
        Base.metadata.drop_all(bind=self.engine)


# Global database manager instance
_db_manager = None


def get_database_manager() -> DatabaseManager:
    """Get the global database manager instance"""
    global _db_manager
    if _db_manager is None:
        _db_manager = DatabaseManager()
        _db_manager.init_db()
    return _db_manager
