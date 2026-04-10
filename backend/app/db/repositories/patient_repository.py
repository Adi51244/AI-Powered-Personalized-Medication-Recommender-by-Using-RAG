"""
Patient repository for database CRUD operations.
"""

from typing import Optional, List
from sqlalchemy.orm import Session
from app.db.base import Patient
from app.models.schemas import PatientInput, PatientResponse


class PatientRepository:
    """Repository for Patient CRUD operations."""

    @staticmethod
    def create(session: Session, patient_input: PatientInput) -> Patient:
        """Create a new patient."""
        db_patient = Patient(
            age=patient_input.age,
            gender=patient_input.gender,
            weight_kg=patient_input.weight_kg,
            height_cm=patient_input.height_cm,
            allergies=patient_input.allergies,
            chronic_conditions=patient_input.chronic_conditions,
            current_medications=patient_input.current_medications,
        )
        session.add(db_patient)
        session.commit()
        session.refresh(db_patient)
        return db_patient

    @staticmethod
    def get_by_id(session: Session, patient_id: str) -> Optional[Patient]:
        """Get patient by ID."""
        return session.query(Patient).filter(Patient.id == patient_id).first()

    @staticmethod
    def list_all(session: Session, skip: int = 0, limit: int = 100) -> List[Patient]:
        """List all patients with pagination."""
        return session.query(Patient).offset(skip).limit(limit).all()

    @staticmethod
    def update(
        session: Session,
        patient_id: str,
        patient_input: PatientInput
    ) -> Optional[Patient]:
        """Update an existing patient."""
        db_patient = session.query(Patient).filter(Patient.id == patient_id).first()
        if not db_patient:
            return None

        db_patient.age = patient_input.age
        db_patient.gender = patient_input.gender
        db_patient.weight_kg = patient_input.weight_kg
        db_patient.height_cm = patient_input.height_cm
        db_patient.allergies = patient_input.allergies
        db_patient.chronic_conditions = patient_input.chronic_conditions
        db_patient.current_medications = patient_input.current_medications

        session.commit()
        session.refresh(db_patient)
        return db_patient

    @staticmethod
    def delete(session: Session, patient_id: str) -> bool:
        """Delete a patient."""
        db_patient = session.query(Patient).filter(Patient.id == patient_id).first()
        if not db_patient:
            return False

        session.delete(db_patient)
        session.commit()
        return True

    @staticmethod
    def count(session: Session) -> int:
        """Count total patients."""
        return session.query(Patient).count()
