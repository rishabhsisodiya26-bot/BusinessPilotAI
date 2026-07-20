import pandas as pd
import numpy as np
from sklearn.ensemble import RandomForestClassifier
from sklearn.model_selection import train_test_split
from sklearn.metrics import accuracy_score, precision_score, recall_score, f1_score, confusion_matrix

class ChurnPredictor:
    def __init__(self, n_estimators=100, random_state=42):
        self.model = RandomForestClassifier(n_estimators=n_estimators, random_state=random_state)
        self.feature_cols = ['TenureMonths', 'TotalSpend', 'SpendPerMonth']
        self.is_trained = False

    def _prepare_features(self, df: pd.DataFrame) -> pd.DataFrame:
        df = df.copy()
        # Create helper feature: Spend per month (avoiding divide-by-zero)
        df['SpendPerMonth'] = df['TotalSpend'] / df['TenureMonths'].replace(0, 1)
        return df

    def train(self, df: pd.DataFrame):
        """
        Trains model to predict Churn status.
        Maps Status 'Active' to 0 and 'Churned' to 1.
        """
        if len(df) < 10:
            raise ValueError("Insufficient customer records for classification training (minimum 10 required).")
            
        prepared_df = self._prepare_features(df)
        
        # Target mapping
        y = prepared_df['Status'].apply(lambda x: 1 if x == 'Churned' else 0)
        X = prepared_df[self.feature_cols]
        
        # Check if we have both classes
        if len(y.unique()) < 2:
            # Fake a single train split if we only have one class to avoid error, 
            # but usually seeded data contains both.
            raise ValueError("Dataset must contain both Active and Churned customer statuses for training.")
            
        X_train, X_test, y_train, y_test = train_test_split(
            X, y, test_size=0.3, random_state=42, stratify=y
        )
        
        self.model.fit(X_train, y_train)
        
        # Test predictions
        y_pred = self.model.predict(X_test)
        y_prob = self.model.predict_proba(X_test)[:, 1]
        
        acc = accuracy_score(y_test, y_pred)
        prec = precision_score(y_test, y_pred, zero_division=0)
        rec = recall_score(y_test, y_pred, zero_division=0)
        f1 = f1_score(y_test, y_pred, zero_division=0)
        cm = confusion_matrix(y_test, y_pred).tolist() # Convert numpy array to list for JSON serialization
        
        # Retrain on complete dataset
        self.model.fit(X, y)
        self.is_trained = True
        
        metrics = {
            "Accuracy": float(acc),
            "Precision": float(prec),
            "Recall": float(rec),
            "F1_Score": float(f1),
            "ConfusionMatrix": cm
        }
        
        return metrics

    def predict_churn_risk(self, df: pd.DataFrame) -> pd.DataFrame:
        """
        Calculates the probability of churn for each customer.
        """
        if not self.is_trained:
            raise RuntimeError("Model must be trained before predicting.")
            
        prepared_df = self._prepare_features(df)
        X = prepared_df[self.feature_cols]
        
        probs = self.model.predict_proba(X)[:, 1]
        
        result_df = df.copy()
        result_df['ChurnRiskScore'] = np.round(probs, 4)
        return result_df
