import numpy as np
from typing import List, Dict, Any, Optional

class AnomalyDetector:
    def __init__(self, window_size: int = 20, threshold: float = 2.5):
        """
        Initialize AnomalyDetector with Z-Score method.
        
        Args:
            window_size: Number of periods for moving average/std dev
            threshold: Z-Score threshold for anomaly flagging (default 2.5 standard deviations)
        """
        self.window_size = window_size
        self.threshold = threshold

    def detect_anomalies(self, prices: List[float], dates: List[str]) -> List[Dict[str, Any]]:
        """
        Detect anomalies in a price series using statistical Z-Score.
        Returns a list of anomalies found.
        """
        if len(prices) < self.window_size:
            return []

        anomalies = []
        prices_arr = np.array(prices)
        
        # We need at least 'window_size' data points to start calculating statistics
        for i in range(self.window_size, len(prices)):
            window = prices_arr[i-self.window_size:i]
            
            mean = np.mean(window)
            std = np.std(window)
            
            # Avoid division by zero
            if std == 0:
                continue
                
            current_price = prices[i]
            z_score = (current_price - mean) / std
            
            if abs(z_score) > self.threshold:
                anomalies.append({
                    "date": dates[i],
                    "price": current_price,
                    "mean": float(mean),
                    "std": float(std),
                    "z_score": float(z_score),
                    "type": "spike" if z_score > 0 else "drop",
                    "severity": self._calculate_severity(z_score)
                })
                
        return anomalies

    def _calculate_severity(self, z_score: float) -> str:
        abs_z = abs(z_score)
        if abs_z > 4.0:
            return "critical"
        elif abs_z > 3.0:
            return "high"
        else:
            return "medium"

    def analyze_market_behavior(self, market_data: List[Dict[str, Any]]) -> Dict[str, Any]:
        """
        Analyze broader market behavior for regime detection (volatility clustering).
        """
        if not market_data:
            return {}
            
        prices = [d["close"] for d in market_data]
        dates = [d["date"] for d in market_data]
        
        # Calculate recent volatility
        returns = np.diff(np.log(prices))
        current_volatility = np.std(returns[-20:]) * np.sqrt(252) if len(returns) >= 20 else 0
        
        # Detect regime
        regime = "neutral"
        if current_volatility > 0.25: # Arbitrary high vol threshold
            regime = "volatile"
        elif current_volatility < 0.10:
            regime = "stable"
            
        return {
            "current_volatility": float(current_volatility),
            "regime": regime,
            "anomalies_count": len(self.detect_anomalies(prices, dates))
        }
