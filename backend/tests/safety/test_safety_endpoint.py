"""Tests for safety validation API endpoint."""

from __future__ import annotations

import json
from pathlib import Path

from fastapi.testclient import TestClient

from app.config import settings
from app.main import app
from app.core.safety.validator import SafetyValidator


client = TestClient(app)


def test_safety_validate_endpoint_returns_annotated_recommendations(tmp_path: Path):
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
    SafetyValidator._instance = None

    payload = {
        "patient": {
            "age": 70,
            "gender": "female",
            "symptoms": [{"name": "pain", "severity": 5, "duration_days": 1}],
            "chronic_conditions": ["chronic kidney disease"],
            "allergies": ["penicillin"],
            "current_medications": ["Warfarin"],
        },
        "recommendations": [
            {
                "name": "Ibuprofen",
                "dosage": "800 mg",
                "duration": "7 days",
                "evidence": [],
                "safety_status": "safe",
                "warnings": [],
            },
            {
                "name": "Penicillin",
                "dosage": "500 mg",
                "duration": "5 days",
                "evidence": [],
                "safety_status": "safe",
                "warnings": [],
            },
        ],
    }

    try:
        response = client.post("/api/v1/safety/validate", json=payload)
        assert response.status_code == 200

        body = response.json()
        assert body["validation"]["safe"] is False
        assert len(body["validation"]["warnings"]) >= 2

        statuses = {item["name"].lower(): item["safety_status"] for item in body["recommendations"]}
        assert statuses["ibuprofen"] == "contraindicated"
        assert statuses["penicillin"] == "contraindicated"
    finally:
        settings.drug_interactions_path = old_path
        SafetyValidator._instance = None
