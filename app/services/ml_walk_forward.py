"""
Walk-Forward Optimization Engine
================================
Implements rolling window training and out-of-sample validation to ensure 
models adapt to non-stationary market dynamics.
"""

import numpy as np
import pandas as pd
from typing import Dict, List, Tuple, Optional, Any, Type
from datetime import datetime, timedelta
import logging
from app.services.ml_engine import ml_engine, BaseMLModel
from sklearn.metrics import accuracy_score, f1_score, mean_squared_error

logger = logging.getLogger(__name__)

class WalkForwardOptimizer:
    """
    Implements Walk-Forward Optimization (WFO) for trading strategies.
    
    WFO involves:
    1. Training on an 'In-Sample' (IS) window.
    2. Validating on an 'Out-of-Sample' (OOS) window.
    3. Rolling the windows forward and repeating.
    """
    
    def __init__(
        self, 
        anchor_type: str = "rolling", # "rolling" or "expanding"
        train_window_bars: int = 500,
        oos_window_bars: int = 100,
        step_size_bars: int = 100
    ):
        self.anchor_type = anchor_type
        self.train_window_bars = train_window_bars
        self.oos_window_bars = oos_window_bars
        self.step_size_bars = step_size_bars

    def run_optimization(
        self, 
        symbol: str, 
        df: pd.DataFrame, 
        model_names: List[str] = None
    ) -> Dict[str, Any]:
        """
        Runs the walk-forward process across the provided dataframe.
        """
        if len(df) < (self.train_window_bars + self.oos_window_bars):
            return {
                "status": "error", 
                "message": "Insufficient data for walk-forward optimization."
            }

        if not model_names:
            model_names = ml_engine.get_available_models()

        # Feature Engineering
        features_df = ml_engine.feature_engineering.compute_all_features(df)
        
        # Targets
        horizon = 5
        close = df['Close'].iloc[len(df) - len(features_df):].reset_index(drop=True)
        features_df = features_df.reset_index(drop=True)
        
        features_df['_target_direction'] = (close.shift(-horizon) > close).astype(int)
        features_df['_target_return'] = (close.shift(-horizon) - close) / close
        
        data = features_df.dropna()
        feature_cols = [c for c in data.columns if not c.startswith('_')]
        
        total_bars = len(data)
        results = []
        
        curr_start = 0
        while curr_start + self.train_window_bars + self.oos_window_bars <= total_bars:
            train_end = curr_start + self.train_window_bars
            oos_end = train_end + self.oos_window_bars
            
            # Splitting
            if self.anchor_type == "expanding":
                train_data = data.iloc[0:train_end]
            else:
                train_data = data.iloc[curr_start:train_end]
                
            oos_data = data.iloc[train_end:oos_end]
            
            X_train = train_data[feature_cols].values
            y_train_cls = train_data['_target_direction'].values
            y_train_reg = train_data['_target_return'].values
            
            X_oos = oos_data[feature_cols].values
            y_oos_cls = oos_data['_target_direction'].values
            y_oos_reg = oos_data['_target_return'].values
            
            fold_result = {
                "train_range": (train_data.index[0], train_data.index[-1]),
                "oos_range": (oos_data.index[0], oos_data.index[-1]),
                "model_performance": {}
            }
            
            # Evaluate each model for this fold
            for name in model_names:
                # We need fresh instances for each fold to avoid leakage
                # This is a bit simplified; in reality we'd use the MLEngine's factory
                model_instance = self._get_model_instance(name)
                if not model_instance: continue
                
                model_instance.train(X_train, y_train_cls, y_train_reg, feature_cols)
                
                # Predict on OOS
                X_oos_scaled = model_instance.scaler.transform(X_oos)
                y_pred_cls = model_instance.classifier.predict(X_oos_scaled)
                y_pred_reg = model_instance.regressor.predict(X_oos_scaled)
                
                fold_result["model_performance"][name] = {
                    "accuracy": float(accuracy_score(y_oos_cls, y_pred_cls)),
                    "f1": float(f1_score(y_oos_cls, y_pred_cls, average='weighted')),
                    "mse": float(mean_squared_error(y_oos_reg, y_pred_reg))
                }
            
            results.append(fold_result)
            curr_start += self.step_size_bars
            
        # Calculate aggregate metrics
        agg_metrics = self._calculate_aggregate_metrics(results, model_names)
        
        return {
            "status": "success",
            "symbol": symbol,
            "folds": len(results),
            "aggregate_performance": agg_metrics,
            "fold_details": results
        }

    def _get_model_instance(self, name: str) -> Optional[BaseMLModel]:
        """Helper to get a fresh instance of a model by name"""
        from app.services.ml_engine import (
            RandomForestModel, ExtraTreesModel, XGBoostModel, 
            LightGBMModel, CatBoostModel, HAS_XGBOOST, HAS_LIGHTGBM, HAS_CATBOOST
        )
        
        if name == 'RandomForest': return RandomForestModel()
        if name == 'ExtraTrees': return ExtraTreesModel()
        if name == 'XGBoost' and HAS_XGBOOST: return XGBoostModel()
        if name == 'LightGBM' and HAS_LIGHTGBM: return LightGBMModel()
        if name == 'CatBoost' and HAS_CATBOOST: return CatBoostModel()
        return None

    def _calculate_aggregate_metrics(self, results: List[Dict], model_names: List[str]) -> Dict:
        """Helper to calculate average performance across all folds"""
        agg = {}
        for name in model_names:
            accs = [r["model_performance"][name]["accuracy"] for r in results if name in r["model_performance"]]
            if not accs: continue
            
            agg[name] = {
                "avg_accuracy": float(np.mean(accs)),
                "std_accuracy": float(np.std(accs)),
                "min_accuracy": float(np.min(accs)),
                "max_accuracy": float(np.max(accs)),
                "consistency_score": float(np.mean(accs) / (np.std(accs) + 1e-6))
            }
        return agg

# Singleton
ml_walk_forward = WalkForwardOptimizer()
