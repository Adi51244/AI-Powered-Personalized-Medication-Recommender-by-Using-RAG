"""
Random Forest model wrapper for disease classification.
"""

from __future__ import annotations

from pathlib import Path
from typing import Any, Dict, Optional

import joblib
import numpy as np
from sklearn.ensemble import RandomForestClassifier


class RandomForestModel:
    """Thin wrapper around sklearn RandomForestClassifier."""

    DEFAULT_PARAMS: Dict[str, Any] = {
        "n_estimators": 200,
        "max_depth": 20,
        "min_samples_split": 5,
        "min_samples_leaf": 2,
        "class_weight": "balanced",
        "n_jobs": -1,
        "random_state": 42,
    }

    def __init__(self, params: Optional[Dict[str, Any]] = None):
        self.params = dict(self.DEFAULT_PARAMS)
        if params:
            self.params.update(params)
        self.model = RandomForestClassifier(**self.params)

    def train(
        self,
        x: np.ndarray,
        y: np.ndarray,
        sample_weight: Optional[np.ndarray] = None,
    ) -> "RandomForestModel":
        fit_kwargs = {}
        if sample_weight is not None:
            fit_kwargs["sample_weight"] = sample_weight
        self.model.fit(x, y, **fit_kwargs)
        return self

    def predict(self, x: np.ndarray) -> np.ndarray:
        return self.model.predict(x)

    def predict_proba(self, x: np.ndarray) -> np.ndarray:
        return self.model.predict_proba(x)

    def feature_importances(self) -> Optional[np.ndarray]:
        return getattr(self.model, "feature_importances_", None)

    def save(self, path: str | Path) -> None:
        path = Path(path)
        path.parent.mkdir(parents=True, exist_ok=True)
        joblib.dump(self.model, path)

    @classmethod
    def load(cls, path: str | Path) -> "RandomForestModel":
        instance = cls()
        instance.model = joblib.load(path)
        return instance
