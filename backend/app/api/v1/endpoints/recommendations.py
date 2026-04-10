"""
Recommendation CRUD API endpoints.

This module provides endpoints for managing medication recommendations:
- Create recommendations from diagnosis
- Retrieve recommendations
- List diagnosis recommendations
- Approve recommendations
- Update recommendations
- Delete recommendations
"""

import logging
from fastapi import APIRouter, HTTPException, status, Query, Depends
from sqlalchemy.orm import Session

from app.db.session import get_session
from app.db.repositories.recommendation_repository import RecommendationRepository
from app.db.repositories.diagnosis_repository import DiagnosisRepository
from app.models.schemas import (
    RecommendationCreate,
    RecommendationApprove,
    RecommendationListResponse,
)

logger = logging.getLogger(__name__)

router = APIRouter()


@router.post(
    "/recommendations",
    response_model=dict,
    status_code=status.HTTP_201_CREATED,
    summary="Create recommendation",
    description="Create a medication recommendation for a diagnosis"
)
async def create_recommendation(
    recommendation_data: RecommendationCreate,
    session: Session = Depends(get_session)
):
    """
    Create a medication recommendation.

    Args:
        recommendation_data: Recommendation information
        session: Database session

    Returns:
        Recommendation ID and creation timestamp

    Raises:
        HTTPException: If diagnosis not found or creation fails
    """
    try:
        logger.info(f"Creating recommendation for diagnosis: {recommendation_data.diagnosis_id}")

        # Verify diagnosis exists
        diagnosis = DiagnosisRepository.get_by_id(session, recommendation_data.diagnosis_id)
        if not diagnosis:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"Diagnosis {recommendation_data.diagnosis_id} not found"
            )

        # Create recommendation
        recommendation = RecommendationRepository.create(
            session,
            diagnosis_id=recommendation_data.diagnosis_id,
            medications=[m.model_dump() for m in recommendation_data.medications],
            safety_checks=recommendation_data.safety_checks,
            explanations=recommendation_data.explanations
        )

        logger.info(f"✓ Recommendation created: {recommendation.id}")

        return {
            "recommendation_id": recommendation.id,
            "diagnosis_id": recommendation.diagnosis_id,
            "created_at": recommendation.created_at.isoformat(),
            "approved": recommendation.approved
        }

    except HTTPException:
        raise
    except Exception as e:
        session.rollback()
        logger.error(f"Failed to create recommendation: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to create recommendation: {str(e)}"
        )


@router.get(
    "/recommendations/{recommendation_id}",
    response_model=dict,
    summary="Get recommendation",
    description="Retrieve a specific recommendation"
)
async def get_recommendation(
    recommendation_id: str,
    session: Session = Depends(get_session)
):
    """
    Get recommendation by ID.

    Args:
        recommendation_id: Recommendation ID
        session: Database session

    Returns:
        Recommendation record

    Raises:
        HTTPException: If recommendation not found
    """
    try:
        logger.info(f"Retrieving recommendation: {recommendation_id}")

        recommendation = RecommendationRepository.get_by_id(session, recommendation_id)

        if not recommendation:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"Recommendation {recommendation_id} not found"
            )

        return {
            "id": recommendation.id,
            "diagnosis_id": recommendation.diagnosis_id,
            "medications": recommendation.medications,
            "safety_checks": recommendation.safety_checks,
            "explanations": recommendation.explanations,
            "approved": recommendation.approved,
            "approved_by": recommendation.approved_by,
            "created_at": recommendation.created_at.isoformat()
        }

    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Failed to retrieve recommendation: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to retrieve recommendation: {str(e)}"
        )


@router.get(
    "/diagnoses/{diagnosis_id}/recommendations",
    response_model=RecommendationListResponse,
    summary="Get diagnosis recommendations",
    description="Get all recommendations for a specific diagnosis"
)
async def get_diagnosis_recommendations(
    diagnosis_id: str,
    skip: int = Query(0, ge=0, description="Number of records to skip"),
    limit: int = Query(100, ge=1, le=1000, description="Number of records to return"),
    session: Session = Depends(get_session)
):
    """
    Get all recommendations for a diagnosis.

    Args:
        diagnosis_id: Diagnosis ID
        skip: Number of records to skip
        limit: Number of records to return
        session: Database session

    Returns:
        RecommendationListResponse with recommendations

    Raises:
        HTTPException: If diagnosis not found
    """
    try:
        logger.info(f"Retrieving recommendations for diagnosis: {diagnosis_id}")

        # Verify diagnosis exists
        diagnosis = DiagnosisRepository.get_by_id(session, diagnosis_id)
        if not diagnosis:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"Diagnosis {diagnosis_id} not found"
            )

        recommendations = RecommendationRepository.get_by_diagnosis(
            session,
            diagnosis_id=diagnosis_id,
            skip=skip,
            limit=limit
        )
        total = RecommendationRepository.count_by_diagnosis(session, diagnosis_id)

        return RecommendationListResponse(
            total=total,
            items=[
                {
                    "id": r.id,
                    "diagnosis_id": r.diagnosis_id,
                    "medications": r.medications,
                    "safety_checks": r.safety_checks,
                    "approved": r.approved,
                    "created_at": r.created_at.isoformat()
                }
                for r in recommendations
            ]
        )

    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Failed to retrieve recommendations: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to retrieve recommendations: {str(e)}"
        )


@router.get(
    "/recommendations/all",
    response_model=RecommendationListResponse,
    summary="List all recommendations",
    description="Get a paginated list of all recommendations"
)
async def list_all_recommendations(
    skip: int = Query(0, ge=0, description="Number of records to skip"),
    limit: int = Query(100, ge=1, le=1000, description="Number of records to return"),
    session: Session = Depends(get_session)
):
    """
    List all recommendations.

    Args:
        skip: Number of records to skip
        limit: Number of records to return
        session: Database session

    Returns:
        RecommendationListResponse with all recommendations
    """
    try:
        logger.info(f"Listing all recommendations: skip={skip}, limit={limit}")

        recommendations = RecommendationRepository.list_all(session, skip=skip, limit=limit)
        total = RecommendationRepository.count_all(session)

        return RecommendationListResponse(
            total=total,
            items=[
                {
                    "id": r.id,
                    "diagnosis_id": r.diagnosis_id,
                    "medications": r.medications,
                    "approved": r.approved,
                    "created_at": r.created_at.isoformat()
                }
                for r in recommendations
            ]
        )

    except Exception as e:
        logger.error(f"Failed to list recommendations: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to list recommendations: {str(e)}"
        )


@router.post(
    "/recommendations/{recommendation_id}/approve",
    response_model=dict,
    summary="Approve recommendation",
    description="Mark a recommendation as approved by a clinician"
)
async def approve_recommendation(
    recommendation_id: str,
    approval_data: RecommendationApprove,
    session: Session = Depends(get_session)
):
    """
    Approve a recommendation.

    Args:
        recommendation_id: Recommendation ID
        approval_data: Approval information (who approved)
        session: Database session

    Returns:
        Updated recommendation with approval status

    Raises:
        HTTPException: If recommendation not found or approval fails
    """
    try:
        logger.info(f"Approving recommendation: {recommendation_id}")

        recommendation = RecommendationRepository.get_by_id(session, recommendation_id)
        if not recommendation:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"Recommendation {recommendation_id} not found"
            )

        # Approve recommendation
        updated = RecommendationRepository.approve(
            session,
            recommendation_id=recommendation_id,
            approved_by=approval_data.approved_by
        )

        logger.info(f"✓ Recommendation approved: {recommendation_id}")

        return {
            "recommendation_id": updated.id,
            "approved": updated.approved,
            "approved_by": updated.approved_by
        }

    except HTTPException:
        raise
    except Exception as e:
        session.rollback()
        logger.error(f"Failed to approve recommendation: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to approve recommendation: {str(e)}"
        )


@router.put(
    "/recommendations/{recommendation_id}",
    response_model=dict,
    summary="Update recommendation",
    description="Update a recommendation"
)
async def update_recommendation(
    recommendation_id: str,
    recommendation_data: RecommendationCreate,
    session: Session = Depends(get_session)
):
    """
    Update a recommendation.

    Args:
        recommendation_id: Recommendation ID
        recommendation_data: Updated recommendation data
        session: Database session

    Returns:
        Updated recommendation

    Raises:
        HTTPException: If recommendation not found or update fails
    """
    try:
        logger.info(f"Updating recommendation: {recommendation_id}")

        recommendation = RecommendationRepository.get_by_id(session, recommendation_id)
        if not recommendation:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"Recommendation {recommendation_id} not found"
            )

        # Update recommendation
        updated = RecommendationRepository.update(
            session,
            recommendation_id=recommendation_id,
            medications=[m.model_dump() for m in recommendation_data.medications],
            safety_checks=recommendation_data.safety_checks,
            explanations=recommendation_data.explanations
        )

        logger.info(f"✓ Recommendation updated: {recommendation_id}")

        return {
            "recommendation_id": updated.id,
            "medications": updated.medications,
            "safety_checks": updated.safety_checks
        }

    except HTTPException:
        raise
    except Exception as e:
        session.rollback()
        logger.error(f"Failed to update recommendation: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to update recommendation: {str(e)}"
        )


@router.delete(
    "/recommendations/{recommendation_id}",
    status_code=status.HTTP_204_NO_CONTENT,
    summary="Delete recommendation",
    description="Delete a recommendation record"
)
async def delete_recommendation(
    recommendation_id: str,
    session: Session = Depends(get_session)
):
    """
    Delete a recommendation.

    Args:
        recommendation_id: Recommendation ID
        session: Database session

    Raises:
        HTTPException: If recommendation not found or deletion fails
    """
    try:
        logger.info(f"Deleting recommendation: {recommendation_id}")

        recommendation = RecommendationRepository.get_by_id(session, recommendation_id)
        if not recommendation:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"Recommendation {recommendation_id} not found"
            )

        success = RecommendationRepository.delete(session, recommendation_id)

        if not success:
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail="Failed to delete recommendation"
            )

        logger.info(f"✓ Recommendation deleted: {recommendation_id}")

    except HTTPException:
        raise
    except Exception as e:
        session.rollback()
        logger.error(f"Failed to delete recommendation: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to delete recommendation: {str(e)}"
        )
