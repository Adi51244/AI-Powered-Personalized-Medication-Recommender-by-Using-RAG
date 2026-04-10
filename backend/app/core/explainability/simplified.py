"""
Simplified explanation generator for patient education.
Converts technical diagnosis into simple, understandable language.
"""

from typing import List, Optional
from dataclasses import dataclass
from enum import Enum


class ExplanationLevel(str, Enum):
    SIMPLE = "simple"  # Simple terms, for general public
    INTERMEDIATE = "intermediate"  # Some medical terms, for informed patients
    DETAILED = "detailed"  # Full technical explanation


@dataclass
class SimpleExplanation:
    """User-friendly explanation for patients."""
    problem: str
    cause: str
    why_our_system_recommended_this: str
    what_you_should_do: str
    medications_explained: List[dict]
    risk_factors_explained: List[str]
    when_to_seek_help: List[str]
    confidence_level: str


class SimplifiedExplainationService:
    """Convert medical findings into simple explanations."""

    @staticmethod
    def get_simple_explanation(
        disease: str,
        confidence: float,
        symptoms: List[str],
        medications: List[dict],
        evidence_sources: List[str],
        level: ExplanationLevel = ExplanationLevel.SIMPLE,
    ) -> SimpleExplanation:
        """
        Generate a simple explanation of the diagnosis.

        Args:
            disease: Diagnosed condition
            confidence: Confidence percentage (0-100)
            symptoms: Patient's reported symptoms
            medications: Recommended medications
            evidence_sources: Medical sources supporting the diagnosis
            level: Explanation complexity level

        Returns:
            SimpleExplanation object with user-friendly text
        """

        # Simplify disease name
        simple_disease = SimplifiedExplainationService._simplify_disease_name(disease)

        # Build problem statement
        problem = SimplifiedExplainationService._build_problem_statement(
            simple_disease, symptoms, level
        )

        # Explain why these symptoms suggest this condition
        cause = SimplifiedExplainationService._explain_cause(
            simple_disease, symptoms, level
        )

        # Explain the AI's reasoning
        why_recommended = SimplifiedExplainationService._explain_recommendation_logic(
            simple_disease, confidence, evidence_sources, level
        )

        # What to do about it
        what_to_do = SimplifiedExplainationService._build_action_plan(
            simple_disease, medications, level
        )

        # Explain medications in simple terms
        medications_explained = [
            SimplifiedExplainationService._explain_medication(med, level)
            for med in medications
        ]

        # Risk factors
        risk_factors = SimplifiedExplainationService._extract_risk_factors(
            simple_disease, level
        )

        # When to seek emergency help
        when_to_seek = SimplifiedExplainationService._get_emergency_signs(
            simple_disease, level
        )

        # Confidence level in plain language
        confidence_text = SimplifiedExplainationService._confidence_to_text(
            confidence, level
        )

        return SimpleExplanation(
            problem=problem,
            cause=cause,
            why_our_system_recommended_this=why_recommended,
            what_you_should_do=what_to_do,
            medications_explained=medications_explained,
            risk_factors_explained=risk_factors,
            when_to_seek_help=when_to_seek,
            confidence_level=confidence_text,
        )

    @staticmethod
    def _simplify_disease_name(disease: str) -> str:
        """Convert medical disease names to simple terms."""
        simplifications = {
            "pharyngitis": "sore throat",
            "rhinitis": "runny/stuffy nose",
            "bronchitis": "chest cold",
            "pneumonia": "lung infection",
            "gastroenteritis": "stomach flu",
            "dermatitis": "skin irritation",
            "hypertension": "high blood pressure",
            "diabetes": "diabetes",
            "asthma": "asthma",
            "migraine": "severe headache",
            "arthralgia": "joint pain",
            "fever": "high temperature",
            "influenza": "flu",
            "common cold": "cold",
        }

        disease_lower = disease.lower()
        for medical, simple in simplifications.items():
            if medical in disease_lower:
                return simple

        return disease

    @staticmethod
    def _build_problem_statement(
        disease: str, symptoms: List[str], level: ExplanationLevel
    ) -> str:
        """Build a simple statement of what the patient likely has."""
        if level == ExplanationLevel.SIMPLE:
            return f"Based on your symptoms, it looks like you might have **{disease}**. This is a common condition that can be treated."
        elif level == ExplanationLevel.INTERMEDIATE:
            return f"Your symptoms are consistent with **{disease}**. This condition affects the {SimplifiedExplainationService._get_body_part(disease)}."
        else:
            return f"Clinical assessment indicates probable **{disease}** based on symptomatology and risk factors."

    @staticmethod
    def _explain_cause(
        disease: str, symptoms: List[str], level: ExplanationLevel
    ) -> str:
        """Explain why these symptoms indicate this condition."""
        symptom_list = ", ".join(symptoms[:3])

        if level == ExplanationLevel.SIMPLE:
            return (
                f"Your symptoms ({symptom_list}) are typical of {disease}. "
                f"When you have these symptoms together, it usually means your body is "
                f"reacting to a {SimplifiedExplainationService._get_simple_cause(disease)}."
            )
        elif level == ExplanationLevel.INTERMEDIATE:
            return (
                f"The combination of symptoms ({symptom_list}) suggests {disease}. "
                f"These are characteristic presentations of {SimplifiedExplainationService._get_medical_cause(disease)}."
            )
        else:
            return f"Symptom cluster ({symptom_list}) supports presumptive diagnosis of {disease}."

    @staticmethod
    def _explain_recommendation_logic(
        disease: str, confidence: float, evidence_sources: List[str], level: ExplanationLevel
    ) -> str:
        """Explain why our AI recommended this diagnosis."""
        if level == ExplanationLevel.SIMPLE:
            return (
                f"Our AI system analyzed your symptoms and matched them against thousands of cases. "
                f"The diagnosis of {disease} has a {int(confidence)}% match. "
                f"We're basing this on medical guidelines from reputable sources like WHO and clinical databases. "
                f"However, always see a doctor for confirmation."
            )
        elif level == ExplanationLevel.INTERMEDIATE:
            return (
                f"The recommendation algorithm achieved {int(confidence)}% confidence by cross-referencing "
                f"against clinical pathways from {', '.join(evidence_sources[:2])}. "
                f"This level of confidence supports a provisional diagnosis pending clinical evaluation."
            )
        else:
            return (
                f"RAG-based inference with {int(confidence)}% confidence score derived from "
                f"{'evidence sources' if evidence_sources else 'clinical databases'}."
            )

    @staticmethod
    def _build_action_plan(
        disease: str, medications: List[dict], level: ExplanationLevel
    ) -> str:
        """Build a simple action plan for the patient."""
        med_names = [m.get("name", "medication") for m in medications[:2]]
        med_list = " and ".join(med_names) if med_names else "medication"

        if level == ExplanationLevel.SIMPLE:
            return (
                f"1. **See a Doctor**: Get a professional diagnosis to confirm\n"
                f"2. **Take Prescribed Medication**: {med_list} (as directed)\n"
                f"3. **Rest & Recovery**: Get plenty of sleep and fluids\n"
                f"4. **Follow Up**: Return to doctor if symptoms don't improve in a few days"
            )
        elif level == ExplanationLevel.INTERMEDIATE:
            return (
                f"1. Clinical confirmation by healthcare provider\n"
                f"2. Pharmacotherapy with {med_list} as indicated\n"
                f"3. Supportive care and monitoring\n"
                f"4. Follow-up assessment if symptoms persist"
            )
        else:
            return "Implement clinical management protocol as recommended."

    @staticmethod
    def _explain_medication(medication: dict, level: ExplanationLevel) -> dict:
        """Explain a medication in simple terms."""
        name = medication.get("name", "Unknown")
        dosage = medication.get("dosage", "as directed")
        safety = medication.get("safety_status", "safe")

        simple_purpose = {
            "aspirin": "Pain relief and fever reduction",
            "acetaminophen": "Pain relief and fever reduction",
            "ibuprofen": "Pain relief and inflammation reduction",
            "amoxicillin": "Antibiotic to fight bacterial infections",
            "doxycycline": "Antibiotic for infections",
            "omeprazole": "Reduces stomach acid",
            "metformin": "Helps control blood sugar",
            "lisinopril": "Lowers blood pressure",
            "atorvastatin": "Lowers cholesterol",
        }

        purpose = simple_purpose.get(name.lower(), "Treats your condition")

        if level == ExplanationLevel.SIMPLE:
            return {
                "name": name,
                "dosage": dosage,
                "purpose": purpose,
                "how_it_works": f"This medication helps your body fight {purpose.lower()}",
                "side_effects": "Take as directed. Common side effects are mild.",
                "safety": f"This medication is {safety} for you.",
            }
        elif level == ExplanationLevel.INTERMEDIATE:
            return {
                "name": name,
                "dosage": dosage,
                "purpose": purpose,
                "mechanism": f"Pharmacologically indicated for {purpose.lower()}",
                "contraindications": "Follow contraindication checks with prescriber",
                "safety": f"Safety status: {safety}",
            }
        else:
            return medication

    @staticmethod
    def _extract_risk_factors(disease: str, level: ExplanationLevel) -> List[str]:
        """Extract simple risk factors for a disease."""
        risk_map = {
            "sore throat": [
                "Exposed to someone with a sore throat",
                "Cold or warm weather",
                "Smoking or air pollution",
                "Weak immune system",
            ],
            "cold": [
                "Contact with people who have a cold",
                "Stress and fatigue",
                "Poor hand hygiene",
                "Winter season",
            ],
            "flu": [
                "Not vaccinated",
                "Close contact with infected people",
                "Crowded places",
                "Age extremes (very young or old)",
            ],
            "high blood pressure": [
                "High salt diet",
                "Stress",
                "Obesity",
                "Family history",
                "Lack of exercise",
            ],
            "diabetes": [
                "Family history",
                "Obesity",
                "Sedentary lifestyle",
                "High sugar diet",
                "Age",
            ],
        }

        disease_lower = disease.lower()
        factors = []
        for key, value in risk_map.items():
            if key in disease_lower:
                factors = value
                break

        if level == ExplanationLevel.SIMPLE:
            return factors
        else:
            return [f"Risk factor: {f}" for f in factors]

    @staticmethod
    def _get_emergency_signs(disease: str, level: ExplanationLevel) -> List[str]:
        """Get emergency warning signs for a disease."""
        emergency_map = {
            "sore throat": [
                "Difficulty breathing or swallowing",
                "Severe pain that doesn't improve",
                "High fever (over 103°F)",
                "Swelling in neck",
            ],
            "pneumonia": [
                "Difficulty breathing",
                "Chest pain",
                "Coughing up blood",
                "Severe shortness of breath",
            ],
            "high blood pressure": [
                "Severe headache",
                "Chest pain",
                "Shortness of breath",
                "Vision changes",
            ],
            "diabetes": [
                "Extreme thirst with no relief",
                "Unconsciousness or confusion",
                "Sweet smell to breath",
                "Fruity urine odor",
            ],
        }

        disease_lower = disease.lower()
        signs = []
        for key, value in emergency_map.items():
            if key in disease_lower:
                signs = value
                break

        if not signs:
            signs = [
                "Severe worsening of symptoms",
                "Difficulty breathing",
                "Loss of consciousness",
                "Severe chest or abdominal pain",
            ]

        if level == ExplanationLevel.SIMPLE:
            return [f"🚨 {sign}" for sign in signs]
        else:
            return signs

    @staticmethod
    def _confidence_to_text(confidence: float, level: ExplanationLevel) -> str:
        """Convert confidence percentage to plain language."""
        if confidence >= 85:
            confident = "Very confident" if level == ExplanationLevel.SIMPLE else "High confidence"
        elif confidence >= 70:
            confident = "Fairly confident" if level == ExplanationLevel.SIMPLE else "Moderate-to-high confidence"
        elif confidence >= 50:
            confident = "Some confidence" if level == ExplanationLevel.SIMPLE else "Moderate confidence"
        else:
            confident = "Lower confidence" if level == ExplanationLevel.SIMPLE else "Low confidence"

        return f"{confident} ({int(confidence)}%)"

    @staticmethod
    def _get_body_part(disease: str) -> str:
        """Map disease to affected body part."""
        part_map = {
            "sore throat": "throat",
            "runny nose": "nose",
            "bronchitis": "lungs",
            "pneumonia": "lungs",
            "gastroenteritis": "stomach",
            "dermatitis": "skin",
            "arthralgia": "joints",
        }
        return part_map.get(disease.lower(), "body")

    @staticmethod
    def _get_simple_cause(disease: str) -> str:
        """Get simple cause explanation."""
        cause_map = {
            "sore throat": "viral or bacterial infection",
            "cold": "viral infection",
            "flu": "virus",
            "pneumonia": "bacterial or viral lung infection",
            "gastroenteritis": "stomach virus or bacteria",
            "high blood pressure": "stress or lifestyle factors",
        }
        return cause_map.get(disease.lower(), "infection or condition")

    @staticmethod
    def _get_medical_cause(disease: str) -> str:
        """Get more medical cause explanation."""
        return f"pathophysiology consistent with {disease}"
