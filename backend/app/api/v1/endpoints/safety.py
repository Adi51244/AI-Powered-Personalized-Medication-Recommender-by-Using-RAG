"""Safety validation endpoints."""

from __future__ import annotations

import logging

from fastapi import APIRouter, HTTPException, status

from app.config import settings
from app.core.safety import SafetyValidator
from app.models.schemas import (
    SafetyValidationDetailedResponse,
    SafetyValidationInput,
)

logger = logging.getLogger(__name__)

router = APIRouter()


@router.post(
    "/safety/validate",
    response_model=SafetyValidationDetailedResponse,
    status_code=status.HTTP_200_OK,
    summary="Validate medication recommendations for safety",
)
async def validate_safety(payload: SafetyValidationInput):
    """Run Phase 5 safety checks for a patient + recommendation set."""
    if not settings.safety_enabled:
        raise HTTPException(
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
            detail="Safety validation is disabled by configuration.",
        )

    try:
        validator = SafetyValidator.get_instance()
        recommendations, validation = validator.validate_recommendations(
            patient_input=payload.patient,
            recommendations=payload.recommendations,
        )
        return SafetyValidationDetailedResponse(validation=validation, recommendations=recommendations)
    except Exception as exc:
        logger.exception("Safety validation endpoint failed")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Safety validation failed: {exc}",
        )
