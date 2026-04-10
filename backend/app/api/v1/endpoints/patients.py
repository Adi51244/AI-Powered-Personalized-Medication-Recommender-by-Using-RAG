"""
Patient CRUD API endpoints.

This module provides endpoints for managing patient records:
- Create new patients
- Retrieve patient information
- List all patients
- Update patient records
- Delete patient records
"""

import logging
from fastapi import APIRouter, HTTPException, status, Query, Depends
from sqlalchemy.orm import Session

from app.db.session import get_session
from app.db.repositories.patient_repository import PatientRepository
from app.models.schemas import (
    PatientCreate,
    PatientUpdate,
    PatientResponse,
    PatientListResponse,
)

logger = logging.getLogger(__name__)

router = APIRouter()


@router.post(
    "/patients",
    response_model=PatientResponse,
    status_code=status.HTTP_201_CREATED,
    summary="Create a new patient",
    description="Create a new patient record with medical information"
)
async def create_patient(
    patient_data: PatientCreate,
    session: Session = Depends(get_session)
):
    """
    Create a new patient.

    Args:
        patient_data: Patient information
        session: Database session

    Returns:
        PatientResponse with created patient ID

    Raises:
        HTTPException: If patient creation fails
    """
    try:
        logger.info(f"Creating patient: age={patient_data.age}, gender={patient_data.gender}")

        # Convert to PatientInput format for repository
        patient = PatientRepository.create(session, patient_data)

        logger.info(f"✓ Patient created: {patient.id}")

        return PatientResponse.model_validate(patient)

    except Exception as e:
        logger.error(f"Failed to create patient: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to create patient: {str(e)}"
        )


@router.get(
    "/patients/{patient_id}",
    response_model=PatientResponse,
    summary="Get patient by ID",
    description="Retrieve a specific patient record by ID"
)
async def get_patient(
    patient_id: str,
    session: Session = Depends(get_session)
):
    """
    Get patient by ID.

    Args:
        patient_id: Patient ID
        session: Database session

    Returns:
        PatientResponse

    Raises:
        HTTPException: If patient not found
    """
    try:
        logger.info(f"Retrieving patient: {patient_id}")

        patient = PatientRepository.get_by_id(session, patient_id)

        if not patient:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"Patient {patient_id} not found"
            )

        return PatientResponse.model_validate(patient)

    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Failed to retrieve patient: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to retrieve patient: {str(e)}"
        )


@router.get(
    "/patients",
    response_model=PatientListResponse,
    summary="List all patients",
    description="Get a paginated list of all patients"
)
async def list_patients(
    skip: int = Query(0, ge=0, description="Number of records to skip"),
    limit: int = Query(100, ge=1, le=1000, description="Number of records to return"),
    session: Session = Depends(get_session)
):
    """
    List all patients with pagination.

    Args:
        skip: Number of records to skip
        limit: Number of records to return
        session: Database session

    Returns:
        PatientListResponse with total count and patient list
    """
    try:
        logger.info(f"Listing patients: skip={skip}, limit={limit}")

        patients = PatientRepository.list_all(session, skip=skip, limit=limit)
        total = PatientRepository.count(session)

        return PatientListResponse(
            total=total,
            items=[PatientResponse.model_validate(p) for p in patients]
        )

    except Exception as e:
        logger.error(f"Failed to list patients: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to list patients: {str(e)}"
        )


@router.put(
    "/patients/{patient_id}",
    response_model=PatientResponse,
    summary="Update patient",
    description="Update a patient record"
)
async def update_patient(
    patient_id: str,
    patient_data: PatientUpdate,
    session: Session = Depends(get_session)
):
    """
    Update an existing patient.

    Args:
        patient_id: Patient ID
        patient_data: Updated patient information
        session: Database session

    Returns:
        PatientResponse with updated data

    Raises:
        HTTPException: If patient not found or update fails
    """
    try:
        logger.info(f"Updating patient: {patient_id}")

        # Check if patient exists
        patient = PatientRepository.get_by_id(session, patient_id)
        if not patient:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"Patient {patient_id} not found"
            )

        # Apply only provided updates
        if patient_data.age is not None:
            patient.age = patient_data.age
        if patient_data.gender is not None:
            patient.gender = patient_data.gender
        if patient_data.weight_kg is not None:
            patient.weight_kg = patient_data.weight_kg
        if patient_data.height_cm is not None:
            patient.height_cm = patient_data.height_cm
        if patient_data.allergies is not None:
            patient.allergies = patient_data.allergies
        if patient_data.chronic_conditions is not None:
            patient.chronic_conditions = patient_data.chronic_conditions
        if patient_data.current_medications is not None:
            patient.current_medications = patient_data.current_medications

        session.commit()
        session.refresh(patient)

        logger.info(f"✓ Patient updated: {patient_id}")

        return PatientResponse.model_validate(patient)

    except HTTPException:
        raise
    except Exception as e:
        session.rollback()
        logger.error(f"Failed to update patient: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to update patient: {str(e)}"
        )


@router.delete(
    "/patients/{patient_id}",
    status_code=status.HTTP_204_NO_CONTENT,
    summary="Delete patient",
    description="Delete a patient record"
)
async def delete_patient(
    patient_id: str,
    session: Session = Depends(get_session)
):
    """
    Delete a patient.

    Args:
        patient_id: Patient ID
        session: Database session

    Raises:
        HTTPException: If patient not found or deletion fails
    """
    try:
        logger.info(f"Deleting patient: {patient_id}")

        patient = PatientRepository.get_by_id(session, patient_id)
        if not patient:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"Patient {patient_id} not found"
            )

        success = PatientRepository.delete(session, patient_id)

        if not success:
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail="Failed to delete patient"
            )

        logger.info(f"✓ Patient deleted: {patient_id}")

    except HTTPException:
        raise
    except Exception as e:
        session.rollback()
        logger.error(f"Failed to delete patient: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to delete patient: {str(e)}"
        )
