import os
import sqlite3
import json
import pandas as pd
import numpy as np
from datetime import datetime

# Import models
from ml_models.forecasting import SalesForecaster
from ml_models.churn_predictor import ChurnPredictor
from ml_models.segmenter import CustomerSegmenter
from ml_models.anomaly_detector import AnomalyDetector

DB_PATH = os.path.join(".", "database", "database.db")

class MLEvaluator:
    def __init__(self, db_path=DB_PATH):
        self.db_path = db_path

    def _get_connection(self):
        return sqlite3.connect(self.db_path)

    def run_all_models(self, company_id=1):
        """
        Loads data from DB, runs all ML models, evaluates them,
        saves forecasts and risks back to predictions table,
        and returns consolidated metrics.
        """
        conn = self._get_connection()
        metrics_summary = {}
        
        try:
            # Clear old predictions of the company to avoid duplication
            cursor = conn.cursor()
            cursor.execute("DELETE FROM predictions WHERE company_id = ?", (company_id,))
            conn.commit()
            
            # 1. RUN SALES FORECASTING
            print("Running Sales Forecasting...")
            sales_df = pd.read_sql_query(
                "SELECT id, date, revenue, orders_count, inventory_level FROM sales WHERE company_id = ?", 
                conn, params=(company_id,)
            )
            if not sales_df.empty:
                sales_df = sales_df.rename(columns={
                    "date": "Date",
                    "revenue": "Revenue",
                    "orders_count": "OrdersCount",
                    "inventory_level": "InventoryLevel"
                })
            
            if not sales_df.empty and len(sales_df) >= 35:
                forecaster = SalesForecaster()
                forecast_metrics = forecaster.train(sales_df)
                metrics_summary["sales_forecast"] = forecast_metrics
                
                # Make 30-day forecast
                forecast_results = forecaster.predict_future(sales_df, days_to_forecast=30)
                
                # Save predictions
                forecast_rows = []
                for _, row in forecast_results.iterrows():
                    forecast_rows.append((
                        company_id,
                        'sales_forecast',
                        None,
                        json.dumps({"Date": row["Date"], "ForecastedRevenue": row["ForecastedRevenue"]}),
                        None,
                        json.dumps(forecast_metrics)
                    ))
                cursor.executemany("""
                    INSERT INTO predictions (company_id, target_type, source_id, predicted_value, probability, metrics_json)
                    VALUES (?, ?, ?, ?, ?, ?)
                """, forecast_rows)
                conn.commit()
            else:
                metrics_summary["sales_forecast"] = {"Error": "Insufficient historical sales data."}

            # 2. RUN CUSTOMER CHURN PREDICTION
            print("Running Churn Prediction...")
            customers_df = pd.read_sql_query(
                "SELECT id, name, email, tenure_months, total_spend, status FROM customers WHERE company_id = ?",
                conn, params=(company_id,)
            )
            if not customers_df.empty:
                customers_df = customers_df.rename(columns={
                    "name": "CustomerName",
                    "email": "Email",
                    "tenure_months": "TenureMonths",
                    "total_spend": "TotalSpend",
                    "status": "Status"
                })
            
            if not customers_df.empty and len(customers_df) >= 10:
                churn_pred = ChurnPredictor()
                churn_metrics = churn_pred.train(customers_df)
                metrics_summary["customer_churn"] = churn_metrics
                
                # Make predictions
                churn_results = churn_pred.predict_churn_risk(customers_df)
                
                # Save predictions
                churn_rows = []
                for _, row in churn_results.iterrows():
                    churn_rows.append((
                        company_id,
                        'customer_churn',
                        int(row["id"]),
                        str(1 if row["ChurnRiskScore"] >= 0.5 else 0), # Binary classification
                        float(row["ChurnRiskScore"]),
                        json.dumps(churn_metrics)
                    ))
                cursor.executemany("""
                    INSERT INTO predictions (company_id, target_type, source_id, predicted_value, probability, metrics_json)
                    VALUES (?, ?, ?, ?, ?, ?)
                """, churn_rows)
                conn.commit()
            else:
                metrics_summary["customer_churn"] = {"Error": "Insufficient customer data."}

            # 3. RUN CUSTOMER SEGMENTATION
            print("Running Customer Segmentation...")
            if not customers_df.empty and len(customers_df) >= 3:
                segmenter = CustomerSegmenter()
                segment_results, segment_metrics = segmenter.fit_predict(customers_df)
                metrics_summary["segmentation"] = segment_metrics
                
                # Save predictions
                segment_rows = []
                for _, row in segment_results.iterrows():
                    segment_rows.append((
                        company_id,
                        'segmentation',
                        int(row["id"]),
                        row["ClusterLabel"],
                        None,
                        json.dumps(segment_metrics)
                    ))
                cursor.executemany("""
                    INSERT INTO predictions (company_id, target_type, source_id, predicted_value, probability, metrics_json)
                    VALUES (?, ?, ?, ?, ?, ?)
                """, segment_rows)
                conn.commit()
            else:
                metrics_summary["segmentation"] = {"Error": "Insufficient customer data for clustering."}

            # 4. RUN ANOMALY DETECTION
            print("Running Anomaly Detection...")
            if not sales_df.empty and len(sales_df) >= 10:
                detector = AnomalyDetector()
                anomaly_results, anomaly_metrics = detector.detect_anomalies(sales_df)
                metrics_summary["anomaly"] = anomaly_metrics
                
                # Save predictions
                anomaly_rows = []
                for _, row in anomaly_results.iterrows():
                    # Save anomaly result linked to the sales row ID
                    anomaly_rows.append((
                        company_id,
                        'anomaly',
                        int(row["id"]),
                        str(row["IsAnomaly"]),
                        None,
                        json.dumps(anomaly_metrics)
                    ))
                cursor.executemany("""
                    INSERT INTO predictions (company_id, target_type, source_id, predicted_value, probability, metrics_json)
                    VALUES (?, ?, ?, ?, ?, ?)
                """, anomaly_rows)
                conn.commit()
            else:
                metrics_summary["anomaly"] = {"Error": "Insufficient sales records for anomaly detection."}
                
            print("ML pipeline executed and predictions saved successfully.")
            return metrics_summary
            
        except Exception as e:
            print(f"Error in ML pipeline run: {e}")
            conn.rollback()
            raise e
        finally:
            conn.close()

if __name__ == "__main__":
    evaluator = MLEvaluator()
    summary = evaluator.run_all_models(company_id=1)
    print("\nExecution Metrics Summary:")
    print(json.dumps(summary, indent=2))
