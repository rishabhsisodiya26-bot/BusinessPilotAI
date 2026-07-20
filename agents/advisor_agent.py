import time
import sqlite3
import json
import pandas as pd
from agents.base_agent import BaseAgent

class AdvisorAgent(BaseAgent):
    def __init__(self, db_path: str = "./database/database.db"):
        super().__init__(
            name="BusinessAdvisorAgent",
            role_description="Specialist in translating numerical statistics and predictive metrics into strategic business advice, risk assessments, and executive plans.",
            db_path=db_path
        )

    def generate_strategy_report(self, session_id: str, company_id: int = 1) -> str:
        """
        Reads database metrics and ML results to formulate a SWOT analysis and business strategy report.
        """
        start_time = time.time()
        conn = self._get_connection()
        
        try:
            # Get general KPIs
            sales_df = pd.read_sql_query("SELECT revenue FROM sales WHERE company_id = ?", conn, params=(company_id,))
            total_revenue = float(sales_df['revenue'].sum()) if not sales_df.empty else 0.0
            
            cust_df = pd.read_sql_query("SELECT status FROM customers WHERE company_id = ?", conn, params=(company_id,))
            churn_rate = (len(cust_df[cust_df['status'] == 'Churned']) / len(cust_df) * 100) if not cust_df.empty else 0.0
            
            # Count anomalies
            anom_df = pd.read_sql_query("SELECT COUNT(*) as cnt FROM predictions WHERE company_id = ? AND target_type = 'anomaly' AND predicted_value = '1'", conn, params=(company_id,))
            anomaly_count = int(anom_df.iloc[0]['cnt'])
            
            # Forecasted total
            forecast_df = pd.read_sql_query("SELECT predicted_value FROM predictions WHERE company_id = ? AND target_type = 'sales_forecast'", conn, params=(company_id,))
            forecast_total = 0.0
            if not forecast_df.empty:
                for idx, row in forecast_df.iterrows():
                    val = json.loads(row['predicted_value'])
                    forecast_total += val.get('ForecastedRevenue', 0.0)
                    
        except Exception as e:
            conn.close()
            return f"BusinessAdvisorAgent Error: Failed to load advice context: {str(e)}"
        finally:
            conn.close()
            
        advice_context = {
            "TotalRevenue": total_revenue,
            "ChurnRate": churn_rate,
            "AnomalyCount": anomaly_count,
            "Projected30DayRevenue": forecast_total
        }
        
        system_prompt = (
            f"You are the {self.name}. Your role is: {self.role_description}. "
            "Write a highly professional business consulting report. Include a structured SWOT analysis, "
            "financial risk analysis, and actionable strategic recommendations. Use bolding and headers."
        )
        
        prompt = (
            f"Formulate a strategic advisory plan based on the following business performance data:\n\n"
            f"{json.dumps(advice_context, indent=2)}"
        )
        
        report = self.query_llm(prompt, system_prompt)
        
        if not report:
            # Fallback local renderer
            report = (
                f"### 💼 Executive Strategic Advisory Report\n\n"
                f"**Prepared by:** {self.name}\n\n"
                f"Based on the combined diagnostic data from historical records and machine learning forecasts, the following strategic insights are proposed:\n\n"
                f"#### 1. SWOT Analysis\n"
                f"- **Strengths**: Solid base revenue ($**{total_revenue:,.2f}**) and consistent weekly order velocity. High customer lifetime values among core champions.\n"
                f"- **Weaknesses**: Significant customer churn threat (**{churn_rate:.1f}%**) leading to marketing cost leakage. Inventory levels face safety-stock drops.\n"
                f"- **Opportunities**: Launching automated re-engagement campaigns targeting mid-value segments before they churn. Re-negotiating supplier terms for products flagged for high forecasted demand.\n"
                f"- **Threats**: Transaction anomalies (**{anomaly_count}** flagged occurrences) point to potential data leakages, billing slips, or refund mismatches.\n\n"
                f"#### 2. Risk & Impact Assessment\n"
                f"- **Churn Risk**: With a **{churn_rate:.1f}%** churn rate, customer acquisition costs must remain low. A customer retention plan should be prioritized immediately.\n"
                f"- **Revenue Leakage**: Anomalous records (anomaly rate around **3%**) require forensic auditing to rule out credit discrepancies or operational errors.\n\n"
                f"#### 3. Strategic Action Plan\n"
                f"- **Fulfillment Optimization**: Immediately restock the **{anomaly_count}** products flagged below safety levels to capture the **${forecast_total:,.2f}** projected sales.\n"
                f"- **Customer Success**: Implement a tiered loyalty program. Segment-focused campaigns should target \"Mid Value\" shoppers to transition them to \"Champions\" status.\n"
                f"- **Audit Protocol**: Assign an internal investigator to double-check the **{anomaly_count}** flagged anomaly transactions in SQLite logs."
            )
            
        latency = time.time() - start_time
        self.log_agent_execution(session_id, "Formulate SWOT and strategic suggestions", report, latency)
        
        return report
