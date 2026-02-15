"""
Explainable AI (XAI) Service
============================
Provides model interpretability using SHAP (SHapley Additive exPlanations)
and LIME (Local Interpretable Model-agnostic Explanations).
"""

import os
import shap
import lime
import lime.lime_tabular
import numpy as np
import pandas as pd
from typing import Dict, List, Any, Optional
import logging

logger = logging.getLogger(__name__)

class ExplainabilityService:
    """
    Service to explain ML model predictions.
    Supports ensemble models and individual gradient boosting models.
    """
    
    def __init__(self):
        self.shap_explainers = {}
        self.lime_explainers = {}

    def get_feature_importance_shap(
        self, 
        model_name: str, 
        model: Any, 
        X_train: np.ndarray, 
        feature_names: List[str]
    ) -> Dict[str, float]:
        """
        Calculate global feature importance using SHAP values.
        """
        try:
            # For tree-based models, use TreeExplainer for efficiency
            if model_name in ['XGBoost', 'LightGBM', 'CatBoost', 'RandomForest', 'ExtraTrees']:
                explainer = shap.TreeExplainer(model)
                shap_values = explainer.shap_values(X_train)
                
                # Check if it's a classification model with multiple classes
                if isinstance(shap_values, list): # Multi-class
                    # Take absolute mean of SHAP values across classes
                    abs_shap = np.abs(shap_values).mean(axis=0)
                else:
                    abs_shap = np.abs(shap_values)
                
                # Mean across samples
                importances = abs_shap.mean(axis=0)
                
                return dict(zip(feature_names, [float(v) for v in importances]))
            else:
                # Fallback for others
                explainer = shap.Explainer(model, X_train)
                shap_values = explainer(X_train)
                importances = np.abs(shap_values.values).mean(axis=0)
                return dict(zip(feature_names, [float(v) for v in importances]))
        except Exception as e:
            logger.error(f"Error calculating SHAP importance for {model_name}: {e}")
            return {}

    def explain_prediction(
        self, 
        model: Any, 
        X_instance: np.ndarray, 
        X_train: np.ndarray, 
        feature_names: List[str],
        method: str = "shap"
    ) -> Dict[str, Any]:
        """
        Produce a local explanation for a single prediction.
        """
        if method == "shap":
            return self._explain_shap(model, X_instance, X_train, feature_names)
        else:
            return self._explain_lime(model, X_instance[0], X_train, feature_names)

    def _explain_shap(self, model: Any, X_instance: np.ndarray, X_train: np.ndarray, feature_names: List[str]) -> Dict[str, Any]:
        """Local SHAP explanation"""
        try:
            explainer = shap.Explainer(model, X_train)
            shap_values = explainer(X_instance)
            
            # Format results
            contributions = []
            for i, feat in enumerate(feature_names):
                contributions.append({
                    "feature": feat,
                    "value": float(X_instance[0][i]),
                    "contribution": float(shap_values.values[0][i])
                })
            
            # Sort by absolute contribution
            contributions.sort(key=lambda x: abs(x["contribution"]), reverse=True)
            
            return {
                "method": "shap",
                "base_value": float(shap_values.base_values[0]),
                "prediction_value": float(shap_values.values[0].sum() + shap_values.base_values[0]),
                "contributions": contributions
            }
        except Exception as e:
            logger.error(f"SHAP local explanation error: {e}")
            return {"error": str(e)}

    def _explain_lime(self, model: Any, instance: np.ndarray, X_train: np.ndarray, feature_names: List[str]) -> Dict[str, Any]:
        """Local LIME explanation"""
        try:
            explainer = lime.lime_tabular.LimeTabularExplainer(
                X_train,
                feature_names=feature_names,
                class_names=['Down', 'Up'],
                mode='classification'
            )
            
            # Handle prediction function
            predict_fn = None
            if hasattr(model, "predict_proba"):
                predict_fn = model.predict_proba
            else:
                # For regressors or others, we might need a wrapper
                def mock_predict_proba(x):
                    preds = model.predict(x)
                    # Convert to dummy probas
                    p1 = 1 / (1 + np.exp(-preds))
                    return np.column_stack([1 - p1, p1])
                predict_fn = mock_predict_proba

            exp = explainer.explain_instance(instance, predict_fn, num_features=10)
            
            return {
                "method": "lime",
                "intercept": float(exp.intercept[1]),
                "contributions": [
                    {"feature": feat, "contribution": float(weight)} 
                    for feat, weight in exp.as_list()
                ]
            }
        except Exception as e:
            logger.error(f"LIME local explanation error: {e}")
            return {"error": str(e)}

# Singleton instance
xai_service = ExplainabilityService()