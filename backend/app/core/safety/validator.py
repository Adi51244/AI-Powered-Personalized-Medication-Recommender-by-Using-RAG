"""
Phase 5 safety validation layer.

Validates medication recommendations for:
1. Drug-drug interactions
2. Patient allergies
3. Contraindications (age/condition heuristics)
4. Dosage range checks
5. Safety scoring
"""

from __future__ import annotations

import json
import logging
import re
from dataclasses import dataclass
from itertools import combinations
from pathlib import Path
from typing import Dict, List, Optional, Tuple

from app.config import settings
from app.models.schemas import (
    MedicationRecommendation,
    PatientInput,
    SafetyValidationResponse,
    SafetyWarning,
)

logger = logging.getLogger(__name__)


# Conservative medication dosage ranges (mg/day).
DOSAGE_RANGES_MG_PER_DAY: Dict[str, Tuple[float, float]] = {
    "aspirin": (75.0, 325.0),
    "warfarin": (1.0, 10.0),
    "metformin": (500.0, 2550.0),
    "amoxicillin": (250.0, 3000.0),
    "ibuprofen": (200.0, 3200.0),
    "lisinopril": (2.5, 40.0),
    "atorvastatin": (10.0, 80.0),
    "furosemide": (20.0, 600.0),
    "clonazepam": (0.25, 4.0),
}


AGE_CONTRAINDICATIONS: Dict[str, List[str]] = {
    "elderly": ["clonazepam", "diazepam", "amitriptyline", "diphenhydramine"],
}


CONDITION_CONTRAINDICATIONS: Dict[str, List[str]] = {
    "chronic kidney disease": ["ibuprofen", "naproxen", "diclofenac"],
    "kidney disease": ["ibuprofen", "naproxen", "diclofenac"],
    "heart failure": ["ibuprofen", "naproxen", "pioglitazone"],
    "pregnancy": ["warfarin", "lisinopril", "atorvastatin"],
}


@dataclass
class _ValidationState:
    warnings: List[SafetyWarning]
    blocked_medications: List[str]
    safe_medications: List[str]
    recommendation_warnings: Dict[str, List[str]]
    recommendation_status: Dict[str, str]


class SafetyValidator:
    """Singleton safety validator used by the RAG pipeline."""

    _instance: Optional["SafetyValidator"] = None

    def __init__(self) -> None:
        self._interactions_loaded = False
        self._interaction_index: Dict[Tuple[str, str], Tuple[str, str]] = {}
        self._pair_cache: Dict[Tuple[str, ...], List[SafetyWarning]] = {}

    _SEVERITY_RANK = {"minor": 1, "moderate": 2, "major": 3}

    @classmethod
    def get_instance(cls) -> "SafetyValidator":
        if cls._instance is None:
            cls._instance = cls()
        return cls._instance

    def validate_recommendations(
        self,
        patient_input: PatientInput,
        recommendations: List[MedicationRecommendation],
    ) -> Tuple[List[MedicationRecommendation], SafetyValidationResponse]:
        """Validate recommendation list and annotate safety status per medication."""
        state = _ValidationState(
            warnings=[],
            blocked_medications=[],
            safe_medications=[],
            recommendation_warnings={},
            recommendation_status={},
        )

        rec_names = [self._normalize_name(rec.name) for rec in recommendations]
        current_meds = [self._normalize_name(med) for med in patient_input.current_medications]

        self._apply_interaction_checks(rec_names, current_meds, state)
        self._apply_allergy_checks(patient_input, rec_names, state)
        self._apply_contraindication_checks(patient_input, rec_names, state)
        self._apply_dosage_checks(recommendations, state)

        if settings.safety_max_warnings > 0 and len(state.warnings) > settings.safety_max_warnings:
            state.warnings = state.warnings[: settings.safety_max_warnings]

        blocked_set = set(state.blocked_medications)
        for rec in recommendations:
            name = self._normalize_name(rec.name)
            if name in blocked_set:
                rec.safety_status = "contraindicated"
            elif state.recommendation_status.get(name) == "warning":
                rec.safety_status = "warning"
            else:
                rec.safety_status = "safe"
                state.safe_medications.append(rec.name)

            rec.warnings = state.recommendation_warnings.get(name, [])

        result = SafetyValidationResponse(
            safe=len(state.blocked_medications) == 0,
            warnings=state.warnings,
            safe_medications=state.safe_medications,
            blocked_medications=state.blocked_medications,
        )

        return recommendations, result

    def _load_interactions(self) -> None:
        if self._interactions_loaded:
            return

        path = Path(settings.drug_interactions_path)
        if not path.exists():
            logger.warning("Drug interactions file not found: %s", path)
            self._interactions = []
            self._interactions_loaded = True
            return

        with path.open("r", encoding="utf-8") as handle:
            data = json.load(handle)

        interactions = data.get("interactions", []) if isinstance(data, dict) else []
        if not isinstance(interactions, list):
            interactions = []

        indexed: Dict[Tuple[str, str], Tuple[str, str]] = {}
        for row in interactions:
            d1 = self._normalize_name(str(row.get("drug1_name", "")))
            d2 = self._normalize_name(str(row.get("drug2_name", "")))
            if not d1 or not d2 or d1 == d2:
                continue

            severity = str(row.get("severity", "moderate")).lower()
            if severity not in self._SEVERITY_RANK:
                severity = "moderate"

            key = tuple(sorted((d1, d2)))
            message = str(row.get("description", f"Interaction between {d1} and {d2}."))

            existing = indexed.get(key)
            if existing is None or self._SEVERITY_RANK[severity] > self._SEVERITY_RANK[existing[0]]:
                indexed[key] = (severity, message)

        self._interaction_index = indexed
        self._interactions_loaded = True
        logger.info(
            "Loaded %s interaction rows, indexed %s unique drug pairs",
            len(interactions),
            len(self._interaction_index),
        )

    def _apply_interaction_checks(self, rec_names: List[str], current_meds: List[str], state: _ValidationState) -> None:
        self._load_interactions()
        if not self._interaction_index:
            return

        candidate = sorted(set([m for m in rec_names + current_meds if m]))
        cache_key = tuple(candidate)
        if cache_key in self._pair_cache:
            warnings = self._pair_cache[cache_key]
        else:
            warnings = []
            for left, right in combinations(candidate, 2):
                key = tuple(sorted((left, right)))
                match = self._interaction_index.get(key)
                if match is None:
                    continue

                severity, message = match
                warnings.append(
                    SafetyWarning(
                        type="drug_interaction",
                        severity=severity,
                        message=message,
                        drugs=[left, right],
                    )
                )
            self._pair_cache[cache_key] = warnings

        for warning in warnings:
            state.warnings.append(warning)
            for drug in warning.drugs or []:
                if drug in rec_names:
                    state.recommendation_warnings.setdefault(drug, []).append(warning.message)
                    if warning.severity == "major" and settings.safety_block_on_major_interaction:
                        state.recommendation_status[drug] = "contraindicated"
                        if drug not in state.blocked_medications:
                            state.blocked_medications.append(drug)
                    else:
                        state.recommendation_status.setdefault(drug, "warning")

    def _apply_allergy_checks(self, patient_input: PatientInput, rec_names: List[str], state: _ValidationState) -> None:
        allergies = [self._normalize_name(a) for a in patient_input.allergies]
        if not allergies:
            return

        for rec_name in rec_names:
            for allergy in allergies:
                if not allergy:
                    continue
                if allergy in rec_name or rec_name in allergy:
                    msg = f"Medication {rec_name} conflicts with recorded allergy: {allergy}."
                    warning = SafetyWarning(
                        type="allergy",
                        severity="major",
                        message=msg,
                        drugs=[rec_name],
                    )
                    state.warnings.append(warning)
                    state.recommendation_warnings.setdefault(rec_name, []).append(msg)
                    state.recommendation_status[rec_name] = "contraindicated"
                    if rec_name not in state.blocked_medications:
                        state.blocked_medications.append(rec_name)

    def _apply_contraindication_checks(self, patient_input: PatientInput, rec_names: List[str], state: _ValidationState) -> None:
        if patient_input.age >= 65:
            for med in AGE_CONTRAINDICATIONS["elderly"]:
                if med in rec_names:
                    msg = f"Medication {med} may be inappropriate in older adults (age {patient_input.age})."
                    warning = SafetyWarning(
                        type="contraindication",
                        severity="moderate",
                        message=msg,
                        drugs=[med],
                    )
                    state.warnings.append(warning)
                    state.recommendation_warnings.setdefault(med, []).append(msg)
                    state.recommendation_status.setdefault(med, "warning")

        conditions = [self._normalize_name(c) for c in patient_input.chronic_conditions]
        for condition in conditions:
            for cond_key, meds in CONDITION_CONTRAINDICATIONS.items():
                if cond_key in condition:
                    for med in meds:
                        if med in rec_names:
                            msg = f"Medication {med} may be contraindicated with condition: {condition}."
                            warning = SafetyWarning(
                                type="contraindication",
                                severity="major",
                                message=msg,
                                drugs=[med],
                            )
                            state.warnings.append(warning)
                            state.recommendation_warnings.setdefault(med, []).append(msg)
                            state.recommendation_status[med] = "contraindicated"
                            if med not in state.blocked_medications:
                                state.blocked_medications.append(med)

    def _apply_dosage_checks(self, recommendations: List[MedicationRecommendation], state: _ValidationState) -> None:
        for rec in recommendations:
            name = self._normalize_name(rec.name)
            if name not in DOSAGE_RANGES_MG_PER_DAY:
                continue

            parsed = self._extract_first_mg_amount(rec.dosage)
            if parsed is None:
                continue

            min_dose, max_dose = DOSAGE_RANGES_MG_PER_DAY[name]
            if parsed < min_dose or parsed > max_dose:
                msg = (
                    f"Dosage for {name} appears outside conservative range "
                    f"({min_dose:g}-{max_dose:g} mg/day): {parsed:g} mg."
                )
                warning = SafetyWarning(
                    type="contraindication",
                    severity="moderate",
                    message=msg,
                    drugs=[name],
                )
                state.warnings.append(warning)
                state.recommendation_warnings.setdefault(name, []).append(msg)
                state.recommendation_status.setdefault(name, "warning")

    @staticmethod
    def _normalize_name(value: str) -> str:
        cleaned = value.lower().strip()
        cleaned = re.sub(r"\s+", " ", cleaned)
        cleaned = re.sub(r"[^a-z0-9\s]", "", cleaned)
        return cleaned

    @staticmethod
    def _extract_first_mg_amount(dosage: str) -> Optional[float]:
        # Matches values like "500mg" or "2.5 mg"
        match = re.search(r"(\d+(?:\.\d+)?)\s*mg", dosage.lower())
        if not match:
            return None
        try:
            return float(match.group(1))
        except ValueError:
            return None
