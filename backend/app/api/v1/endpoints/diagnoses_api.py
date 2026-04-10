from fastapi import APIRouter, HTTPException, Depends
from sqlalchemy.orm import Session
from app.db.session import get_session
from app.db.base import Diagnosis, UserProfile, Patient
from app.schemas import DiagnosisCreate, DiagnosisResponse
from app.api.v1.endpoints.diagnosis import get_cached_diagnosis
from datetime import datetime
import uuid

router = APIRouter(prefix="/diagnoses", tags=["diagnoses"])

@router.post("/save", response_model=DiagnosisResponse)
async def save_diagnosis(
    user_id: str,
    diagnosis: DiagnosisCreate,
    session: Session = Depends(get_session)
):
    """Save a diagnosis to the database"""
    
    # Verify user exists
    user = session.query(UserProfile).filter(
        UserProfile.user_id == user_id
    ).first()
    
    if not user:
        raise HTTPException(status_code=404, detail="User not found")
    
    # Create diagnosis record
    db_diagnosis = Diagnosis(
        id=str(uuid.uuid4()),
        user_id=user_id,
        primary_diagnosis=diagnosis.primary_diagnosis,
        confidence=diagnosis.confidence,
        predictions=diagnosis.predictions,
        medications=diagnosis.medications,
        simple_explanation=diagnosis.simple_explanation,
        technical_explanation=diagnosis.technical_explanation,
        evidence_sources=diagnosis.evidence_sources,
        safety_status=diagnosis.safety_status,
        safety_alerts=diagnosis.safety_alerts,
        symptoms=diagnosis.symptoms,
        patient_info=diagnosis.patient_info.dict() if diagnosis.patient_info else None
    )
    
    session.add(db_diagnosis)
    session.commit()
    session.refresh(db_diagnosis)
    
    return db_diagnosis

@router.get("/patient/{user_id}")
async def get_patient_diagnoses(
    user_id: str,
    session: Session = Depends(get_session)
):
    """Get all diagnoses for a patient"""
    
    diagnoses = session.query(Diagnosis).filter(
        Diagnosis.user_id == user_id
    ).order_by(Diagnosis.created_at.desc()).all()
    
    return {
        "user_id": user_id,
        "total": len(diagnoses),
        "diagnoses": diagnoses
    }

@router.get("/record/{diagnosis_id}")
async def get_diagnosis_record(
    diagnosis_id: str,
    session: Session = Depends(get_session)
):
    """Get a specific diagnosis with all details"""
    if diagnosis_id.startswith("diag_"):
        cached = get_cached_diagnosis(diagnosis_id)
        if cached:
            return cached.model_dump()
    
    diagnosis = session.query(Diagnosis).filter(
        Diagnosis.id == diagnosis_id
    ).first()
    
    if not diagnosis:
        raise HTTPException(status_code=404, detail="Diagnosis not found")
    
    return diagnosis
