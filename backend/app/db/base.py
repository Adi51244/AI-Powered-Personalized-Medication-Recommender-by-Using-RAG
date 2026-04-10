"""
Database models and schema for MediRAG.

This module defines the SQLAlchemy models for the PostgreSQL database.
"""
from datetime import datetime
from typing import Optional
from sqlalchemy import Column, String, Integer, Float, DateTime, Boolean, ForeignKey, Text
from sqlalchemy.dialects.postgresql import UUID, JSONB
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import relationship
import uuid


Base = declarative_base()


def generate_uuid():
    """Generate UUID for primary keys."""
    return str(uuid.uuid4())


class UserProfile(Base):
    """User profile for Supabase authentication integration."""

    __tablename__ = "user_profiles"

    user_id = Column(String, primary_key=True)
    email = Column(String, unique=True, index=True, nullable=False)
    display_name = Column(String, nullable=False)
    role = Column(String, default="patient")  # patient, admin, doctor
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    def __repr__(self):
        return f"<UserProfile(user_id={self.user_id}, email={self.email}, role={self.role})>"


class Patient(Base):
    """Patient information and medical history."""

    __tablename__ = "patients"

    id = Column(UUID(as_uuid=False), primary_key=True, default=generate_uuid)
    age = Column(Integer, nullable=False)
    gender = Column(String(20), nullable=False)
    weight_kg = Column(Float, nullable=True)
    height_cm = Column(Float, nullable=True)
    allergies = Column(JSONB, default=list)  # List of allergy strings
    chronic_conditions = Column(JSONB, default=list)  # List of condition strings
    current_medications = Column(JSONB, default=list)  # List of medication strings
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    # Relationships
    diagnoses = relationship("Diagnosis", back_populates="patient", cascade="all, delete-orphan")

    def __repr__(self):
        return f"<Patient(id={self.id}, age={self.age}, gender={self.gender})>"


class Diagnosis(Base):
    """Diagnosis results from ML and RAG pipelines."""

    __tablename__ = "diagnoses"

    id = Column(UUID(as_uuid=False), primary_key=True, default=generate_uuid)
    patient_id = Column(UUID(as_uuid=False), ForeignKey("patients.id"), nullable=False)
    symptoms = Column(JSONB, nullable=False)  # List of symptom objects
    predictions = Column(JSONB, nullable=False)  # List of disease predictions with confidence
    ml_features = Column(JSONB, nullable=True)  # Features used for ML prediction
    rag_evidence = Column(JSONB, nullable=True)  # Retrieved documents from RAG
    created_at = Column(DateTime, default=datetime.utcnow)

    # Relationships
    patient = relationship("Patient", back_populates="diagnoses")
    recommendations = relationship("Recommendation", back_populates="diagnosis", cascade="all, delete-orphan")

    def __repr__(self):
        return f"<Diagnosis(id={self.id}, patient_id={self.patient_id})>"


class Recommendation(Base):
    """Medication recommendations with safety validation results."""

    __tablename__ = "recommendations"

    id = Column(UUID(as_uuid=False), primary_key=True, default=generate_uuid)
    diagnosis_id = Column(UUID(as_uuid=False), ForeignKey("diagnoses.id"), nullable=False)
    medications = Column(JSONB, nullable=False)  # List of medication objects
    safety_checks = Column(JSONB, nullable=False)  # Results of safety validation
    explanations = Column(JSONB, nullable=True)  # SHAP/LIME explanations
    approved = Column(Boolean, default=False)
    approved_by = Column(String(255), nullable=True)
    created_at = Column(DateTime, default=datetime.utcnow)

    # Relationships
    diagnosis = relationship("Diagnosis", back_populates="recommendations")

    def __repr__(self):
        return f"<Recommendation(id={self.id}, diagnosis_id={self.diagnosis_id})>"


class AuditLog(Base):
    """Audit trail for all critical actions."""

    __tablename__ = "audit_log"

    id = Column(UUID(as_uuid=False), primary_key=True, default=generate_uuid)
    entity_type = Column(String(50), nullable=False)  # "patient", "diagnosis", "recommendation"
    entity_id = Column(UUID(as_uuid=False), nullable=False)
    action = Column(String(50), nullable=False)  # "create", "update", "delete", "approve"
    user_id = Column(String(255), nullable=True)  # Future: actual user ID
    changes = Column(JSONB, nullable=True)  # What changed
    timestamp = Column(DateTime, default=datetime.utcnow)

    def __repr__(self):
        return f"<AuditLog(id={self.id}, action={self.action}, entity_type={self.entity_type})>"
