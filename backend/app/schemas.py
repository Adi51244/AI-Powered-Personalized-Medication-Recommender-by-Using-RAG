from pydantic import BaseModel, EmailStr
from typing import Optional, List, Any
from datetime import datetime

# User Schemas
class UserCreate(BaseModel):
    user_id: str
    email: EmailStr
    display_name: str
    role: Optional[str] = "patient"

class UserResponse(BaseModel):
    user_id: str
    email: str
    display_name: str
    role: str
    created_at: datetime

    class Config:
        from_attributes = True

# Diagnosis Schemas
class DiagnosisMetadata(BaseModel):
    age: Optional[int] = None
    gender: Optional[str] = None
    medical_history: Optional[List[str]] = None

class DiagnosisCreate(BaseModel):
    primary_diagnosis: str
    confidence: float
    predictions: List[Any]
    medications: List[str]
    simple_explanation: str
    technical_explanation: str
    evidence_sources: List[Any]
    safety_status: str = "safe"
    safety_alerts: Optional[List[Any]] = None
    symptoms: List[str]
    patient_info: DiagnosisMetadata

class DiagnosisResponse(BaseModel):
    id: str
    user_id: str
    primary_diagnosis: str
    confidence: float
    simple_explanation: str
    medications: List[str]
    safety_status: str
    created_at: datetime

    class Config:
        from_attributes = True

# Recommendation Schemas
class RecommendationCreate(BaseModel):
    medication_name: str
    dosage: str
    frequency: str
    duration: str
    reason: str
    simple_explanation: str

class RecommendationResponse(BaseModel):
    id: str
    diagnosis_id: str
    medication_name: str
    dosage: str
    frequency: str
    approved: bool
    created_at: datetime

    class Config:
        from_attributes = True
