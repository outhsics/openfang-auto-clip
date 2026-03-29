"""
OpenFang Auto Clip - REST API Server

FastAPI-based REST API for OpenFang Auto Clip operations.
"""

from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
from contextlib import asynccontextmanager
import logging
from typing import Dict

from .routers import process, jobs, validate, health
from .config import settings


# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)


@asynccontextmanager
async def lifespan(app: FastAPI):
    """Manage application lifespan"""
    logger.info("🚀 OpenFang API Server starting...")
    yield
    logger.info("👋 OpenFang API Server shutting down...")


# Create FastAPI app
app = FastAPI(
    title="OpenFang Auto Clip API",
    description="REST API for automated video short creation and script generation",
    version="0.5.0",
    docs_url="/docs",
    redoc_url="/redoc",
    lifespan=lifespan
)


# Configure CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.CORS_ORIGINS,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


# Include routers
app.include_router(health.router, prefix="/api/v1", tags=["Health"])
app.include_router(process.router, prefix="/api/v1", tags=["Process"])
app.include_router(jobs.router, prefix="/api/v1/jobs", tags=["Jobs"])
app.include_router(validate.router, prefix="/api/v1", tags=["Validate"])


# Root endpoint
@app.get("/", tags=["Root"])
async def root() -> Dict[str, str]:
    """Root endpoint"""
    return {
        "name": "OpenFang Auto Clip API",
        "version": "0.5.0",
        "status": "running",
        "docs": "/docs",
        "health": "/api/v1/health"
    }


# Global exception handler
@app.exception_handler(Exception)
async def global_exception_handler(request, exc):
    """Handle all unhandled exceptions"""
    logger.error(f"Unhandled exception: {exc}", exc_info=True)
    return JSONResponse(
        status_code=500,
        content={
            "error": "Internal server error",
            "message": str(exc) if settings.DEBUG else "An error occurred"
        }
    )


# Startup event
@app.on_event("startup")
async def startup_event():
    """Log startup info"""
    logger.info(f"✅ API Server ready at http://{settings.API_HOST}:{settings.API_PORT}")
    logger.info(f"📚 API Documentation: http://{settings.API_HOST}:{settings.API_PORT}/docs")


if __name__ == "__main__":
    import uvicorn
    uvicorn.run(
        "main:app",
        host=settings.API_HOST,
        port=settings.API_PORT,
        reload=settings.DEBUG,
        log_level="info"
    )
