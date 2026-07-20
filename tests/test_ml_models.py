import unittest
import pandas as pd
import numpy as np
import os
import sys

sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from utils.data_cleaner import DataCleaner
from ml_models.forecasting import SalesForecaster
from ml_models.churn_predictor import ChurnPredictor
from ml_models.segmenter import CustomerSegmenter
from ml_models.anomaly_detector import AnomalyDetector

class TestMLModels(unittest.TestCase):
    def setUp(self):
        # Generate dummy data frames for testing
        np.random.seed(42)
        
        # 1. Sales df (80 rows for forecasting)
        dates = pd.date_range(start="2026-01-01", periods=80, freq="D")
        self.sales_df = pd.DataFrame({
            "Date": dates,
            "Revenue": [float(i * 100 + np.random.normal(0, 10)) for i in range(80)],
            "OrdersCount": [int(i + 2) for i in range(80)],
            "InventoryLevel": [1000 - i * 10 for i in range(80)]
        })
        
        # 2. Customers df (15 rows for classification/clustering)
        self.cust_df = pd.DataFrame({
            "CustomerName": [f"Customer {i}" for i in range(15)],
            "Email": [f"cust{i}@example.com" for i in range(15)],
            "TenureMonths": [2, 12, 24, 36, 1, 3, 30, 28, 4, 8, 14, 18, 22, 6, 9],
            "TotalSpend": [100.0, 1200.0, 2400.0, 3600.0, 50.0, 150.0, 3100.0, 2900.0, 200.0, 800.0, 1400.0, 1900.0, 2200.0, 400.0, 700.0],
            "Status": ["Churned", "Active", "Active", "Active", "Churned", "Churned", "Active", "Active", "Churned", "Active", "Active", "Active", "Active", "Churned", "Active"]
        })

    def test_data_cleaner(self):
        # Create dirty dataframe
        dirty_df = pd.DataFrame({
            "Date": ["2026-01-01", "2026-01-02"],
            "Revenue": [100.0, None], # NaN
            "OrdersCount": [-5, 10], # Negative
            "InventoryLevel": [500, None]
        })
        
        clean_df = DataCleaner.clean_sales_data(dirty_df)
        # Check NaNs imputed
        self.assertFalse(clean_df["Revenue"].isnull().any())
        self.assertFalse(clean_df["InventoryLevel"].isnull().any())
        # Check negative count capped
        self.assertTrue((clean_df["OrdersCount"] >= 0).all())

    def test_sales_forecaster(self):
        forecaster = SalesForecaster()
        metrics = forecaster.train(self.sales_df)
        self.assertIn("MAE", metrics)
        self.assertIn("R2", metrics)
        
        forecast = forecaster.predict_future(self.sales_df, days_to_forecast=7)
        self.assertEqual(len(forecast), 7)
        self.assertTrue("ForecastedRevenue" in forecast.columns)

    def test_churn_predictor(self):
        predictor = ChurnPredictor()
        metrics = predictor.train(self.cust_df)
        self.assertIn("Accuracy", metrics)
        self.assertIn("F1_Score", metrics)
        
        predictions = predictor.predict_churn_risk(self.cust_df)
        self.assertTrue("ChurnRiskScore" in predictions.columns)

    def test_customer_segmenter(self):
        segmenter = CustomerSegmenter(n_clusters=3)
        res_df, metrics = segmenter.fit_predict(self.cust_df)
        self.assertIn("SilhouetteScore", metrics)
        self.assertTrue("ClusterLabel" in res_df.columns)

    def test_anomaly_detector(self):
        detector = AnomalyDetector(contamination=0.1)
        res_df, metrics = detector.detect_anomalies(self.sales_df)
        self.assertIn("AnomalyCount", metrics)
        self.assertTrue("IsAnomaly" in res_df.columns)
