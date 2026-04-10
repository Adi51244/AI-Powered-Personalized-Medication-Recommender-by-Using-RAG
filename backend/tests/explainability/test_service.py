"""Unit tests for Phase 6 explainability service."""

from __future__ import annotations

import numpy as np

from app.core.explainability.service import ExplainabilityService, _PredictionContext
from app.models.schemas import PatientInput, ShapValue, SymptomInput


def _patient() -> PatientInput:
    return PatientInput(
        age=52,
        gender="male",
        symptoms=[SymptomInput(name="cough", severity=5, duration_days=3)],
        chronic_conditions=[],
        allergies=[],
        current_medications=[],
    )


def test_explain_patient_uses_primary_contributions(monkeypatch):
    service = ExplainabilityService.get_instance()

    ctx = _PredictionContext(
        disease="pneumonia",
        confidence=0.72,
        class_index=1,
        feature_vector=np.array([[0.2, 0.8]], dtype=np.float32),
        feature_names=["feat_a", "feat_b"],
    )

    monkeypatch.setattr(service, "_ensure_predictor_loaded", lambda: None)
    monkeypatch.setattr(service, "_build_prediction_context", lambda _: ctx)
    monkeypatch.setattr(
        service,
        "_compute_shap_values",
        lambda *_args, **_kwargs: ([ShapValue(feature="feat_b", contribution=0.8, value=0.8)], "shap"),
    )
    monkeypatch.setattr(service, "_compute_lime_values", lambda *_args, **_kwargs: [])

    result = service.explain_patient(_patient(), top_k_features=5)

    assert result.predicted_disease == "pneumonia"
    assert result.method == "shap"
    assert result.top_features == ["feat_b"]


def test_explain_patient_hybrid_merges_shap_and_lime(monkeypatch):
    service = ExplainabilityService.get_instance()

    ctx = _PredictionContext(
        disease="asthma",
        confidence=0.61,
        class_index=2,
        feature_vector=np.array([[0.1, 0.4, 0.9]], dtype=np.float32),
        feature_names=["f1", "f2", "f3"],
    )

    monkeypatch.setattr(service, "_ensure_predictor_loaded", lambda: None)
    monkeypatch.setattr(service, "_build_prediction_context", lambda _: ctx)
    monkeypatch.setattr(
        service,
        "_compute_shap_values",
        lambda *_args, **_kwargs: (
            [
                ShapValue(feature="f3", contribution=0.9, value=0.9),
                ShapValue(feature="f2", contribution=0.4, value=0.4),
            ],
            "shap",
        ),
    )
    monkeypatch.setattr(
        service,
        "_compute_lime_values",
        lambda *_args, **_kwargs: [ShapValue(feature="f1", contribution=0.7, value="lime")],
    )

    result = service.explain_patient(_patient(), top_k_features=3)

    assert result.method == "hybrid"
    assert len(result.shap_values) == 3
    assert "f3" in result.top_features
    assert "f1" in result.top_features
