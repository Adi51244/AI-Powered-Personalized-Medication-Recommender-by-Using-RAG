"""
Utilities for loading prepared ML datasets and artifacts.
"""

from __future__ import annotations

import json
import pickle
from dataclasses import dataclass
from pathlib import Path
from typing import Dict, Generator, Optional, Tuple

import numpy as np

from app.ml.feature_engineering import FeatureExtractor


@dataclass(frozen=True)
class DatasetSplit:
    """In-memory representation of one dataset split."""

    features: np.ndarray
    labels: np.ndarray


class MLDataLoader:
    """Load ML arrays, metadata, and artifacts created by prepare_ml_data.py."""

    def __init__(self, data_dir: str | Path = "data/ml"):
        self.data_dir = Path(data_dir)

    def _require_file(self, filename: str) -> Path:
        path = self.data_dir / filename
        if not path.exists():
            raise FileNotFoundError(f"Required artifact not found: {path}")
        return path

    def load_split(self, split: str) -> DatasetSplit:
        """
        Load a split by name.

        Args:
            split: One of train, val, test.
        """
        if split not in {"train", "val", "test"}:
            raise ValueError("split must be one of: train, val, test")

        features = np.load(self._require_file(f"{split}_features.npy"))
        labels = np.load(self._require_file(f"{split}_labels.npy"))

        if features.shape[0] != labels.shape[0]:
            raise ValueError(
                f"Mismatched rows for {split}: features={features.shape[0]}, labels={labels.shape[0]}"
            )

        return DatasetSplit(features=features, labels=labels)

    def load_all_splits(self) -> Dict[str, DatasetSplit]:
        """Load train, validation, and test splits."""
        return {
            "train": self.load_split("train"),
            "val": self.load_split("val"),
            "test": self.load_split("test"),
        }

    def load_label_encoder(self):
        """Load sklearn LabelEncoder artifact."""
        with self._require_file("label_encoder.pkl").open("rb") as handle:
            return pickle.load(handle)

    def load_feature_extractor(self) -> FeatureExtractor:
        """Load fitted FeatureExtractor artifact."""
        return FeatureExtractor.load(str(self._require_file("feature_extractor.pkl")))

    def load_metadata(self) -> Dict:
        """Load metadata JSON produced by data prep."""
        with self._require_file("metadata.json").open("r", encoding="utf-8") as handle:
            return json.load(handle)

    @staticmethod
    def iter_batches(
        features: np.ndarray,
        labels: np.ndarray,
        batch_size: int,
        shuffle: bool = True,
        random_state: Optional[int] = 42,
    ) -> Generator[Tuple[np.ndarray, np.ndarray], None, None]:
        """Yield mini-batches from arrays."""
        if batch_size <= 0:
            raise ValueError("batch_size must be > 0")

        if features.shape[0] != labels.shape[0]:
            raise ValueError("features and labels must have matching row counts")

        indices = np.arange(features.shape[0])
        if shuffle:
            rng = np.random.default_rng(seed=random_state)
            rng.shuffle(indices)

        for start in range(0, len(indices), batch_size):
            batch_indices = indices[start : start + batch_size]
            yield features[batch_indices], labels[batch_indices]
