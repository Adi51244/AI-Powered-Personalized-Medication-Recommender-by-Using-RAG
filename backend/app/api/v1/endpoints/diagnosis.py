"""
Diagnosis API endpoints.

This module provides API endpoints for creating diagnoses and
medication recommendations using the RAG pipeline.
"""

import logging
from fastapi import APIRouter, HTTPException, status

from app.core.rag.exceptions import RAGError, VectorStoreError, LLMError
from app.models.schemas import PatientInput, DiagnosisResponse

logger = logging.getLogger(__name__)

router = APIRouter()
_DIAGNOSIS_CACHE: dict[str, DiagnosisResponse] = {}


def get_cached_diagnosis(diagnosis_id: str) -> DiagnosisResponse | None:
    return _DIAGNOSIS_CACHE.get(diagnosis_id)


def get_pipeline():
    """
    Get the global RAG pipeline instance.

    The pipeline is initialized at app startup via the lifespan context manager.
    This function imports it from main to avoid circular imports.
    """
    from app.main import get_global_pipeline
    return get_global_pipeline()


@router.post(
    "/diagnoses",
    response_model=DiagnosisResponse,
    status_code=status.HTTP_200_OK,
    summary="Create diagnosis with medication recommendations",
    description="""
    Analyze patient symptoms and medical history to provide:
    - Disease predictions based on similar clinical cases
    - Evidence-based medication recommendations
    - Citations from medical literature (MIMIC, DrugBank, WHO)

    The system uses RAG (Retrieval-Augmented Generation) to retrieve
    relevant medical evidence and generate recommendations.
    """
)
async def create_diagnosis(patient_input: PatientInput):
    """
    Create diagnosis and medication recommendations.

    Args:
        patient_input: Patient information including symptoms, history, allergies

    Returns:
        DiagnosisResponse with predictions, recommendations, and evidence

    Raises:
        HTTPException: If diagnosis fails
    """
    try:
        logger.info("=== DIAGNOSIS REQUEST START ===")
        logger.info(f"Processing diagnosis request: age={patient_input.age}, symptoms={len(patient_input.symptoms)}")

        # Get pipeline
        pipeline = get_pipeline()

        # Run RAG pipeline
        response = await pipeline.run(patient_input)
        _DIAGNOSIS_CACHE[response.diagnosis_id] = response

        logger.info(f"✓ Diagnosis completed: {response.diagnosis_id}")
        logger.info("=== DIAGNOSIS REQUEST END ===")

        return response

    except VectorStoreError as e:
        logger.error(f"Vector store error: {e}")
        raise HTTPException(
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
            detail="Vector store is unavailable. Please try again later."
        )

    except LLMError as e:
        logger.error(f"LLM error: {e}")
        raise HTTPException(
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
            detail=f"AI service is unavailable: {str(e)}"
        )

    except RAGError as e:
        logger.error(f"RAG pipeline error: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Diagnosis failed: {str(e)}"
        )

    except Exception as e:
        logger.exception("Unexpected error in diagnosis endpoint")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="An unexpected error occurred. Please contact support."
        )


@router.get(
    "/diagnoses/{diagnosis_id}",
    response_model=DiagnosisResponse,
    summary="Get diagnosis by ID",
    description="Retrieve a previously created diagnosis by its ID."
)
async def get_diagnosis(diagnosis_id: str):
    """
    Get diagnosis by ID.

    This is a placeholder endpoint. In production, this would retrieve
    the diagnosis from the database.

    Args:
        diagnosis_id: Diagnosis ID

    Returns:
        DiagnosisResponse

    Raises:
        HTTPException: If diagnosis not found
    """
    cached = get_cached_diagnosis(diagnosis_id)
    if cached:
        return cached

    raise HTTPException(
        status_code=status.HTTP_404_NOT_FOUND,
        detail="Diagnosis not found. Please create a new diagnosis first."
    )
