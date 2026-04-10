"""
Prompt templates for medical LLM generation.

This module contains prompt templates specifically designed for medical
medication recommendation using RAG-retrieved context.
"""

from typing import Dict
from app.models.schemas import PatientInput


SYSTEM_PROMPT = """You are a medical AI assistant helping clinicians make evidence-based medication recommendations.

Your role is to:
1. Analyze patient information and medical evidence
2. Recommend appropriate medications with dosages
3. Cite evidence sources from retrieved medical literature
4. Highlight potential safety concerns
5. Provide clear reasoning for recommendations

Always prioritize patient safety and evidence-based medicine."""


def build_medication_recommendation_prompt(
    patient_input: PatientInput,
    context: str
) -> str:
    """
    Build prompt for medication recommendation.

    Args:
        patient_input: Patient information
        context: Retrieved medical context

    Returns:
        Complete prompt string
    """
    # Format symptoms
    symptoms_text = ", ".join([
        f"{s.name} (severity {s.severity}/10, {s.duration_days} days)"
        for s in patient_input.symptoms
    ])

    # Format chronic conditions
    conditions_text = ", ".join(patient_input.chronic_conditions) if patient_input.chronic_conditions else "None"

    # Format current medications
    medications_text = ", ".join(patient_input.current_medications) if patient_input.current_medications else "None"

    # Format allergies
    allergies_text = ", ".join(patient_input.allergies) if patient_input.allergies else "None"

    prompt = f"""{SYSTEM_PROMPT}

PATIENT INFORMATION:
- Age: {patient_input.age} years old
- Gender: {patient_input.gender}
- Symptoms: {symptoms_text}
- Chronic Conditions: {conditions_text}
- Current Medications: {medications_text}
- Allergies: {allergies_text}

RETRIEVED MEDICAL EVIDENCE:
{context}

INSTRUCTIONS:
Based on the patient information and medical evidence above, provide medication recommendations.

For each medication, you MUST include:
1. Medication name
2. Specific dosage (e.g., "500mg")
3. Frequency (e.g., "twice daily")
4. Duration (e.g., "7 days", "ongoing")
5. Evidence source IDs from the context above (e.g., "DrugBank_DB00123", "MIMIC_12345")
6. Brief reasoning for why this medication is appropriate

IMPORTANT SAFETY CONSIDERATIONS:
- Avoid medications that interact with current medications
- Avoid medications that may trigger listed allergies
- Consider age-appropriate dosing
- Consider chronic conditions

RESPONSE FORMAT (JSON):
Return your response as valid JSON with this structure:
{{
  "recommendations": [
    {{
      "name": "medication_name",
      "dosage": "specific_amount",
      "frequency": "how_often",
      "duration": "how_long",
      "evidence_ids": ["source_id_1", "source_id_2"],
      "reasoning": "brief_explanation"
    }}
  ],
  "warnings": ["any_safety_warnings"],
  "confidence": "high|medium|low"
}}

RESPONSE:"""

    return prompt


def extract_json_from_response(response_text: str) -> Dict:
    """
    Extract JSON from LLM response.

    Handles cases where LLM includes markdown code blocks or extra text.

    Args:
        response_text: Raw LLM response

    Returns:
        Parsed JSON dictionary

    Raises:
        ValueError: If JSON cannot be extracted
    """
    import json
    import re

    # Try to find JSON in code blocks first
    json_match = re.search(r'```(?:json)?\s*(\{.*?\})\s*```', response_text, re.DOTALL)
    if json_match:
        json_str = json_match.group(1)
    else:
        # Try to find JSON anywhere in response
        json_match = re.search(r'\{.*\}', response_text, re.DOTALL)
        if json_match:
            json_str = json_match.group(0)
        else:
            raise ValueError("No JSON found in response")

    try:
        return json.loads(json_str)
    except json.JSONDecodeError as e:
        raise ValueError(f"Invalid JSON: {e}")


# Template for simple template-based fallback (no LLM)
def build_template_response(context: str, patient_input: PatientInput) -> Dict:
    """
    Build intelligent template-based response without LLM.

    Extracts medication names and info from retrieved documents,
    tailored to patient symptoms and conditions.

    Args:
        context: Retrieved medical context (may contain full prompt)
        patient_input: Patient information

    Returns:
        Template response dictionary customized for patient
    """
    import re
    import json

    # Extended list of common drugs with symptoms they treat
    drug_symptom_map = {
        # Pain/Headache
        "Acetaminophen": ["pain", "headache", "fever", "ache"],
        "Ibuprofen": ["pain", "headache", "inflammation", "fever", "arthritis"],
        "Aspirin": ["pain", "headache", "chest pain", "heart attack"],
        "Naproxen": ["pain", "inflammation", "arthritis"],

        # Dizziness/Vertigo
        "Meclizine": ["dizziness", "vertigo", "nausea", "motion sickness"],
        "Dimenhydrinate": ["dizziness", "vertigo", "nausea"],
        "Metoclopramide": ["nausea", "dizziness", "vomiting"],

        # Infection
        "Amoxicillin": ["infection", "bacterial", "throat", "pneumonia", "ear infection"],
        "Azithromycin": ["infection", "pneumonia", "bronchitis", "throat"],
        "Cephalexin": ["infection", "bacterial", "skin infection"],

        # Respiratory
        "Albuterol": ["cough", "asthma", "wheezing", "shortness of breath", "respiratory"],
        "Omeprazole": ["acid", "reflux", "gerd", "heartburn"],

        # Allergy/Cold
        "Diphenhydramine": ["allergy", "cold", "cough", "histamine"],
        "Loratadine": ["allergy", "runny nose", "sneezing"],
        "Cetirizine": ["allergy", "histamine"],

        # Diabetes/Metabolic
        "Metformin": ["diabetes", "blood sugar", "glucose"],
        "Glipizide": ["diabetes", "type 2"],

        # Cardiovascular
        "Lisinopril": ["hypertension", "blood pressure", "heart", "cardiac"],
        "Metoprolol": ["hypertension", "heart"],
        "Atorvastatin": ["cholesterol", "lipid", "cardiovascular"],
        "Amlodipine": ["hypertension", "angina"],

        # Mental Health
        "Sertraline": ["depression", "anxiety", "ssri"],
        "Fluoxetine": ["depression", "anxiety", "ocd"],

        # Thyroid
        "Levothyroxine": ["thyroid", "hypothyroidism"],
    }

    # Get primary symptom from patient input
    primary_symptom = patient_input.symptoms[0].name.lower() if patient_input.symptoms else "general"

    # Find drugs that match the primary symptom
    matching_drugs = []
    for drug, symptoms in drug_symptom_map.items():
        if any(sym in primary_symptom for sym in symptoms):
            matching_drugs.append(drug)

    # Also check context for drug mentions
    drugs_from_context = []
    common_drugs = list(drug_symptom_map.keys())

    for drug in common_drugs:
        if drug.lower() in context.lower():
            if drug not in matching_drugs:
                drugs_from_context.append(drug)

    # Combine: symptom-matched drugs first, then context drugs
    drugs = matching_drugs if matching_drugs else drugs_from_context

    # If no matches, use a safe default based on symptom
    if not drugs:
        if "dizziness" in primary_symptom.lower() or "vertigo" in primary_symptom.lower():
            drugs = ["Meclizine"]
        elif "infection" in primary_symptom.lower():
            drugs = ["Amoxicillin"]
        elif "cough" in primary_symptom.lower():
            drugs = ["Albuterol"]
        else:
            drugs = ["Acetaminophen"]  # Ultimate fallback

    # Limit to 5 recommendations
    drugs = drugs[:5]

    # Build recommendations tailored to patient
    recommendations = []

    age = patient_input.age
    gender = patient_input.gender

    # Determine dosage scale based on age
    if age < 18:
        dosage_scale = "pediatric"
    elif age > 65:
        dosage_scale = "elderly"
    else:
        dosage_scale = "standard"

    # Comprehensive dosages by drug and age group
    dosage_map = {
        "Acetaminophen": {"standard": "500-1000mg", "pediatric": "10-15mg/kg", "elderly": "650mg"},
        "Ibuprofen": {"standard": "200-400mg", "pediatric": "5-10mg/kg", "elderly": "200-400mg"},
        "Aspirin": {"standard": "325-500mg", "pediatric": "5-10mg/kg", "elderly": "81mg"},
        "Naproxen": {"standard": "250-500mg", "pediatric": "Not recommended", "elderly": "250mg"},
        "Metformin": {"standard": "500-2000mg", "pediatric": "Not recommended", "elderly": "500-1000mg"},
        "Lisinopril": {"standard": "10mg", "pediatric": "0.07mg/kg", "elderly": "5mg"},
        "Metoprolol": {"standard": "50-100mg", "pediatric": "0.5-1mg/kg", "elderly": "25-50mg"},
        "Atorvastatin": {"standard": "10-80mg", "pediatric": "Not recommended", "elderly": "10-40mg"},
        "Sertraline": {"standard": "50-200mg", "pediatric": "25-200mg", "elderly": "50mg"},
        "Albuterol": {"standard": "2-4 puffs", "pediatric": "1-2 puffs", "elderly": "1-2 puffs"},
        "Amoxicillin": {"standard": "500-875mg", "pediatric": "12.5-25mg/kg", "elderly": "500mg"},
        "Meclizine": {"standard": "25-50mg", "pediatric": "12.5-25mg", "elderly": "25mg"},
        "Omeprazole": {"standard": "20-40mg", "pediatric": "0.3-0.6mg/kg", "elderly": "20mg"},
    }

    for i, drug in enumerate(drugs):
        # Get appropriate dosage
        dosage = dosage_map.get(drug, {}).get(dosage_scale, "as directed by physician")

        # Determine frequency and duration based on drug and symptom
        if any(word in primary_symptom.lower() for word in ["pain", "headache", "fever"]):
            frequency = "every 4-6 hours as needed"
            duration = "until symptoms resolve (max 7-10 days)"
        elif any(word in primary_symptom.lower() for word in ["infection", "bacterial"]):
            frequency = "as prescribed"
            duration = "complete full course (typically 7-10 days)"
        elif any(word in primary_symptom.lower() for word in ["dizziness", "vertigo"]):
            frequency = "every 4-6 hours as needed"
            duration = "until symptoms resolve"
        elif any(word in primary_symptom.lower() for word in ["cough", "respiratory", "asthma"]):
            frequency = "as needed (typically 4-6 times daily)"
            duration = "until symptoms resolve or as prescribed"
        elif any(cond.lower() in str(patient_input.chronic_conditions).lower() for cond in ["diabetes", "hypertension", "thyroid"]):
            frequency = "once daily"
            duration = "ongoing, as prescribed"
        else:
            frequency = "as needed or as prescribed"
            duration = "per physician guidance"

        recommendations.append({
            "name": drug,
            "dosage": dosage,
            "frequency": frequency,
            "duration": duration,
            "evidence_ids": [],  # Empty - will use retrieved evidence instead
            "reasoning": f"Based on retrieved medical literature for {primary_symptom} in {age} year old {gender}. Always consult physician for personalized dosing."
        })

    # Generate warnings based on patient profile
    warnings = ["⚠️ Template-based recommendation (LLM unavailable - using safe fallback)"]

    if patient_input.allergies:
        warnings.append(f"Patient has allergies: {', '.join(patient_input.allergies)}")

    if patient_input.chronic_conditions:
        warnings.append(f"Patient has chronic conditions: {', '.join(patient_input.chronic_conditions)}")

    if patient_input.current_medications:
        warnings.append(f"Check interactions with current medications: {', '.join(patient_input.current_medications)}")

    warnings.append("Please consult a healthcare provider before taking any medication.")

    return {
        "recommendations": recommendations,
        "warnings": warnings,
        "confidence": "low"
    }
