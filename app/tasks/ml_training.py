"""
ML Training Celery Tasks - Background training to avoid blocking API requests
"""
from celery import Task
from app.core.celery_app import celery_app
from app.db.session import SessionLocal
import logging
from datetime import datetime
from typing import List, Optional
import pandas as pd
import yfinance as yf
from sklearn.ensemble import RandomForestRegressor, GradientBoostingRegressor
from sklearn.model_selection import train_test_split
import joblib
import os

logger = logging.getLogger(__name__)


class DatabaseTask(Task):
    """Base task with database session"""
    _db = None
    
    @property
    def db(self):
        if self._db is None:
            self._db = SessionLocal()
        return self._db
    
    def after_return(self, *args, **kwargs):
        if self._db is not None:
            self._db.close()


@celery_app.task(base=DatabaseTask, bind=True, name="app.tasks.ml_training.train_stock_model")
def train_stock_model(self, symbol: str, period: str = "2y"):
    """
    Train ML model for a specific stock in background
    """
    try:
        logger.info(f"Starting ML training for {symbol}")
        
        # Fetch historical data
        ticker = yf.Ticker(symbol)
        hist = ticker.history(period=period)
        
        if hist.empty or len(hist) < 100:
            logger.warning(f"Insufficient data for {symbol}")
            return {"status": "insufficient_data", "symbol": symbol}
        
        # Feature engineering
        from app.services.feature_extraction_service import FeatureExtractionService
        feature_service = FeatureExtractionService(self.db)
        
        features_df = feature_service.extract_features_for_training(hist)
        
        if features_df.empty:
            return {"status": "feature_extraction_failed", "symbol": symbol}
        
        # Prepare target (next day returns)
        features_df['target'] = features_df['close'].pct_change().shift(-1)
        features_df = features_df.dropna()
        
        # Split data
        feature_cols = [col for col in features_df.columns if col not in ['target', 'date', 'symbol']]
        X = features_df[feature_cols]
        y = features_df['target']
        
        X_train, X_test, y_train, y_test = train_test_split(
            X, y, test_size=0.2, shuffle=False
        )
        
        # Train Random Forest
        rf_model = RandomForestRegressor(
            n_estimators=100,
            max_depth=10,
            random_state=42,
            n_jobs=-1
        )
        rf_model.fit(X_train, y_train)
        
        # Train Gradient Boosting
        gb_model = GradientBoostingRegressor(
            n_estimators=100,
            max_depth=5,
            random_state=42
        )
        gb_model.fit(X_train, y_train)
        
        # Evaluate
        rf_score = rf_model.score(X_test, y_test)
        gb_score = gb_model.score(X_test, y_test)
        
        # Save models
        models_dir = "models"
        os.makedirs(models_dir, exist_ok=True)
        
        model_path_rf = f"{models_dir}/{symbol}_rf.joblib"
        model_path_gb = f"{models_dir}/{symbol}_gb.joblib"
        
        joblib.dump(rf_model, model_path_rf)
        joblib.dump(gb_model, model_path_gb)
        
        logger.info(f"Models trained for {symbol}: RF={rf_score:.4f}, GB={gb_score:.4f}")
        
        return {
            "status": "success",
            "symbol": symbol,
            "rf_score": rf_score,
            "gb_score": gb_score,
            "model_paths": {
                "random_forest": model_path_rf,
                "gradient_boosting": model_path_gb
            },
            "trained_at": datetime.utcnow().isoformat()
        }
        
    except Exception as e:
        logger.error(f"Error training model for {symbol}: {e}")
        return {
            "status": "error",
            "symbol": symbol,
            "error": str(e)
        }


@celery_app.task(base=DatabaseTask, bind=True, name="app.tasks.ml_training.train_all_models")
def train_all_models(self, symbols: Optional[List[str]] = None):
    """
    Train models for multiple stocks (scheduled daily)
    """
    if symbols is None:
        # Default top Indian stocks
        symbols = [
            "RELIANCE.NS", "TCS.NS", "HDFCBANK.NS", "INFY.NS", "ITC.NS",
            "ICICIBANK.NS", "SBIN.NS", "BHARTIARTL.NS", "HINDUNILVR.NS",
            "KOTAKBANK.NS", "LT.NS", "AXISBANK.NS", "WIPRO.NS", "ASIANPAINT.NS",
            "MARUTI.NS", "ULTRACEMCO.NS", "SUNPHARMA.NS", "TITAN.NS", 
            "NESTLEIND.NS", "M&M.NS"
        ]
    
    logger.info(f"Starting batch training for {len(symbols)} stocks")
    
    results = []
    for symbol in symbols:
        try:
            result = train_stock_model.apply_async(
                args=[symbol],
                kwargs={"period": "2y"}
            )
            results.append({
                "symbol": symbol,
                "task_id": result.id,
                "status": "queued"
            })
        except Exception as e:
            logger.error(f"Error queueing training for {symbol}: {e}")
            results.append({
                "symbol": symbol,
                "status": "error",
                "error": str(e)
            })
    
    return {
        "total_symbols": len(symbols),
        "queued": len([r for r in results if r["status"] == "queued"]),
        "failed": len([r for r in results if r["status"] == "error"]),
        "results": results,
        "timestamp": datetime.utcnow().isoformat()
    }


@celery_app.task(base=DatabaseTask, bind=True, name="app.tasks.ml_training.update_feature_store")
def update_feature_store(self, symbol: str):
    """
    Update feature store with latest calculated features
    """
    try:
        from app.services.feature_store_service import FeatureStoreService
        from app.services.feature_extraction_service import FeatureExtractionService
        
        feature_store = FeatureStoreService(self.db)
        feature_service = FeatureExtractionService(self.db)
        
        # Fetch latest data
        ticker = yf.Ticker(symbol)
        hist = ticker.history(period="5d")
        
        if hist.empty:
            return {"status": "no_data", "symbol": symbol}
        
        # Extract features
        features = feature_service.extract_all_features(hist)
        
        # Store in feature store
        stored_count = feature_store.store_features_bulk(
            symbol=symbol,
            features=features,
            source="calculated"
        )
        
        logger.info(f"Updated {stored_count} features for {symbol}")
        
        return {
            "status": "success",
            "symbol": symbol,
            "features_updated": stored_count,
            "timestamp": datetime.utcnow().isoformat()
        }
        
    except Exception as e:
        logger.error(f"Error updating feature store for {symbol}: {e}")
        return {
            "status": "error",
            "symbol": symbol,
            "error": str(e)
        }


@celery_app.task(name="app.tasks.ml_training.cleanup_old_models")
def cleanup_old_models(days_to_keep: int = 30):
    """
    Clean up old model files to save space
    """
    try:
        import glob
        from datetime import datetime, timedelta
        
        models_dir = "models"
        if not os.path.exists(models_dir):
            return {"status": "no_models_dir"}
        
        cutoff_date = datetime.now() - timedelta(days=days_to_keep)
        deleted_count = 0
        
        for model_file in glob.glob(f"{models_dir}/*.joblib"):
            file_time = datetime.fromtimestamp(os.path.getmtime(model_file))
            if file_time < cutoff_date:
                os.remove(model_file)
                deleted_count += 1
                logger.info(f"Deleted old model: {model_file}")
        
        return {
            "status": "success",
            "deleted_count": deleted_count,
            "cutoff_date": cutoff_date.isoformat()
        }
        
    except Exception as e:
        logger.error(f"Error cleaning up models: {e}")
        return {"status": "error", "error": str(e)}
