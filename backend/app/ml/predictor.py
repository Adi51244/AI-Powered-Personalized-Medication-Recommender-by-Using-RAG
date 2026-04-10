"""
Runtime ML predictor service for disease predictions.
"""

from __future__ import annotations

import json
import logging
import pickle
from pathlib import Path
from typing import Dict, List, Optional

import joblib
import numpy as np

from app.ml.feature_engineering import FeatureExtractor
from app.models.schemas import DiseasePrediction, PatientInput


logger = logging.getLogger(__name__)


class MLPredictor:
    """Singleton predictor using soft-voting over available ML models."""

    _instance: Optional["MLPredictor"] = None

    DEFAULT_WEIGHTS: Dict[str, float] = {
        "random_forest": 0.4,
        "xgboost": 0.4,
        "svm": 0.2,
    }

    def __init__(self):
        self.models: Dict[str, object] = {}
        self.label_encoder = None
        self.feature_extractor: Optional[FeatureExtractor] = None
        self.loaded = False
        self.model_metadata: Dict = {}
        self.ensemble_weights: Dict[str, float] = self.DEFAULT_WEIGHTS.copy()  # Will be updated if available

    @classmethod
    def get_instance(cls) -> "MLPredictor":
        if cls._instance is None:
            cls._instance = cls()
        return cls._instance

    def load_models(self, models_path: str | Path, artifacts_path: str | Path = "data/ml") -> None:
        """
        Load available models and required artifacts.

        Args:
            models_path: Directory containing model .pkl files.
            artifacts_path: Directory containing feature_extractor/label_encoder artifacts.
        """
        models_dir = Path(models_path)
        artifacts_dir = Path(artifacts_path)

        self.models = {}
        model_files = {
            "random_forest": models_dir / "random_forest.pkl",
            "xgboost": models_dir / "xgboost.pkl",
            "svm": models_dir / "svm.pkl",
        }
        for model_name, path in model_files.items():
            if path.exists():
                self.models[model_name] = joblib.load(path)
                logger.info("Loaded ML model: %s", model_name)
            else:
                logger.warning("Model artifact missing, skipping %s: %s", model_name, path)

        if not self.models:
            raise RuntimeError(f"No ML model artifacts were loaded from {models_dir}")

        label_encoder_path = models_dir / "label_encoder.pkl"
        if not label_encoder_path.exists():
            label_encoder_path = artifacts_dir / "label_encoder.pkl"
        if not label_encoder_path.exists():
            raise FileNotFoundError("Label encoder not found in models_path or artifacts_path")

        with label_encoder_path.open("rb") as handle:
            self.label_encoder = pickle.load(handle)

        extractor_path = models_dir / "feature_extractor.pkl"
        if not extractor_path.exists():
            extractor_path = artifacts_dir / "feature_extractor.pkl"
        if not extractor_path.exists():
            raise FileNotFoundError("Feature extractor not found in models_path or artifacts_path")

        self.feature_extractor = FeatureExtractor.load(str(extractor_path))

        metadata_path = models_dir / "model_metadata.json"
        if metadata_path.exists():
            with metadata_path.open("r", encoding="utf-8") as handle:
                self.model_metadata = json.load(handle)
        
        # Load optimized ensemble weights if available
        metrics_path = models_dir / "evaluation_metrics.json"
        if metrics_path.exists():
            with metrics_path.open("r", encoding="utf-8") as handle:
                metrics = json.load(handle)
                if "ensemble" in metrics and "weights" in metrics["ensemble"]:
                    self.ensemble_weights = metrics["ensemble"]["weights"]
                    logger.info("Loaded optimized ensemble weights: %s", self.ensemble_weights)
                else:
                    logger.info("Using default ensemble weights (optimized weights not found in metrics)")
        else:
            logger.info("Using default ensemble weights (evaluation metrics file not found)")

        self.loaded = True
        logger.info("MLPredictor loaded with %s model(s)", len(self.models))

    def predict_from_patient(self, patient_input: PatientInput, top_k: int = 5) -> List[DiseasePrediction]:
        if not self.loaded or self.feature_extractor is None:
            raise RuntimeError("MLPredictor is not loaded")

        features = self.feature_extractor.transform(patient_input)
        return self.predict(features, top_k=top_k)

    def predict(self, features: np.ndarray, top_k: int = 5) -> List[DiseasePrediction]:
        if not self.loaded:
            raise RuntimeError("MLPredictor is not loaded")
        if self.label_encoder is None:
            raise RuntimeError("Label encoder is not loaded")

        if features.ndim == 1:
            features = features.reshape(1, -1)

        model_probs: Dict[str, np.ndarray] = {}
        for name, model in self.models.items():
            probs = model.predict_proba(features)[0]
            model_probs[name] = probs

        ensemble_probs = self._ensemble_vote(model_probs)
        sorted_indices = np.argsort(ensemble_probs)[::-1][: max(1, top_k)]

        predictions: List[DiseasePrediction] = []
        for idx in sorted_indices:
            disease_name = str(self.label_encoder.classes_[idx])
            confidence = float(ensemble_probs[idx])
            predictions.append(
                DiseasePrediction(
                    disease=disease_name,
                    confidence=confidence,
                    source="ml_ensemble",
                    explanation=self._build_explanation(model_probs, idx),
                )
            )

        return predictions

    def _ensemble_vote(self, model_probs: Dict[str, np.ndarray]) -> np.ndarray:
        if not model_probs:
            raise RuntimeError("No model probabilities available")

        available_weights = {name: self.ensemble_weights.get(name, 0.0) for name in model_probs}
        total = sum(available_weights.values())
        if total <= 0.0:
            raise RuntimeError("Invalid ensemble weights")
        normalized = {name: weight / total for name, weight in available_weights.items()}

        first_shape = next(iter(model_probs.values())).shape
        ensemble = np.zeros(first_shape, dtype=np.float64)
        for name, probs in model_probs.items():
            if probs.shape != first_shape:
                raise RuntimeError("Inconsistent class probability shapes across models")
            ensemble += normalized[name] * probs

        summed = np.sum(ensemble)
        if summed > 0:
            ensemble /= summed

        return ensemble.astype(np.float32)

    @staticmethod
    def _build_explanation(model_probs: Dict[str, np.ndarray], class_index: int) -> str:
        parts = []
        for model_name, probs in model_probs.items():
            parts.append(f"{model_name}={probs[class_index]:.3f}")
        return "Ensemble probabilities: " + ", ".join(parts)
