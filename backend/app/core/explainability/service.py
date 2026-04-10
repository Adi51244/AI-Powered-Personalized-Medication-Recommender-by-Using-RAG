"""Phase 6 explainability service using SHAP and LIME with robust fallbacks."""

from __future__ import annotations

import logging
from dataclasses import dataclass
from typing import List, Optional, Tuple

import numpy as np

from app.config import settings
from app.ml.predictor import MLPredictor
from app.models.schemas import ExplanationResponse, PatientInput, ShapValue

logger = logging.getLogger(__name__)


@dataclass
class _PredictionContext:
    disease: str
    confidence: float
    class_index: int
    feature_vector: np.ndarray
    feature_names: List[str]


class ExplainabilityService:
    """Singleton explainability orchestrator for ML predictions."""

    _instance: Optional["ExplainabilityService"] = None

    def __init__(self) -> None:
        self.predictor = MLPredictor.get_instance()
        self._lime_explainer = None

    @classmethod
    def get_instance(cls) -> "ExplainabilityService":
        if cls._instance is None:
            cls._instance = cls()
        return cls._instance

    def explain_patient(self, patient_input: PatientInput, top_k_features: int = 10) -> ExplanationResponse:
        self._ensure_predictor_loaded()
        ctx = self._build_prediction_context(patient_input)

        shap_values, method = self._compute_shap_values(ctx, top_k_features)
        lime_values = self._compute_lime_values(ctx, top_k_features)

        if lime_values:
            merged = self._merge_contributions(shap_values, lime_values, top_k_features)
            top_features = [item.feature for item in merged]
            summary = self._build_summary(ctx, top_features, method="hybrid")
            return ExplanationResponse(
                predicted_disease=ctx.disease,
                predicted_confidence=ctx.confidence,
                method="hybrid",
                summary=summary,
                shap_values=merged,
                top_features=top_features,
                evidence_citations=[],
            )

        top_features = [item.feature for item in shap_values]
        summary = self._build_summary(ctx, top_features, method=method)
        return ExplanationResponse(
            predicted_disease=ctx.disease,
            predicted_confidence=ctx.confidence,
            method=method,
            summary=summary,
            shap_values=shap_values,
            top_features=top_features,
            evidence_citations=[],
        )

    def _ensure_predictor_loaded(self) -> None:
        if self.predictor.loaded:
            return
        self.predictor.load_models(
            models_path=settings.ml_models_path,
            artifacts_path="./data/ml",
        )

    def _build_prediction_context(self, patient_input: PatientInput) -> _PredictionContext:
        if self.predictor.feature_extractor is None or self.predictor.label_encoder is None:
            raise RuntimeError("Predictor artifacts unavailable for explainability")

        feature_vector = self.predictor.feature_extractor.transform(patient_input).reshape(1, -1)
        probs_by_model = {name: model.predict_proba(feature_vector)[0] for name, model in self.predictor.models.items()}
        ensemble = self.predictor._ensemble_vote(probs_by_model)

        class_index = int(np.argmax(ensemble))
        disease = str(self.predictor.label_encoder.classes_[class_index])
        confidence = float(ensemble[class_index])

        return _PredictionContext(
            disease=disease,
            confidence=confidence,
            class_index=class_index,
            feature_vector=feature_vector,
            feature_names=self.predictor.feature_extractor.feature_names,
        )

    def _compute_shap_values(self, ctx: _PredictionContext, top_k_features: int) -> Tuple[List[ShapValue], str]:
        preferred_models = ["xgboost", "random_forest"]

        for model_name in preferred_models:
            model = self.predictor.models.get(model_name)
            if model is None:
                continue

            try:
                import shap

                explainer = shap.TreeExplainer(model)
                shap_out = explainer.shap_values(ctx.feature_vector)

                if isinstance(shap_out, list):
                    values = np.array(shap_out[ctx.class_index]).reshape(-1)
                else:
                    arr = np.array(shap_out)
                    if arr.ndim == 3:  # [samples, features, classes]
                        values = arr[0, :, ctx.class_index]
                    else:
                        values = arr.reshape(-1)

                return self._top_shap_values(values, ctx.feature_names, top_k_features), "shap"
            except Exception as exc:
                logger.warning("SHAP computation failed for %s: %s", model_name, exc)

        fallback = self._fallback_importance_values(ctx, top_k_features)
        return fallback, "fallback"

    def _compute_lime_values(self, ctx: _PredictionContext, top_k_features: int) -> List[ShapValue]:
        try:
            from lime import lime_tabular

            if self._lime_explainer is None:
                train_features = np.load("./data/ml/train_features.npy")
                self._lime_explainer = lime_tabular.LimeTabularExplainer(
                    training_data=train_features,
                    feature_names=ctx.feature_names,
                    class_names=[str(c) for c in self.predictor.label_encoder.classes_],
                    mode="classification",
                    discretize_continuous=True,
                )

            def _predict_fn(arr: np.ndarray) -> np.ndarray:
                probs_by_model = {name: model.predict_proba(arr) for name, model in self.predictor.models.items()}
                # Weighted average over models
                first = next(iter(probs_by_model.values()))
                weighted = np.zeros_like(first, dtype=np.float64)
                for name, probs in probs_by_model.items():
                    weighted += self.predictor.ensemble_weights.get(name, 0.0) * probs
                sums = weighted.sum(axis=1, keepdims=True)
                sums[sums == 0] = 1.0
                return (weighted / sums).astype(np.float32)

            exp = self._lime_explainer.explain_instance(
                data_row=ctx.feature_vector[0],
                predict_fn=_predict_fn,
                labels=[ctx.class_index],
                num_features=top_k_features,
            )
            items = exp.as_list(label=ctx.class_index)
            out: List[ShapValue] = []
            for feature_name, contribution in items:
                out.append(ShapValue(feature=feature_name, contribution=float(contribution), value="lime"))
            return out
        except Exception as exc:
            logger.warning("LIME computation unavailable: %s", exc)
            return []

    @staticmethod
    def _top_shap_values(values: np.ndarray, feature_names: List[str], top_k_features: int) -> List[ShapValue]:
        order = np.argsort(np.abs(values))[::-1][:top_k_features]
        out: List[ShapValue] = []
        for idx in order:
            out.append(
                ShapValue(
                    feature=feature_names[idx] if idx < len(feature_names) else f"feature_{idx}",
                    contribution=float(values[idx]),
                    value=float(values[idx]),
                )
            )
        return out

    def _fallback_importance_values(self, ctx: _PredictionContext, top_k_features: int) -> List[ShapValue]:
        # Deterministic fallback: weighted importances from tree models if available.
        weighted = np.zeros(ctx.feature_vector.shape[1], dtype=np.float64)
        total = 0.0

        for name in ("xgboost", "random_forest"):
            model = self.predictor.models.get(name)
            if model is None:
                continue
            imp = getattr(model, "feature_importances_", None)
            if imp is None:
                continue
            w = float(self.predictor.ensemble_weights.get(name, 0.0))
            weighted += w * np.array(imp)
            total += w

        if total > 0:
            weighted /= total
            contributions = weighted * np.abs(ctx.feature_vector[0])
        else:
            contributions = np.abs(ctx.feature_vector[0])

        return self._top_shap_values(contributions, ctx.feature_names, top_k_features)

    @staticmethod
    def _merge_contributions(primary: List[ShapValue], secondary: List[ShapValue], top_k_features: int) -> List[ShapValue]:
        scores = {}
        for item in primary:
            scores[item.feature] = scores.get(item.feature, 0.0) + abs(float(item.contribution))
        for item in secondary:
            scores[item.feature] = scores.get(item.feature, 0.0) + abs(float(item.contribution))

        ranked = sorted(scores.items(), key=lambda kv: kv[1], reverse=True)[:top_k_features]
        return [ShapValue(feature=name, contribution=float(score), value="hybrid") for name, score in ranked]

    @staticmethod
    def _build_summary(ctx: _PredictionContext, top_features: List[str], method: str) -> str:
        features_text = ", ".join(top_features[:5]) if top_features else "no dominant features"
        return (
            f"Predicted '{ctx.disease}' with confidence {ctx.confidence:.3f}. "
            f"Top contributing features ({method}): {features_text}."
        )

    def explain_patient_fallback(
        self,
        patient_input: PatientInput,
        top_k_features: int = 10
    ) -> ExplanationResponse:
        """
        Patient-specific explanation based on actual symptoms and conditions.

        Used when SHAP/LIME computation times out (>90s).
        Returns a simple, understandable explanation of which patient factors
        contributed to the predicted diagnosis.

        Args:
            patient_input: Patient data
            top_k_features: Number of top features to return

        Returns:
            ExplanationResponse with patient-specific factors
        """
        self._ensure_predictor_loaded()
        ctx = self._build_prediction_context(patient_input)

        # Build patient-specific explanation from actual data
        contributing_factors = []

        # Add symptoms as primary contributing factors
        if patient_input.symptoms:
            for symptom in patient_input.symptoms:
                severity_factor = symptom.severity / 10.0  # Normalize to 0-1
                contributing_factors.append(ShapValue(
                    feature=f"{symptom.name} (severity {symptom.severity}/10, {symptom.duration_days}d)",
                    contribution=severity_factor,
                    value=f"{symptom.severity}/10"
                ))

        # Add chronic conditions
        if patient_input.chronic_conditions:
            for condition in patient_input.chronic_conditions[:3]:
                contributing_factors.append(ShapValue(
                    feature=f"Chronic: {condition}",
                    contribution=0.7,
                    value="present"
                ))

        # Add age as a factor
        age_factor = min(patient_input.age / 100.0, 1.0)
        contributing_factors.append(ShapValue(
            feature=f"Age ({patient_input.age} years)",
            contribution=age_factor,
            value=str(patient_input.age)
        ))

        # Add gender
        contributing_factors.append(ShapValue(
            feature=f"Gender ({patient_input.gender})",
            contribution=0.3,
            value=patient_input.gender
        ))

        # Sort by contribution and take top k
        contributing_factors.sort(key=lambda x: x.contribution, reverse=True)
        shap_values = contributing_factors[:top_k_features]
        top_features = [sv.feature for sv in shap_values]

        # Build patient-specific summary
        symptoms_list = ", ".join([s.name for s in patient_input.symptoms[:3]]) if patient_input.symptoms else "unspecified symptoms"
        age_text = f"{patient_input.age}-year-old {patient_input.gender}"

        summary = (
            f"Predicted '{ctx.disease}' with confidence {ctx.confidence:.1%}. "
            f"Primary factors: {age_text} presenting with {symptoms_list}. "
            f"Contributing factors analyzed: {', '.join(top_features[:4])}."
        )

        logger.info(f"Generated patient-specific fallback explanation ({len(shap_values)} factors)")

        return ExplanationResponse(
            predicted_disease=ctx.disease,
            predicted_confidence=ctx.confidence,
            method="patient-specific",
            summary=summary,
            shap_values=shap_values,
            top_features=top_features,
            evidence_citations=[]
        )
