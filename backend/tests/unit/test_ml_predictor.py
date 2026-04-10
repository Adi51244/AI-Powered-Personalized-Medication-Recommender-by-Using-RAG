"""Unit tests for MLPredictor service."""

from __future__ import annotations

from app.ml.predictor import MLPredictor
from app.models.schemas import DiseasePrediction, PatientInput, SymptomInput


def test_ml_predictor_loads_artifacts():
    predictor = MLPredictor.get_instance()
    predictor.load_models(models_path="data/models/disease_models", artifacts_path="data/ml")

    assert predictor.loaded is True
    assert len(predictor.models) >= 2
    assert predictor.label_encoder is not None
    assert predictor.feature_extractor is not None


def test_ml_predictor_returns_ranked_predictions():
    predictor = MLPredictor.get_instance()
    predictor.load_models(models_path="data/models/disease_models", artifacts_path="data/ml")

    patient = PatientInput(
        age=62,
        gender="male",
        symptoms=[
            SymptomInput(name="chest pain", severity=8, duration_days=2),
            SymptomInput(name="shortness of breath", severity=7, duration_days=2),
        ],
        chronic_conditions=["hypertension", "diabetes"],
        current_medications=["aspirin"],
        allergies=["penicillin"],
    )

    predictions = predictor.predict_from_patient(patient, top_k=5)

    assert predictions
    assert all(isinstance(p, DiseasePrediction) for p in predictions)
    assert all(0.0 <= p.confidence <= 1.0 for p in predictions)
    assert predictions[0].confidence >= predictions[-1].confidence
    assert all(p.source == "ml_ensemble" for p in predictions)
