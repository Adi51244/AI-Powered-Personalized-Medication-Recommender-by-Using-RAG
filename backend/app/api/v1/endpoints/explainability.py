"""Explainability endpoints for Phase 6."""

from __future__ import annotations

import asyncio
import logging

from fastapi import APIRouter, HTTPException, status

from app.core.explainability import ExplainabilityService
from app.models.schemas import ExplanationRequest, ExplanationResponse

logger = logging.getLogger(__name__)

router = APIRouter()


@router.post(
    "/explanations",
    response_model=ExplanationResponse,
    status_code=status.HTTP_200_OK,
    summary="Generate model explanation for a patient diagnosis",
)
async def create_explanation(payload: ExplanationRequest):
    """Generate local explanation using SHAP/LIME with fallback mode."""
    try:
        service = ExplainabilityService.get_instance()
        
        # Wrap with 90s timeout to prevent indefinite hangs
        # SHAP/LIME computation can take 30-60s for complex models
        logger.info(f"Starting explanation generation (timeout: 90s, top_k={payload.top_k_features})")
        
        try:
            result = await asyncio.wait_for(
                asyncio.to_thread(  # Run CPU-bound SHAP/LIME in thread pool
                    service.explain_patient,
                    patient_input=payload.patient,
                    top_k_features=payload.top_k_features,
                ),
                timeout=90.0
            )
            logger.info(f"✓ Explanation generated using method: {result.method}")
            return result
            
        except asyncio.TimeoutError:
            logger.warning(
                "⚠️  Explanation computation timed out after 90s, using fast fallback"
            )
            # Use fast fallback method (feature importance only, no SHAP/LIME)
            return service.explain_patient_fallback(
                patient_input=payload.patient,
                top_k_features=payload.top_k_features,
            )
            
    except Exception as exc:
        logger.exception("Explainability generation failed")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Explainability generation failed: {exc}",
        )
