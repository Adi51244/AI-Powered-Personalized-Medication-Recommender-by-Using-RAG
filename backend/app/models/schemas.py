"""
Pydantic schemas for API request/response validation.
"""
from typing import List, Optional, Dict, Any
from pydantic import BaseModel, Field, field_validator
from datetime import datetime


# ========== Patient Schemas ==========

class SymptomInput(BaseModel):
    """Individual symptom with severity and duration."""
    name: str = Field(..., description="Symptom name (e.g., 'fever', 'cough')")
    severity: int = Field(..., ge=1, le=10, description="Severity on scale 1-10")
    duration_days: int = Field(..., ge=0, description="Duration in days")


class PatientInput(BaseModel):
    """Patient information for diagnosis."""
    patient_id: Optional[str] = Field(None, description="Existing patient ID")
    age: int = Field(..., ge=0, le=150)
    gender: str = Field(..., description="Gender: male, female, or other")
    weight_kg: Optional[float] = Field(None, ge=0)
    height_cm: Optional[float] = Field(None, ge=0)
    symptoms: List[SymptomInput] = Field(..., min_length=1)
    chronic_conditions: List[str] = Field(default_factory=list)
    allergies: List[str] = Field(default_factory=list)
    current_medications: List[str] = Field(default_factory=list)

    @field_validator('gender', mode='before')
    @classmethod
    def normalize_gender(cls, v):
        """Normalize gender values, mapping unknown/invalid values to 'other'."""
        if not v:
            return 'other'
        v_lower = str(v).lower().strip()
        # Map common variants to valid values
        if v_lower in ('m', 'male'):
            return 'male'
        elif v_lower in ('f', 'female', 'woman', 'woman'):
            return 'female'
        elif v_lower in ('male', 'female', 'other'):
            return v_lower
        else:
            # Map any unknown value to 'other'
            return 'other'


class PatientResponse(BaseModel):
    """Patient record response."""
    id: str
    age: int
    gender: str
    weight_kg: Optional[float]
    height_cm: Optional[float]
    allergies: List[str]
    chronic_conditions: List[str]
    current_medications: List[str]
    created_at: datetime

    class Config:
        from_attributes = True


# ========== Diagnosis Schemas ==========

class DiseasePrediction(BaseModel):
    """Individual disease prediction."""
    disease: str
    confidence: float = Field(..., ge=0.0, le=1.0)
    source: str = Field(..., description="ml_model or rag_retrieval")
    explanation: Optional[str] = None


class Evidence(BaseModel):
    """Evidence from retrieved documents."""
    source: str = Field(..., description="Document source (e.g., MIMIC_12345, DrugBank_DB00123)")
    type: str = Field(..., description="clinical_case, drug_profile, or clinical_guideline")
    text: str = Field(..., description="Relevant text excerpt")
    relevance_score: float = Field(..., ge=0.0, le=1.0)


class MedicationRecommendation(BaseModel):
    """Medication recommendation with evidence."""
    name: str
    dosage: str
    duration: str
    evidence: List[str] = Field(default_factory=list, description="Source IDs (e.g., DrugBank_DB00123)")
    safety_status: str = Field(..., pattern="^(safe|contraindicated|warning)$")
    warnings: List[str] = Field(default_factory=list)


class DiagnosisResponse(BaseModel):
    """Diagnosis result with predictions and recommendations."""
    diagnosis_id: str
    predictions: List[DiseasePrediction]
    recommendations: List[MedicationRecommendation]
    evidence: List[Evidence]


# ========== Safety Validation Schemas ==========

class SafetyWarning(BaseModel):
    """Safety warning from validation."""
    type: str = Field(..., pattern="^(drug_interaction|allergy|contraindication)$")
    severity: str = Field(..., pattern="^(major|moderate|minor)$")
    message: str
    drugs: Optional[List[str]] = None


class ValidationRequest(BaseModel):
    """Request to validate medication recommendations."""
    patient_id: str
    medications: List[str]


class SafetyValidationResponse(BaseModel):
    """Result of safety validation."""
    safe: bool
    warnings: List[SafetyWarning]
    safe_medications: List[str]
    blocked_medications: List[str]


class SafetyValidationInput(BaseModel):
    """Payload for direct safety validation endpoint."""
    patient: PatientInput
    recommendations: List[MedicationRecommendation]


class SafetyValidationDetailedResponse(BaseModel):
    """Safety validation result with annotated recommendations."""
    validation: SafetyValidationResponse
    recommendations: List[MedicationRecommendation]


# ========== Explainability Schemas ==========

class ShapValue(BaseModel):
    """SHAP feature importance value."""
    feature: str
    contribution: float
    value: Any


class ExplanationRequest(BaseModel):
    """Request payload for explainability endpoint."""
    patient: PatientInput
    top_k_features: int = Field(default=10, ge=3, le=30)


class ExplanationResponse(BaseModel):
    """Explanation for a diagnosis prediction."""
    predicted_disease: str
    predicted_confidence: float = Field(..., ge=0.0, le=1.0)
    method: str = Field(..., description="shap|lime|hybrid|fallback")
    summary: str
    shap_values: List[ShapValue]
    top_features: List[str]
    evidence_citations: List[Evidence]


# ========== Health Check ==========

class HealthResponse(BaseModel):
    """API health check response."""
    status: str
    version: str
    components: Dict[str, str] = Field(
        default_factory=lambda: {
            "database": "unknown",
            "llm": "unknown",
            "vector_store": "unknown"
        }
    )


# ========== Database CRUD Schemas ==========

class PatientCreate(BaseModel):
    """Create patient request."""
    age: int = Field(..., ge=0, le=150)
    gender: str = Field(..., description="Gender: male, female, or other")
    weight_kg: Optional[float] = Field(None, ge=0)
    height_cm: Optional[float] = Field(None, ge=0)
    allergies: List[str] = Field(default_factory=list)
    chronic_conditions: List[str] = Field(default_factory=list)
    current_medications: List[str] = Field(default_factory=list)

    @field_validator('gender', mode='before')
    @classmethod
    def normalize_gender(cls, v):
        """Normalize gender values, mapping unknown/invalid values to 'other'."""
        if not v:
            return 'other'
        v_lower = str(v).lower().strip()
        if v_lower in ('m', 'male'):
            return 'male'
        elif v_lower in ('f', 'female', 'woman'):
            return 'female'
        elif v_lower in ('male', 'female', 'other'):
            return v_lower
        else:
            return 'other'


class PatientUpdate(BaseModel):
    """Update patient request."""
    age: Optional[int] = Field(None, ge=0, le=150)
    gender: Optional[str] = Field(None, description="Gender: male, female, or other")
    weight_kg: Optional[float] = Field(None, ge=0)
    height_cm: Optional[float] = Field(None, ge=0)
    allergies: Optional[List[str]] = None
    chronic_conditions: Optional[List[str]] = None
    current_medications: Optional[List[str]] = None

    @field_validator('gender', mode='before')
    @classmethod
    def normalize_gender(cls, v):
        """Normalize gender values, mapping unknown/invalid values to 'other'."""
        if v is None:
            return None
        v_lower = str(v).lower().strip()
        if v_lower in ('m', 'male'):
            return 'male'
        elif v_lower in ('f', 'female', 'woman'):
            return 'female'
        elif v_lower in ('male', 'female', 'other'):
            return v_lower
        else:
            return 'other'


class PatientListResponse(BaseModel):
    """List of patients."""
    total: int
    items: List[PatientResponse]


class DiagnosisCreate(BaseModel):
    """Create diagnosis request."""
    patient_id: str
    symptoms: List[Dict[str, Any]]
    predictions: List[Dict[str, Any]]
    ml_features: Optional[Dict[str, Any]] = None
    rag_evidence: Optional[Dict[str, Any]] = None


class DiagnosisListResponse(BaseModel):
    """List of diagnoses."""
    total: int
    items: List[DiagnosisResponse]


class RecommendationCreate(BaseModel):
    """Create recommendation request."""
    diagnosis_id: str
    medications: List[MedicationRecommendation]
    safety_checks: Dict[str, Any]
    explanations: Optional[Dict[str, Any]] = None


class RecommendationApprove(BaseModel):
    """Approve recommendation request."""
    approved_by: str = Field(..., description="User ID or name approving the recommendation")


class RecommendationListResponse(BaseModel):
    """List of recommendations."""
    total: int
    items: List[Dict[str, Any]]
