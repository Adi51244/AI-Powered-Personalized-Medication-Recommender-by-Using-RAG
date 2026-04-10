"""
Diagnosis repository for database CRUD operations.
"""

from typing import Optional, List
from sqlalchemy.orm import Session
from datetime import datetime
from app.db.base import Diagnosis
from app.models.schemas import DiagnosisResponse


class DiagnosisRepository:
    """Repository for Diagnosis CRUD operations."""

    @staticmethod
    def create(
        session: Session,
        patient_id: str,
        symptoms: List[dict],
        predictions: List[dict],
        ml_features: Optional[dict] = None,
        rag_evidence: Optional[dict] = None
    ) -> Diagnosis:
        """Create a new diagnosis."""
        db_diagnosis = Diagnosis(
            patient_id=patient_id,
            symptoms=symptoms,
            predictions=predictions,
            ml_features=ml_features,
            rag_evidence=rag_evidence,
        )
        session.add(db_diagnosis)
        session.commit()
        session.refresh(db_diagnosis)
        return db_diagnosis

    @staticmethod
    def get_by_id(session: Session, diagnosis_id: str) -> Optional[Diagnosis]:
        """Get diagnosis by ID."""
        return session.query(Diagnosis).filter(Diagnosis.id == diagnosis_id).first()

    @staticmethod
    def get_by_patient(
        session: Session,
        patient_id: str,
        skip: int = 0,
        limit: int = 100
    ) -> List[Diagnosis]:
        """Get all diagnoses for a patient."""
        return (
            session.query(Diagnosis)
            .filter(Diagnosis.patient_id == patient_id)
            .order_by(Diagnosis.created_at.desc())
            .offset(skip)
            .limit(limit)
            .all()
        )

    @staticmethod
    def list_all(session: Session, skip: int = 0, limit: int = 100) -> List[Diagnosis]:
        """List all diagnoses with pagination."""
        return (
            session.query(Diagnosis)
            .order_by(Diagnosis.created_at.desc())
            .offset(skip)
            .limit(limit)
            .all()
        )

    @staticmethod
    def update(
        session: Session,
        diagnosis_id: str,
        predictions: Optional[List[dict]] = None,
        rag_evidence: Optional[dict] = None
    ) -> Optional[Diagnosis]:
        """Update diagnosis results."""
        db_diagnosis = session.query(Diagnosis).filter(Diagnosis.id == diagnosis_id).first()
        if not db_diagnosis:
            return None

        if predictions is not None:
            db_diagnosis.predictions = predictions
        if rag_evidence is not None:
            db_diagnosis.rag_evidence = rag_evidence

        session.commit()
        session.refresh(db_diagnosis)
        return db_diagnosis

    @staticmethod
    def delete(session: Session, diagnosis_id: str) -> bool:
        """Delete a diagnosis."""
        db_diagnosis = session.query(Diagnosis).filter(Diagnosis.id == diagnosis_id).first()
        if not db_diagnosis:
            return False

        session.delete(db_diagnosis)
        session.commit()
        return True

    @staticmethod
    def count_by_patient(session: Session, patient_id: str) -> int:
        """Count diagnoses for a patient."""
        return session.query(Diagnosis).filter(Diagnosis.patient_id == patient_id).count()

    @staticmethod
    def count_all(session: Session) -> int:
        """Count total diagnoses."""
        return session.query(Diagnosis).count()
