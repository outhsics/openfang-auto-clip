"""
Health Check Router

Simple health check endpoint.
"""

from fastapi import APIRouter
from typing import Dict

router = APIRouter()


@router.get("/health", response_model=Dict[str, str])
async def health_check() -> Dict[str, str]:
    """
    Health check endpoint.

    Returns the API status and version.
    """
    return {
        "status": "healthy",
        "version": "0.5.0",
        "service": "openfang-api"
    }
