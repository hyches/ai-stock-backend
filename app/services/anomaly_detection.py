import numpy as np
import pandas as pd
from sklearn.ensemble import IsolationForest

class AnomalyDetector:
    def __init__(self):
        self.model = IsolationForest(contamination=0.01, random_state=42)

    def fit_predict(self, data: pd.DataFrame):
        # data: DataFrame with columns ['price', 'volume']
        X = data[['price', 'volume']].values
        preds = self.model.fit_predict(X)
        data['anomaly'] = preds
        return data

def detect_anomalies(price_series, volume_series):
    df = pd.DataFrame({'price': price_series, 'volume': volume_series})
    detector = AnomalyDetector()
    return detector.fit_predict(df) 