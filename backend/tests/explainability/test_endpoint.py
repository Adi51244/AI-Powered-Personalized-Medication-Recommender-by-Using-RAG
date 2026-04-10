"""API tests for explainability endpoint."""

from __future__ import annotations

from fastapi.testclient import TestClient

from app.main import app
from app.models.schemas import ExplanationResponse, ShapValue
from app.core.explainability.service import ExplainabilityService


client = TestClient(app)


class _FakeExplainService:
    def explain_patient(self, patient_input, top_k_features: int = 10):
        return ExplanationResponse(
            predicted_disease="pneumonia",
            predicted_confidence=0.83,
            method="fallback",
            summary="Predicted with fallback explanation.",
            shap_values=[ShapValue(feature="symptom_cough_present", contribution=0.42, value=0.42)],
            top_features=["symptom_cough_present"],
            evidence_citations=[],
        )


def test_explainability_endpoint_returns_response(monkeypatch):
    monkeypatch.setattr(ExplainabilityService, "get_instance", classmethod(lambda cls: _FakeExplainService()))

    payload = {
        "patient": {
            "age": 45,
            "gender": "male",
            "symptoms": [{"name": "cough", "severity": 6, "duration_days": 4}],
            "chronic_conditions": [],
            "allergies": [],
            "current_medications": [],
        },
        "top_k_features": 10,
    }

    response = client.post("/api/v1/explanations", json=payload)

    assert response.status_code == 200
    data = response.json()
    assert data["predicted_disease"] == "pneumonia"
    assert data["method"] == "fallback"
    assert data["top_features"] == ["symptom_cough_present"]
