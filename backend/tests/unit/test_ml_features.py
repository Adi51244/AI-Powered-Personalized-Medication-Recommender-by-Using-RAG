"""Unit tests for FeatureExtractor."""

from __future__ import annotations

from pathlib import Path

import numpy as np

from app.ml.feature_engineering import FeatureConfig, FeatureExtractor
from app.models.schemas import PatientInput, SymptomInput


def _sample_patients():
    return [
        {
            "age": 63,
            "gender": "male",
            "symptoms": [{"name": "chest pain", "severity": 8, "duration_days": 2}],
            "chronic_conditions": ["hypertension"],
            "current_medications": ["aspirin"],
            "allergies": ["penicillin"],
        },
        {
            "age": 48,
            "gender": "female",
            "symptoms": [{"name": "fever", "severity": 6, "duration_days": 3}],
            "chronic_conditions": ["asthma"],
            "current_medications": ["albuterol"],
            "allergies": [],
        },
    ]


def test_feature_extractor_fit_transform_shape():
    extractor = FeatureExtractor(
        FeatureConfig(
            n_symptom_features=8,
            n_condition_features=6,
            n_medication_features=5,
            n_allergy_features=4,
        )
    )
    matrix = extractor.fit_transform(_sample_patients())

    assert matrix.shape[0] == 2
    assert matrix.shape[1] == len(extractor.feature_names)
    assert matrix.dtype == np.float32


def test_feature_extractor_save_load_roundtrip(tmp_path: Path):
    extractor = FeatureExtractor(FeatureConfig(n_symptom_features=5, n_condition_features=5))
    extractor.fit(_sample_patients())

    sample = PatientInput(
        age=60,
        gender="male",
        symptoms=[SymptomInput(name="chest pain", severity=9, duration_days=1)],
        chronic_conditions=["hypertension"],
        current_medications=["aspirin"],
        allergies=["penicillin"],
    )

    before = extractor.transform(sample)
    out = tmp_path / "feature_extractor.pkl"
    extractor.save(str(out))

    loaded = FeatureExtractor.load(str(out))
    after = loaded.transform(sample)

    assert np.allclose(before, after)
