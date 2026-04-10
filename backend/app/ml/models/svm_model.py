"""
SVM model wrapper for disease classification.
"""

from __future__ import annotations

from pathlib import Path
from typing import Any, Dict, Optional

import joblib
import numpy as np
from sklearn.pipeline import Pipeline
from sklearn.preprocessing import StandardScaler
from sklearn.svm import SVC


class SVMModel:
    """Thin wrapper around sklearn SVC."""

    DEFAULT_PARAMS: Dict[str, Any] = {
        "kernel": "rbf",
        "C": 10.0,
        "gamma": "scale",
        "probability": True,
        "class_weight": "balanced",
        "random_state": 42,
    }

    def __init__(self, params: Optional[Dict[str, Any]] = None):
        self.params = dict(self.DEFAULT_PARAMS)
        if params:
            self.params.update(params)
        self.model = Pipeline(
            steps=[
                ("scaler", StandardScaler()),
                ("svc", SVC(**self.params)),
            ]
        )

    def train(
        self,
        x: np.ndarray,
        y: np.ndarray,
        sample_weight: Optional[np.ndarray] = None,
    ) -> "SVMModel":
        fit_kwargs = {}
        if sample_weight is not None:
            fit_kwargs["svc__sample_weight"] = sample_weight
        self.model.fit(x, y, **fit_kwargs)
        return self

    def predict(self, x: np.ndarray) -> np.ndarray:
        return self.model.predict(x)

    def predict_proba(self, x: np.ndarray) -> np.ndarray:
        return self.model.predict_proba(x)

    def save(self, path: str | Path) -> None:
        path = Path(path)
        path.parent.mkdir(parents=True, exist_ok=True)
        joblib.dump(self.model, path)

    @classmethod
    def load(cls, path: str | Path) -> "SVMModel":
        instance = cls()
        instance.model = joblib.load(path)
        return instance
