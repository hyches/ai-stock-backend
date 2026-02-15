"""
Auto-Retraining Pipeline
========================
Monitors model performance and triggers automated re-training when 
drift is detected or periodically.
"""

import os
import logging
from typing import Dict, Any, Optional
from datetime import datetime, timedelta
import pandas as pd
from app.services.ml_engine import ml_engine
from app.api.endpoints.research_ml import trigger_ml_training

logger = logging.getLogger(__name__)

class AutoRetrainer:
    """
    Service to automate ML model retraining.
    """
    
    def __init__(self, retrain_interval_days: int = 7):
        self.retrain_interval_days = retrain_interval_days
        self.last_retrain_times = {} # symbol -> last_retrain_time

    async def check_and_retrain(self, symbol: str, current_df: pd.DataFrame) -> Dict[str, Any]:
        """
        Check if a symbol needs retraining based on time or performance drift.
        """
        if self._should_retrain(symbol):
            logger.info(f"Auto-retraining triggered for {symbol}")
            # In a real system, we'd check drift metrics here
            # For now, we use a simple interval-based approach
            try:
                # Use the existing background training endpoint logic
                # Note: trigger_ml_training returns a Job ID
                result = await trigger_ml_training(symbol)
                self.last_retrain_times[symbol] = datetime.utcnow()
                return {
                    "status": "triggered",
                    "symbol": symbol,
                    "job_id": result.get("job_id"),
                    "reason": "Interval reached"
                }
            except Exception as e:
                logger.error(f"Auto-retraining failed for {symbol}: {e}")
                return {"status": "error", "message": str(e)}
        
        return {"status": "skipped", "reason": "Retraining not required yet"}

    def _should_retrain(self, symbol: str) -> bool:
        """Determines if retraining is necessary"""
        last_time = self.last_retrain_times.get(symbol)
        if not last_time:
            return True # Never trained before (auto-triggered on first use)
            
        elapsed = datetime.utcnow() - last_time
        return elapsed.days >= self.retrain_interval_days

# Singleton instance
ml_auto_retrainer = AutoRetrainer()
