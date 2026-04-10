"""Tests for Phase 5 safety validator."""

from __future__ import annotations

import json
from pathlib import Path

from app.config import settings
from app.core.safety.validator import SafetyValidator
from app.models.schemas import MedicationRecommendation, PatientInput, SymptomInput


def _build_patient() -> PatientInput:
    return PatientInput(
        age=72,
        gender="female",
        symptoms=[SymptomInput(name="chest pain", severity=7, duration_days=2)],
        chronic_conditions=["chronic kidney disease"],
        allergies=["penicillin"],
        current_medications=["Warfarin"],
    )


def test_safety_validator_flags_interaction_allergy_contraindication(tmp_path: Path):
    interactions_path = tmp_path / "drug_interactions.json"
    interactions_path.write_text(
        json.dumps(
            {
                "interactions": [
                    {
                        "drug1_name": "Warfarin",
                        "drug2_name": "Ibuprofen",
                        "description": "Ibuprofen increases bleeding risk with warfarin.",
                        "severity": "major",
                    }
                ]
            }
        ),
        encoding="utf-8",
    )

    old_path = settings.drug_interactions_path
    settings.drug_interactions_path = str(interactions_path)

    try:
        # Reset singleton for isolated test state.
        SafetyValidator._instance = None
        validator = SafetyValidator.get_instance()

        recommendations = [
            MedicationRecommendation(
                name="Ibuprofen",
                dosage="800 mg",
                duration="7 days",
                evidence=[],
                safety_status="safe",
                warnings=[],
            ),
            MedicationRecommendation(
                name="Penicillin",
                dosage="500 mg",
                duration="5 days",
                evidence=[],
                safety_status="safe",
                warnings=[],
            ),
        ]

        updated, result = validator.validate_recommendations(_build_patient(), recommendations)

        assert result.safe is False
        assert any(w.type == "drug_interaction" for w in result.warnings)
        assert any(w.type == "allergy" for w in result.warnings)
        assert any(w.type == "contraindication" for w in result.warnings)

        statuses = {r.name.lower(): r.safety_status for r in updated}
        assert statuses["ibuprofen"] == "contraindicated"
        assert statuses["penicillin"] == "contraindicated"
    finally:
        settings.drug_interactions_path = old_path
        SafetyValidator._instance = None
