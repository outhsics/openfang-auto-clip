"""
API Configuration

Settings and configuration for the API server.
"""

from pydantic_settings import BaseSettings
from typing import List
import os
from pathlib import Path


class Settings(BaseSettings):
    """API Settings"""

    # API Server
    API_HOST: str = "0.0.0.0"
    API_PORT: int = 8000
    DEBUG: bool = True

    # CORS
    CORS_ORIGINS: List[str] = [
        "http://localhost:5173",  # Vite dev server
        "http://localhost:3000",  # Alternative dev server
        "http://localhost:8080",  # Production build
    ]

    # Processing
    MAX_UPLOAD_SIZE: int = 100 * 1024 * 1024  # 100MB
    ALLOWED_EXTENSIONS: List[str] = [".srt", ".vtt", ".txt"]
    OUTPUT_DIR: Path = Path.home() / ".openfang" / "output"

    # Jobs
    MAX_CONCURRENT_JOBS: int = 3
    JOB_TIMEOUT: int = 3600  # 1 hour

    # OpenFang
    OPENFANG_API_KEY: str = ""
    OPENFANG_API_URL: str = "https://api.openfang.com/v1"

    # Database (for job tracking - optional for now)
    DATABASE_URL: str = "sqlite:///./openfang.db"

    class Config:
        env_file = ".env"
        case_sensitive = True


# Create settings instance
settings = Settings()


# Create output directory
settings.OUTPUT_DIR.mkdir(parents=True, exist_ok=True)
