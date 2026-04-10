"""
ML models for disease prediction.
"""

from app.ml.models.random_forest import RandomForestModel
from app.ml.models.svm_model import SVMModel
try:
	from app.ml.models.xgboost_model import XGBoostModel
except ModuleNotFoundError:
	XGBoostModel = None

__all__ = ["RandomForestModel", "XGBoostModel", "SVMModel"]
