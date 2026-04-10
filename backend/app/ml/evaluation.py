"""
Evaluation utilities for disease classification models.
"""

from __future__ import annotations

from typing import Dict

import numpy as np
from sklearn.metrics import accuracy_score, confusion_matrix, f1_score, precision_score, recall_score


def top_k_accuracy(y_true: np.ndarray, y_prob: np.ndarray, k: int) -> float:
    """Compute top-k accuracy from probability scores."""
    if y_prob.ndim != 2:
        raise ValueError("y_prob must be a 2D array")
    k = max(1, min(k, y_prob.shape[1]))
    top_k = np.argsort(y_prob, axis=1)[:, -k:]
    return float(np.mean(np.any(top_k == y_true.reshape(-1, 1), axis=1)))


def compute_classification_metrics(y_true: np.ndarray, y_pred: np.ndarray, y_prob: np.ndarray) -> Dict[str, float]:
    """Compute aggregate metrics for multi-class classification."""
    return {
        "accuracy": float(accuracy_score(y_true, y_pred)),
        "top3_accuracy": top_k_accuracy(y_true, y_prob, 3),
        "top5_accuracy": top_k_accuracy(y_true, y_prob, 5),
        "precision_weighted": float(precision_score(y_true, y_pred, average="weighted", zero_division=0)),
        "recall_weighted": float(recall_score(y_true, y_pred, average="weighted", zero_division=0)),
        "f1_weighted": float(f1_score(y_true, y_pred, average="weighted", zero_division=0)),
        "precision_macro": float(precision_score(y_true, y_pred, average="macro", zero_division=0)),
        "recall_macro": float(recall_score(y_true, y_pred, average="macro", zero_division=0)),
        "f1_macro": float(f1_score(y_true, y_pred, average="macro", zero_division=0)),
    }


def compute_confusion_matrix(y_true: np.ndarray, y_pred: np.ndarray) -> np.ndarray:
    """Compute confusion matrix."""
    return confusion_matrix(y_true, y_pred)


def soft_vote(probabilities: Dict[str, np.ndarray], weights: Dict[str, float]) -> np.ndarray:
    """Compute weighted soft-voting probabilities."""
    if not probabilities:
        raise ValueError("No model probabilities provided")

    ref_shape = None
    voted = None

    for name, probs in probabilities.items():
        if ref_shape is None:
            ref_shape = probs.shape
            voted = np.zeros_like(probs, dtype=np.float64)
        elif probs.shape != ref_shape:
            raise ValueError(f"Probability shape mismatch for {name}: {probs.shape} != {ref_shape}")

        voted += probs * float(weights.get(name, 0.0))

    if voted is None:
        raise ValueError("Failed to build ensemble probabilities")

    row_sum = voted.sum(axis=1, keepdims=True)
    row_sum[row_sum == 0.0] = 1.0
    return (voted / row_sum).astype(np.float32)
