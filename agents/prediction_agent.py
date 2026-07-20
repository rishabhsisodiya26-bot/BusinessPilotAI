import time
import sqlite3
import json
import pandas as pd
from agents.base_agent import BaseAgent

class PredictionAgent(BaseAgent):
    def __init__(self, db_path: str = "./database/database.db"):
        super().__init__(
            name="MLPredictionAgent",
            role_description="Specialist in interpreting model metrics, tracking model selections, and highlighting statistical predictions.",
            db_path=db_path
        )

    def generate_prediction_summary(self, session_id: str, company_id: int = 1) -> str:
        """
        Reads ML outputs and evaluation metrics from database, compiles a prediction summary report.
        """
        start_time = time.time()
        conn = self._get_connection()
        
        try:
            # Query prediction logs to extract metrics
            cursor = conn.cursor()
            cursor.execute("""
                SELECT target_type, metrics_json, COUNT(*) 
                FROM predictions 
                WHERE company_id = ? 
                GROUP BY target_type
            """, (company_id,))
            records = cursor.fetchall()
            
            metrics_dict = {}
            for rec in records:
                target_type, metrics_json, count = rec
                if metrics_json:
                    try:
                        metrics_dict[target_type] = json.loads(metrics_json)
                    except Exception:
                        pass
                    metrics_dict[target_type]["row_count"] = count
                    
            # Fetch top churn risks
            churn_risks_df = pd.read_sql_query("""
                SELECT c.name, p.probability 
                FROM predictions p
                JOIN customers c ON p.source_id = c.id
                WHERE p.company_id = ? AND p.target_type = 'customer_churn'
                ORDER BY p.probability DESC
                LIMIT 5
            """, conn, params=(company_id,))
            
            # Fetch sales forecast totals
            forecast_df = pd.read_sql_query("""
                SELECT predicted_value FROM predictions 
                WHERE company_id = ? AND target_type = 'sales_forecast'
            """, conn, params=(company_id,))
            
            forecast_total = 0.0
            if not forecast_df.empty:
                for idx, row in forecast_df.iterrows():
                    val = json.loads(row['predicted_value'])
                    forecast_total += val.get('ForecastedRevenue', 0.0)
                    
        except Exception as e:
            conn.close()
            return f"MLPredictionAgent Error: Failed to query predictions: {str(e)}"
        finally:
            conn.close()

        # Build prompt stats
        stats_data = {
            "ModelsTrained": list(metrics_dict.keys()),
            "ForecastTotal30Days": forecast_total,
            "Metrics": metrics_dict,
            "TopChurnRisks": churn_risks_df.to_dict(orient='records') if not churn_risks_df.empty else []
        }
        
        system_prompt = (
            f"You are the {self.name}. Your role is: {self.role_description}. "
            "Write a clean, professional prediction report explaining ML model accuracy, metrics, "
            "risks, segment distributions, and anomaly findings. Use markdown lists and bold text."
        )
        
        prompt = (
            f"Generate a machine learning performance and prediction report based on the following model results:\n\n"
            f"{json.dumps(stats_data, indent=2)}"
        )
        
        report = self.query_llm(prompt, system_prompt)
        
        if not report:
            # Fallback local renderer
            metrics = stats_data["Metrics"]
            forecast_metrics = metrics.get("sales_forecast", {})
            churn_metrics = metrics.get("customer_churn", {})
            segment_metrics = metrics.get("segmentation", {})
            anomaly_metrics = metrics.get("anomaly", {})
            
            risk_list = ""
            for item in stats_data["TopChurnRisks"]:
                risk_list += f"- **{item['name']}** (Risk: {item['probability']*100:.1f}%)\n"
            if not risk_list:
                risk_list = "- No churn risks identified.\n"
                
            report = (
                f"### 🤖 Machine Learning Modules & Predictions Summary\n\n"
                f"**Prepared by:** {self.name}\n\n"
                f"The predictive pipelines have successfully run, evaluated, and cached results inside the central database schema.\n\n"
                f"#### 1. Sales & Demand Forecasting (Random Forest Regressor)\n"
                f"- **Model Fit Evaluation**: Mean Absolute Error (MAE) of **${forecast_metrics.get('MAE', 0):,.2f}** | R² Score: **{forecast_metrics.get('R2', 0):.3f}**.\n"
                f"- **Outlook**: The cumulative projected revenue for the next 30 days is **${forecast_total:,.2f}**.\n\n"
                f"#### 2. Customer Churn Prediction (Random Forest Classifier)\n"
                f"- **Model Fit Evaluation**: Accuracy: **{churn_metrics.get('Accuracy', 0)*100:.1f}%** | F1-Score: **{churn_metrics.get('F1_Score', 0)*100:.1f}%**.\n"
                f"- **Highest Churn Risk Customers**:\n{risk_list}\n"
                f"#### 3. Customer Segmentation (K-Means Clustering)\n"
                f"- **Model Fit Evaluation**: Silhouette Coefficient: **{segment_metrics.get('SilhouetteScore', 0):.3f}**.\n"
                f"- **Groupings**: Customers are clustered into 3 tiers based on tenure and spends (High-Value Champions, Core Shoppers, and Low-Value/At-Risk Shoppers).\n\n"
                f"#### 4. Anomaly Detection (Isolation Forest)\n"
                f"- **Metrics**: Flagged **{anomaly_metrics.get('AnomalyCount', 0)}** transactions as statistical outliers (Anomaly Rate of **{anomaly_metrics.get('AnomalyRate', 0)*100:.2f}%**)."
            )
            
        latency = time.time() - start_time
        self.log_agent_execution(session_id, "Analyze ML predictions and metrics", report, latency)
        
        return report
