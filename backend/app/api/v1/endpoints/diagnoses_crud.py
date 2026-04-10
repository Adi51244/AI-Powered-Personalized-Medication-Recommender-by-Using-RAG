"""
Diagnosis CRUD API endpoints.

This module provides endpoints for managing diagnosis records:
- Create diagnosis from RAG/ML pipeline
- Retrieve diagnosis results
- List patient diagnoses
- Update diagnosis results
- Delete diagnosis records
"""

import logging
from fastapi import APIRouter, HTTPException, status, Query, Depends
from sqlalchemy.orm import Session

from app.db.session import get_session
from app.db.repositories.diagnosis_repository import DiagnosisRepository
from app.db.repositories.patient_repository import PatientRepository
from app.models.schemas import (
    DiagnosisCreate,
    DiagnosisResponse,
    DiagnosisListResponse,
)

logger = logging.getLogger(__name__)

router = APIRouter()


@router.post(
    "/diagnoses/database",
    response_model=dict,
    status_code=status.HTTP_201_CREATED,
    summary="Save diagnosis to database",
    description="Save a diagnosis result to the database for record keeping"
)
async def save_diagnosis_to_db(
    diagnosis_data: DiagnosisCreate,
    session: Session = Depends(get_session)
):
    """
    Save diagnosis to database.

    Args:
        diagnosis_data: Diagnosis information from ML/RAG pipeline
        session: Database session

    Returns:
        Diagnosis record ID and creation timestamp

    Raises:
        HTTPException: If patient not found or save fails
    """
    try:
        logger.info(f"Saving diagnosis for patient: {diagnosis_data.patient_id}")

        # Verify patient exists
        patient = PatientRepository.get_by_id(session, diagnosis_data.patient_id)
        if not patient:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"Patient {diagnosis_data.patient_id} not found"
            )

        # Create diagnosis
        diagnosis = DiagnosisRepository.create(
            session,
            patient_id=diagnosis_data.patient_id,
            symptoms=diagnosis_data.symptoms,
            predictions=diagnosis_data.predictions,
            ml_features=diagnosis_data.ml_features,
            rag_evidence=diagnosis_data.rag_evidence
        )

        logger.info(f"✓ Diagnosis saved: {diagnosis.id}")

        return {
            "diagnosis_id": diagnosis.id,
            "patient_id": diagnosis.patient_id,
            "created_at": diagnosis.created_at.isoformat()
        }

    except HTTPException:
        raise
    except Exception as e:
        session.rollback()
        logger.error(f"Failed to save diagnosis: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to save diagnosis: {str(e)}"
        )


@router.get(
    "/diagnoses/record/{diagnosis_id}",
    response_model=dict,
    summary="Get diagnosis record",
    description="Retrieve a specific diagnosis record from database"
)
async def get_diagnosis_record(
    diagnosis_id: str,
    session: Session = Depends(get_session)
):
    """
    Get diagnosis record by ID.

    Args:
        diagnosis_id: Diagnosis ID
        session: Database session

    Returns:
        Diagnosis record

    Raises:
        HTTPException: If diagnosis not found
    """
    try:
        logger.info(f"Retrieving diagnosis: {diagnosis_id}")

        diagnosis = DiagnosisRepository.get_by_id(session, diagnosis_id)

        if not diagnosis:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"Diagnosis {diagnosis_id} not found"
            )

        return {
            "id": diagnosis.id,
            "patient_id": diagnosis.patient_id,
            "symptoms": diagnosis.symptoms,
            "predictions": diagnosis.predictions,
            "ml_features": diagnosis.ml_features,
            "rag_evidence": diagnosis.rag_evidence,
            "created_at": diagnosis.created_at.isoformat()
        }

    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Failed to retrieve diagnosis: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to retrieve diagnosis: {str(e)}"
        )


@router.get(
    "/patients/{patient_id}/diagnoses",
    response_model=DiagnosisListResponse,
    summary="Get patient diagnoses",
    description="Get all diagnoses for a specific patient"
)
async def get_patient_diagnoses(
    patient_id: str,
    skip: int = Query(0, ge=0, description="Number of records to skip"),
    limit: int = Query(100, ge=1, le=1000, description="Number of records to return"),
    session: Session = Depends(get_session)
):
    """
    Get all diagnoses for a patient.

    Args:
        patient_id: Patient ID
        skip: Number of records to skip
        limit: Number of records to return
        session: Database session

    Returns:
        DiagnosisListResponse with diagnoses

    Raises:
        HTTPException: If patient not found
    """
    try:
        logger.info(f"Retrieving diagnoses for patient: {patient_id}")

        # Verify patient exists
        patient = PatientRepository.get_by_id(session, patient_id)
        if not patient:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"Patient {patient_id} not found"
            )

        diagnoses = DiagnosisRepository.get_by_patient(
            session,
            patient_id=patient_id,
            skip=skip,
            limit=limit
        )
        total = DiagnosisRepository.count_by_patient(session, patient_id)

        return DiagnosisListResponse(
            total=total,
            items=[
                {
                    "id": d.id,
                    "patient_id": d.patient_id,
                    "symptoms": d.symptoms,
                    "predictions": d.predictions,
                    "created_at": d.created_at.isoformat()
                }
                for d in diagnoses
            ]
        )

    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Failed to retrieve patient diagnoses: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to retrieve diagnoses: {str(e)}"
        )


@router.get(
    "/diagnoses/all",
    response_model=DiagnosisListResponse,
    summary="List all diagnoses",
    description="Get a paginated list of all diagnosis records"
)
async def list_all_diagnoses(
    skip: int = Query(0, ge=0, description="Number of records to skip"),
    limit: int = Query(100, ge=1, le=1000, description="Number of records to return"),
    session: Session = Depends(get_session)
):
    """
    List all diagnoses.

    Args:
        skip: Number of records to skip
        limit: Number of records to return
        session: Database session

    Returns:
        DiagnosisListResponse with all diagnoses
    """
    try:
        logger.info(f"Listing all diagnoses: skip={skip}, limit={limit}")

        diagnoses = DiagnosisRepository.list_all(session, skip=skip, limit=limit)
        total = DiagnosisRepository.count_all(session)

        return DiagnosisListResponse(
            total=total,
            items=[
                {
                    "id": d.id,
                    "patient_id": d.patient_id,
                    "symptoms": d.symptoms,
                    "predictions": d.predictions,
                    "created_at": d.created_at.isoformat()
                }
                for d in diagnoses
            ]
        )

    except Exception as e:
        logger.error(f"Failed to list diagnoses: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to list diagnoses: {str(e)}"
        )


@router.delete(
    "/diagnoses/{diagnosis_id}",
    status_code=status.HTTP_204_NO_CONTENT,
    summary="Delete diagnosis",
    description="Delete a diagnosis record"
)
async def delete_diagnosis(
    diagnosis_id: str,
    session: Session = Depends(get_session)
):
    """
    Delete a diagnosis.

    Args:
        diagnosis_id: Diagnosis ID
        session: Database session

    Raises:
        HTTPException: If diagnosis not found or deletion fails
    """
    try:
        logger.info(f"Deleting diagnosis: {diagnosis_id}")

        diagnosis = DiagnosisRepository.get_by_id(session, diagnosis_id)
        if not diagnosis:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"Diagnosis {diagnosis_id} not found"
            )

        success = DiagnosisRepository.delete(session, diagnosis_id)

        if not success:
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail="Failed to delete diagnosis"
            )

        logger.info(f"✓ Diagnosis deleted: {diagnosis_id}")

    except HTTPException:
        raise
    except Exception as e:
        session.rollback()
        logger.error(f"Failed to delete diagnosis: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to delete diagnosis: {str(e)}"
        )
