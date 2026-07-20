import pandas as pd
import numpy as np
from sklearn.ensemble import IsolationForest

class AnomalyDetector:
    def __init__(self, contamination=0.03, random_state=42):
        self.model = IsolationForest(contamination=contamination, random_state=random_state)
        self.feature_cols = ['Revenue', 'OrdersCount']
        self.is_fitted = False

    def detect_anomalies(self, df: pd.DataFrame) -> pd.DataFrame:
        """
        Fits the Isolation Forest on Revenue and OrdersCount.
        Flags outliers with 1 (Anomaly) or 0 (Normal).
        """
        if len(df) < 10:
            raise ValueError("Insufficient data points for anomaly detection training (minimum 10 required).")
            
        df = df.copy()
        X = df[self.feature_cols].copy()
        
        # Fit and predict. IsolationForest outputs -1 for outliers and 1 for inliers.
        self.model.fit(X)
        self.is_fitted = True
        
        preds = self.model.predict(X)
        
        # Convert to 1 for anomaly, 0 for normal
        df['IsAnomaly'] = np.where(preds == -1, 1, 0)
        
        # Calculate anomaly rate
        anomaly_count = int(df['IsAnomaly'].sum())
        anomaly_rate = float(anomaly_count / len(df))
        
        metrics = {
            "AnomalyCount": anomaly_count,
            "AnomalyRate": anomaly_rate
        }
        
        return df, metrics
