"""
Recommendation repository for database CRUD operations.
"""

from typing import Optional, List
from sqlalchemy.orm import Session
from app.db.base import Recommendation


class RecommendationRepository:
    """Repository for Recommendation CRUD operations."""

    @staticmethod
    def create(
        session: Session,
        diagnosis_id: str,
        medications: List[dict],
        safety_checks: dict,
        explanations: Optional[dict] = None
    ) -> Recommendation:
        """Create a new recommendation."""
        db_recommendation = Recommendation(
            diagnosis_id=diagnosis_id,
            medications=medications,
            safety_checks=safety_checks,
            explanations=explanations,
        )
        session.add(db_recommendation)
        session.commit()
        session.refresh(db_recommendation)
        return db_recommendation

    @staticmethod
    def get_by_id(session: Session, recommendation_id: str) -> Optional[Recommendation]:
        """Get recommendation by ID."""
        return session.query(Recommendation).filter(Recommendation.id == recommendation_id).first()

    @staticmethod
    def get_by_diagnosis(
        session: Session,
        diagnosis_id: str,
        skip: int = 0,
        limit: int = 100
    ) -> List[Recommendation]:
        """Get all recommendations for a diagnosis."""
        return (
            session.query(Recommendation)
            .filter(Recommendation.diagnosis_id == diagnosis_id)
            .order_by(Recommendation.created_at.desc())
            .offset(skip)
            .limit(limit)
            .all()
        )

    @staticmethod
    def list_all(session: Session, skip: int = 0, limit: int = 100) -> List[Recommendation]:
        """List all recommendations with pagination."""
        return (
            session.query(Recommendation)
            .order_by(Recommendation.created_at.desc())
            .offset(skip)
            .limit(limit)
            .all()
        )

    @staticmethod
    def approve(
        session: Session,
        recommendation_id: str,
        approved_by: str
    ) -> Optional[Recommendation]:
        """Approve a recommendation."""
        db_recommendation = session.query(Recommendation).filter(
            Recommendation.id == recommendation_id
        ).first()
        if not db_recommendation:
            return None

        db_recommendation.approved = True
        db_recommendation.approved_by = approved_by
        session.commit()
        session.refresh(db_recommendation)
        return db_recommendation

    @staticmethod
    def update(
        session: Session,
        recommendation_id: str,
        medications: Optional[List[dict]] = None,
        safety_checks: Optional[dict] = None,
        explanations: Optional[dict] = None
    ) -> Optional[Recommendation]:
        """Update a recommendation."""
        db_recommendation = session.query(Recommendation).filter(
            Recommendation.id == recommendation_id
        ).first()
        if not db_recommendation:
            return None

        if medications is not None:
            db_recommendation.medications = medications
        if safety_checks is not None:
            db_recommendation.safety_checks = safety_checks
        if explanations is not None:
            db_recommendation.explanations = explanations

        session.commit()
        session.refresh(db_recommendation)
        return db_recommendation

    @staticmethod
    def delete(session: Session, recommendation_id: str) -> bool:
        """Delete a recommendation."""
        db_recommendation = session.query(Recommendation).filter(
            Recommendation.id == recommendation_id
        ).first()
        if not db_recommendation:
            return False

        session.delete(db_recommendation)
        session.commit()
        return True

    @staticmethod
    def count_by_diagnosis(session: Session, diagnosis_id: str) -> int:
        """Count recommendations for a diagnosis."""
        return session.query(Recommendation).filter(
            Recommendation.diagnosis_id == diagnosis_id
        ).count()

    @staticmethod
    def count_all(session: Session) -> int:
        """Count total recommendations."""
        return session.query(Recommendation).count()
