"""
Feature Engineering for ML Disease Prediction.

This module converts patient data (symptoms, demographics, medical history)
into numerical feature vectors suitable for machine learning models.
"""

import numpy as np
import logging
from typing import List, Dict, Optional, Tuple
from dataclasses import dataclass
import pickle
from pathlib import Path

from sklearn.preprocessing import StandardScaler, LabelEncoder
from sklearn.feature_extraction.text import TfidfVectorizer

from app.models.schemas import PatientInput

logger = logging.getLogger(__name__)


@dataclass
class FeatureConfig:
    """Configuration for feature extraction."""
    # Symptom encoding
    max_symptoms: int = 50  # Top 50 most common symptoms
    use_tfidf_symptoms: bool = False  # Use TF-IDF vs one-hot

    # Age normalization
    age_min: float = 0.0
    age_max: float = 120.0

    # Feature dimensions
    n_symptom_features: int = 50
    n_condition_features: int = 30
    n_medication_features: int = 20
    n_allergy_features: int = 10
    
    # Text TF-IDF features
    use_text_tfidf: bool = True
    tfidf_max_features: int = 30  # Top 30 TF-IDF features from clinical text

    # Total features: demographics (3) + symptoms (50*3) + conditions (30) + meds (20) + allergies (10) + text_tfidf (30) = ~243


class FeatureExtractor:
    """
    Extract numerical features from patient data for ML models.

    Features extracted:
    - Demographics: age (normalized), gender (one-hot)
    - Symptoms: name (one-hot/TF-IDF), severity, duration
    - Chronic conditions: one-hot encoding
    - Medications: count, one-hot encoding
    - Allergies: count, one-hot encoding
    """

    def __init__(self, config: Optional[FeatureConfig] = None):
        """
        Initialize feature extractor.

        Args:
            config: Feature extraction configuration
        """
        self.config = config or FeatureConfig()

        # Vocabulary mappings (populated during fit)
        self.symptom_vocab: Dict[str, int] = {}
        self.condition_vocab: Dict[str, int] = {}
        self.medication_vocab: Dict[str, int] = {}
        self.allergy_vocab: Dict[str, int] = {}

        # Gender encoding
        self.gender_encoder = LabelEncoder()
        self.gender_encoder.fit(['male', 'female', 'other'])

        # Scalers
        self.age_scaler = StandardScaler()
        
        # TF-IDF vectorizer for clinical text
        self.tfidf_vectorizer: Optional[TfidfVectorizer] = None

        # Feature names (for interpretability)
        self.feature_names: List[str] = []

        # Fitted flag
        self.is_fitted = False

        logger.info("FeatureExtractor initialized")

    def fit(self, patients: List[Dict]) -> 'FeatureExtractor':
        """
        Fit the feature extractor on training data.

        Learns vocabularies for symptoms, conditions, medications, allergies
        and TF-IDF vectorizer from the training dataset.

        Args:
            patients: List of patient dictionaries (from MIMIC JSONL)
                Each dict should have: symptoms, chronic_conditions, allergies, age

        Returns:
            self (fitted)
        """
        logger.info(f"Fitting feature extractor on {len(patients)} patients")

        # Collect all unique values
        all_symptoms = []
        all_conditions = []
        all_medications = []
        all_allergies = []
        all_ages = []
        all_texts = []

        for patient in patients:
            # Symptoms
            if 'symptoms' in patient:
                for symptom in patient['symptoms']:
                    symptom_name = self._normalize_text(symptom.get('name', ''))
                    if symptom_name:
                        all_symptoms.append(symptom_name)

            # Chronic conditions
            if 'chronic_conditions' in patient:
                for condition in patient['chronic_conditions']:
                    cond_name = self._normalize_text(condition)
                    if cond_name:
                        all_conditions.append(cond_name)

            # Medications
            if 'current_medications' in patient:
                for med in patient['current_medications']:
                    med_name = self._normalize_text(med)
                    if med_name:
                        all_medications.append(med_name)

            # Allergies
            if 'allergies' in patient:
                for allergy in patient['allergies']:
                    allergy_name = self._normalize_text(allergy)
                    if allergy_name:
                        all_allergies.append(allergy_name)

            # Age
            if 'age' in patient:
                all_ages.append(patient['age'])
            
            # Text for TF-IDF (from clinical notes field if available)
            if 'text' in patient:
                text = str(patient['text']).lower()
                all_texts.append(text)
            elif 'chief_complaint' in patient:
                text = str(patient.get('chief_complaint', '')).lower()
                all_texts.append(text)
            else:
                all_texts.append("")

        # Build vocabularies (top-K most frequent)
        self.symptom_vocab = self._build_vocab(all_symptoms, self.config.n_symptom_features)
        self.condition_vocab = self._build_vocab(all_conditions, self.config.n_condition_features)
        self.medication_vocab = self._build_vocab(all_medications, self.config.n_medication_features)
        self.allergy_vocab = self._build_vocab(all_allergies, self.config.n_allergy_features)

        # Fit age scaler
        if all_ages:
            self.age_scaler.fit(np.array(all_ages).reshape(-1, 1))
        
        # Fit TF-IDF vectorizer on clinical text
        if self.config.use_text_tfidf and all_texts:
            self.tfidf_vectorizer = TfidfVectorizer(
                max_features=self.config.tfidf_max_features,
                ngram_range=(1, 2),
                stop_words='english',
                min_df=2,
                max_df=0.9,
            )
            self.tfidf_vectorizer.fit(all_texts)
            logger.info(f"TF-IDF vectorizer fitted with {len(self.tfidf_vectorizer.vocabulary_)} terms")

        # Build feature names
        self._build_feature_names()

        self.is_fitted = True

        logger.info(f"Feature extractor fitted:")
        logger.info(f"  - {len(self.symptom_vocab)} symptoms")
        logger.info(f"  - {len(self.condition_vocab)} conditions")
        logger.info(f"  - {len(self.medication_vocab)} medications")
        logger.info(f"  - {len(self.allergy_vocab)} allergies")
        logger.info(f"  - Total features: {len(self.feature_names)}")

        return self

    def transform(self, patient_input: PatientInput, text_content: str = "") -> np.ndarray:
        """
        Transform patient input into feature vector.

        Args:
            patient_input: Patient data (Pydantic model)
            text_content: Optional clinical text for TF-IDF features

        Returns:
            Feature vector (1D numpy array)

        Raises:
            RuntimeError: If extractor not fitted
        """
        if not self.is_fitted:
            raise RuntimeError("FeatureExtractor must be fitted before transform")

        features = []

        # 1. Demographics
        features.extend(self._extract_demographic_features(patient_input))

        # 2. Symptoms
        features.extend(self._extract_symptom_features(patient_input))

        # 3. Chronic conditions
        features.extend(self._extract_condition_features(patient_input))

        # 4. Medications
        features.extend(self._extract_medication_features(patient_input))

        # 5. Allergies
        features.extend(self._extract_allergy_features(patient_input))
        
        # 6. Text TF-IDF features
        if self.config.use_text_tfidf and self.tfidf_vectorizer:
            features.extend(self._extract_tfidf_features(text_content))

        return np.array(features, dtype=np.float32)

    def fit_transform(self, patients: List[Dict]) -> np.ndarray:
        """
        Fit extractor and transform training data.

        Args:
            patients: List of patient dictionaries

        Returns:
            Feature matrix (2D numpy array, shape [n_patients, n_features])
        """
        self.fit(patients)

        # Convert dicts to PatientInput objects and transform
        feature_vectors = []
        for patient in patients:
            try:
                patient_input = self._dict_to_patient_input(patient)
                # Extract text content for TF-IDF
                text_content = self._extract_text_from_patient(patient)
                features = self.transform(patient_input, text_content)
                feature_vectors.append(features)
            except Exception as e:
                logger.warning(f"Failed to extract features: {e}")
                # Skip invalid patients

        return np.array(feature_vectors, dtype=np.float32)

    def _extract_demographic_features(self, patient: PatientInput) -> List[float]:
        """Extract demographic features: age (normalized), gender (one-hot)."""
        features = []

        # Age (normalized)
        age_normalized = self.age_scaler.transform([[patient.age]])[0][0]
        features.append(age_normalized)

        # Gender (one-hot: male=1,0,0, female=0,1,0, other=0,0,1)
        try:
            gender_idx = self.gender_encoder.transform([patient.gender])[0]
            gender_onehot = [0.0] * len(self.gender_encoder.classes_)
            gender_onehot[gender_idx] = 1.0
            features.extend(gender_onehot)
        except ValueError:
            # Unknown gender, all zeros
            features.extend([0.0] * len(self.gender_encoder.classes_))

        return features

    def _extract_symptom_features(self, patient: PatientInput) -> List[float]:
        """Extract symptom features: one-hot + severity + duration."""
        features = []

        # One-hot encoding for symptom presence
        symptom_onehot = [0.0] * len(self.symptom_vocab)
        symptom_severity = [0.0] * len(self.symptom_vocab)
        symptom_duration = [0.0] * len(self.symptom_vocab)

        for symptom in patient.symptoms:
            symptom_name = self._normalize_text(symptom.name)
            if symptom_name in self.symptom_vocab:
                idx = self.symptom_vocab[symptom_name]
                symptom_onehot[idx] = 1.0
                symptom_severity[idx] = symptom.severity / 10.0  # Normalize to [0, 1]
                symptom_duration[idx] = min(symptom.duration_days / 30.0, 1.0)  # Cap at 30 days

        features.extend(symptom_onehot)
        features.extend(symptom_severity)
        features.extend(symptom_duration)

        return features

    def _extract_condition_features(self, patient: PatientInput) -> List[float]:
        """Extract chronic condition features: one-hot encoding."""
        features = []

        # One-hot encoding
        condition_onehot = [0.0] * len(self.condition_vocab)

        for condition in patient.chronic_conditions:
            condition_name = self._normalize_text(condition)
            if condition_name in self.condition_vocab:
                idx = self.condition_vocab[condition_name]
                condition_onehot[idx] = 1.0

        features.extend(condition_onehot)

        # Count of conditions (additional feature)
        features.append(len(patient.chronic_conditions) / 10.0)  # Normalize

        return features

    def _extract_medication_features(self, patient: PatientInput) -> List[float]:
        """Extract medication features: one-hot encoding + count."""
        features = []

        # One-hot encoding
        medication_onehot = [0.0] * len(self.medication_vocab)

        for med in patient.current_medications:
            med_name = self._normalize_text(med)
            if med_name in self.medication_vocab:
                idx = self.medication_vocab[med_name]
                medication_onehot[idx] = 1.0

        features.extend(medication_onehot)

        # Count of medications (additional feature)
        features.append(len(patient.current_medications) / 20.0)  # Normalize

        return features

    def _extract_allergy_features(self, patient: PatientInput) -> List[float]:
        """Extract allergy features: one-hot encoding + count."""
        features = []

        # One-hot encoding
        allergy_onehot = [0.0] * len(self.allergy_vocab)

        for allergy in patient.allergies:
            allergy_name = self._normalize_text(allergy)
            if allergy_name in self.allergy_vocab:
                idx = self.allergy_vocab[allergy_name]
                allergy_onehot[idx] = 1.0

        features.extend(allergy_onehot)

        # Count of allergies (additional feature)
        features.append(len(patient.allergies) / 10.0)  # Normalize

        return features
    
    def _extract_tfidf_features(self, text_content: str) -> List[float]:
        """
        Extract TF-IDF features from clinical text.
        
        Args:
            text_content: Clinical text to vectorize
            
        Returns:
            List of TF-IDF features (dense array)
        """
        if not self.tfidf_vectorizer:
            return []
        
        # Handle empty text
        if not text_content or not text_content.strip():
            return [0.0] * self.config.tfidf_max_features
        
        # Transform text and convert sparse to dense
        tfidf_sparse = self.tfidf_vectorizer.transform([text_content])
        tfidf_dense = tfidf_sparse.toarray().flatten()
        
        # Ensure we have exactly max_features dimensions
        if len(tfidf_dense) < self.config.tfidf_max_features:
            # Pad with zeros
            tfidf_dense = np.pad(tfidf_dense, (0, self.config.tfidf_max_features - len(tfidf_dense)))
        else:
            # Truncate if needed (shouldn't happen with max_features param)
            tfidf_dense = tfidf_dense[:self.config.tfidf_max_features]
        
        return tfidf_dense.tolist()
    
    def _extract_text_from_patient(self, patient_dict: Dict) -> str:
        """
        Extract clinical text from patient dictionary for TF-IDF.
        
        Tries multiple fields in order of preference: text, chief_complaint, history, etc.
        
        Args:
            patient_dict: Patient data dictionary
            
        Returns:
            Combined clinical text
        """
        texts = []
        
        # Try various text fields in order of preference
        if 'text' in patient_dict and patient_dict['text']:
            texts.append(str(patient_dict['text']))
        
        if 'chief_complaint' in patient_dict and patient_dict['chief_complaint']:
            texts.append(str(patient_dict['chief_complaint']))
        
        if 'history' in patient_dict and patient_dict['history']:
            texts.append(str(patient_dict['history']))
        
        # Combine all available text
        combined_text = " ".join(texts)
        return combined_text.lower()

    def save(self, path: str):
        """
        Save fitted feature extractor to disk.

        Args:
            path: File path to save to
        """
        if not self.is_fitted:
            raise RuntimeError("Cannot save unfitted feature extractor")

        path = Path(path)
        path.parent.mkdir(parents=True, exist_ok=True)

        with open(path, 'wb') as f:
            pickle.dump(self, f)

        logger.info(f"Feature extractor saved to {path}")
    
    def _build_vocab(self, items: List[str], max_items: int) -> Dict[str, int]:
        """
        Build vocabulary from list of items (top-K most frequent).

        Args:
            items: List of items (symptoms, conditions, etc.)
            max_items: Maximum vocabulary size

        Returns:
            Dictionary mapping item to index
        """
        from collections import Counter

        # Count frequencies
        counter = Counter(items)

        # Get top-K most common
        most_common = counter.most_common(max_items)

        # Build vocabulary
        vocab = {item: idx for idx, (item, count) in enumerate(most_common)}

        return vocab

    def _normalize_text(self, text: str) -> str:
        """Normalize text (lowercase, strip, etc.)."""
        if not text:
            return ""
        return text.lower().strip()

    def _build_feature_names(self):
        """Build feature names for interpretability."""
        names = []

        # Demographics
        names.append("age_normalized")
        for gender in self.gender_encoder.classes_:
            names.append(f"gender_{gender}")

        # Symptoms (presence, severity, duration)
        for symptom in sorted(self.symptom_vocab.keys()):
            names.append(f"symptom_{symptom}_present")
        for symptom in sorted(self.symptom_vocab.keys()):
            names.append(f"symptom_{symptom}_severity")
        for symptom in sorted(self.symptom_vocab.keys()):
            names.append(f"symptom_{symptom}_duration")

        # Conditions
        for condition in sorted(self.condition_vocab.keys()):
            names.append(f"condition_{condition}")
        names.append("condition_count")

        # Medications
        for medication in sorted(self.medication_vocab.keys()):
            names.append(f"medication_{medication}")
        names.append("medication_count")

        # Allergies
        for allergy in sorted(self.allergy_vocab.keys()):
            names.append(f"allergy_{allergy}")
        names.append("allergy_count")
        
        # Text TF-IDF features
        if self.config.use_text_tfidf and self.tfidf_vectorizer:
            for term in sorted(self.tfidf_vectorizer.get_feature_names_out()):
                names.append(f"tfidf_{term}")

        self.feature_names = names

    def _dict_to_patient_input(self, patient_dict: Dict) -> PatientInput:
        """
        Convert patient dictionary to PatientInput Pydantic model.

        Args:
            patient_dict: Patient data dictionary

        Returns:
            PatientInput object
        """
        from app.models.schemas import SymptomInput

        # Extract symptoms
        symptoms = []
        if 'symptoms' in patient_dict:
            for s in patient_dict['symptoms']:
                if isinstance(s, dict):
                    symptoms.append(SymptomInput(
                        name=s.get('name', 'unknown'),
                        severity=s.get('severity', 5),
                        duration_days=s.get('duration_days', 1)
                    ))

        # If no symptoms, add placeholder
        if not symptoms:
            symptoms.append(SymptomInput(name="general", severity=5, duration_days=1))

        # Create PatientInput
        return PatientInput(
            age=patient_dict.get('age', 50),
            gender=patient_dict.get('gender', 'other'),
            symptoms=symptoms,
            chronic_conditions=patient_dict.get('chronic_conditions', []),
            current_medications=patient_dict.get('current_medications', []),
            allergies=patient_dict.get('allergies', [])
        )

    def save(self, path: str):
        """
        Save fitted feature extractor to disk.

        Args:
            path: File path to save to
        """
        if not self.is_fitted:
            raise RuntimeError("Cannot save unfitted feature extractor")

        path = Path(path)
        path.parent.mkdir(parents=True, exist_ok=True)

        with open(path, 'wb') as f:
            pickle.dump(self, f)

        logger.info(f"Feature extractor saved to {path}")

    @classmethod
    def load(cls, path: str) -> 'FeatureExtractor':
        """
        Load fitted feature extractor from disk.

        Args:
            path: File path to load from

        Returns:
            Fitted FeatureExtractor
        """
        with open(path, 'rb') as f:
            extractor = pickle.load(f)

        if not extractor.is_fitted:
            raise RuntimeError("Loaded feature extractor is not fitted")

        logger.info(f"Feature extractor loaded from {path}")
        return extractor

    def get_feature_importance_names(self, importances: np.ndarray, top_k: int = 10) -> List[Tuple[str, float]]:
        """
        Get human-readable feature importance names.

        Args:
            importances: Feature importance scores from model
            top_k: Number of top features to return

        Returns:
            List of (feature_name, importance) tuples
        """
        if len(importances) != len(self.feature_names):
            raise ValueError(f"Importance array length ({len(importances)}) doesn't match features ({len(self.feature_names)})")

        # Sort by importance
        indices = np.argsort(importances)[::-1][:top_k]

        return [(self.feature_names[i], importances[i]) for i in indices]
