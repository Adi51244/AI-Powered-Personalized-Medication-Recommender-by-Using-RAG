"""
Database repositories for CRUD operations.
"""

from .patient_repository import PatientRepository
from .diagnosis_repository import DiagnosisRepository
from .recommendation_repository import RecommendationRepository

__all__ = [
    "PatientRepository",
    "DiagnosisRepository",
    "RecommendationRepository",
]
