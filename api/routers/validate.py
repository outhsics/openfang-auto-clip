"""
Validation Router

Level 2 package validation endpoints.
"""

from fastapi import APIRouter, HTTPException, status
from pydantic import BaseModel, Field
from typing import Dict, List, Optional
import logging

logger = logging.getLogger(__name__)

router = APIRouter()


class ValidationResult(BaseModel):
    """Validation result"""
    overall_score: float = Field(..., ge=0, le=10)
    grade: str = Field(..., pattern="^[ABCDF]$")
    scores: Dict[str, float]
    copyright_risk: Dict[str, float]
    production_ready: bool
    issues: List[str]
    recommendations: List[str]


class ValidateRequest(BaseModel):
    """Request to validate a package"""
    package_path: str = Field(..., description="Path to Level 2 package JSON")
    original_transcript: Optional[str] = Field(None, description="Original transcript text")

    class Config:
        json_schema_extra = {
            "example": {
                "package_path": "/output/level2_package.json",
                "original_transcript": "Original transcript text..."
            }
        }


@router.post("/validate", response_model=ValidationResult)
async def validate_package(request: ValidateRequest) -> ValidationResult:
    """
    Validate a Level 2 package.

    Performs multi-dimensional quality analysis:
    - Coherence (script structure and flow)
    - Actionability (visual direction clarity)
    - Originality (creative content)
    - Value Retention (information preservation)
    - Copyright Risk (similarity analysis)

    Args:
        request: Validation request with package path

    Returns:
        Validation results with scores and recommendations
    """
    try:
        # Import processing service
        from ..services import get_processing_service

        # Get processing service
        service = get_processing_service()

        # Validate package
        result = service.validate_package(
            package_path=request.package_path,
            original_transcript=request.original_transcript or ""
        )

        # Extract results
        scores = result.get("scores", {})
        overall = result.get("overall", 0)
        grade = result.get("grade", "F")
        copyright_result = result.get("copyright_risk", {})

        # Determine production readiness
        production_ready = grade in ["A", "B"]

        # Generate issues and recommendations
        issues = []
        recommendations = []

        for dimension, score in scores.items():
            if score < 7:
                issues.append(f"Low {dimension} score ({score}/10)")
                recommendations.append(f"Improve {dimension} for better quality")

        if copyright_result.get("risk_level") == "High":
            issues.append("High copyright risk detected")
            recommendations.append("Reduce similarity to original content")

        logger.info(f"Validation completed: {overall}/10 ({grade})")

        return ValidationResult(
            overall_score=overall,
            grade=grade,
            scores=scores,
            copyright_risk=copyright_result,
            production_ready=production_ready,
            issues=issues,
            recommendations=recommendations
        )

    except ValueError as e:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=str(e)
        )
    except Exception as e:
        logger.error(f"Validation failed: {e}", exc_info=True)
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Validation failed: {str(e)}"
        )
