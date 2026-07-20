import streamlit as st
import pandas as pd
import json
import plotly.express as px
from ml_models.evaluator import MLEvaluator
from backend.api import BusinessService

def show_predictions_page(company_id: int):
    st.markdown("## 🤖 Predictive Intelligence Center")
    st.markdown("Execute ML models, verify statistical scores, and check predictions for sales, churn, groupings, and anomaly detections.")
    
    biz_service = BusinessService()
    
    # 1. Trigger Model Training Button
    if st.button("🚀 Re-train & Evaluate All ML Models", use_container_width=True):
        with st.spinner("Executing ML Model Pipelines..."):
            try:
                evaluator = MLEvaluator()
                metrics = evaluator.run_all_models(company_id=company_id)
                st.success("All ML pipelines executed and results cached successfully!")
            except Exception as e:
                st.error(f"Execution failed: {e}")
                
    st.markdown("---")
    
    # Load cached prediction outputs
    forecast_recs = biz_service.get_predictions_by_type(company_id, 'sales_forecast')
    churn_recs = biz_service.get_predictions_by_type(company_id, 'customer_churn')
    segment_recs = biz_service.get_predictions_by_type(company_id, 'segmentation')
    anomaly_recs = biz_service.get_predictions_by_type(company_id, 'anomaly')
    
    if not (forecast_recs or churn_recs or segment_recs or anomaly_recs):
        st.info("No prediction records found. Please trigger model execution above.")
        return
        
    tab1, tab2, tab3, tab4 = st.tabs([
        "📈 Sales Forecasting", 
        "🚪 Customer Churn", 
        "🎯 Customer Segments", 
        "🚨 Anomaly Detections"
    ])
    
    # TAB 1: SALES FORECASTING
    with tab1:
        st.subheader("Sales & Revenue Forecasting (Random Forest Regressor)")
        if forecast_recs:
            # Parse metrics from first row
            metrics = json.loads(forecast_recs[0]['metrics_json'])
            
            # Print metrics
            cols = st.columns(3)
            cols[0].metric("MAE (Mean Absolute Error)", f"${metrics.get('MAE', 0):,.2f}")
            cols[1].metric("RMSE (Root MSE)", f"${metrics.get('RMSE', 0):,.2f}")
            cols[2].metric("R² Score (Coefficient of Det.)", f"{metrics.get('R2', 0):.3f}")
            
            # Build forecast series
            forecast_list = []
            for r in forecast_recs:
                val = json.loads(r['predicted_value'])
                forecast_list.append({
                    "Date": pd.to_datetime(val["Date"]),
                    "Revenue": val["ForecastedRevenue"],
                    "Type": "Forecasted"
                })
            forecast_df = pd.DataFrame(forecast_list)
            
            # Load historical sales
            history_df = biz_service.get_sales_chart_data(company_id, limit=90)
            history_df['Date'] = pd.to_datetime(history_df['Date'])
            history_df['Type'] = 'Historical'
            
            # Merge for charting
            chart_df = pd.concat([history_df[['Date', 'Revenue', 'Type']], forecast_df], ignore_index=True)
            chart_df = chart_df.sort_values('Date')
            
            fig = px.line(
                chart_df, 
                x='Date', 
                y='Revenue', 
                color='Type', 
                title='Historical vs 30-Day Sales Forecast',
                template='plotly_dark',
                color_discrete_map={'Historical': '#4f46e5', 'Forecasted': '#10b981'}
            )
            fig.update_layout(paper_bgcolor='rgba(0,0,0,0)', plot_bgcolor='rgba(0,0,0,0)')
            st.plotly_chart(fig, use_container_width=True)
        else:
            st.info("No forecasting data available.")
            
    # TAB 2: CHURN PREDICTION
    with tab2:
        st.subheader("Customer Attrition & Churn Analysis (Random Forest Classifier)")
        if churn_recs:
            metrics = json.loads(churn_recs[0]['metrics_json'])
            
            cols = st.columns(3)
            cols[0].metric("Classification Accuracy", f"{metrics.get('Accuracy', 0)*100:.1f}%")
            cols[1].metric("Precision Score", f"{metrics.get('Precision', 0)*100:.1f}%")
            cols[2].metric("Recall Score", f"{metrics.get('Recall', 0)*100:.1f}%")
            
            # Fetch churn ranks
            conn = biz_service._get_connection()
            risk_df = pd.read_sql_query("""
                SELECT c.name as Customer, c.email as Email, c.tenure_months as TenureMonths, c.total_spend as TotalSpend, p.probability as ChurnRisk
                FROM predictions p
                JOIN customers c ON p.source_id = c.id
                WHERE p.company_id = ? AND p.target_type = 'customer_churn'
                ORDER BY p.probability DESC
            """, conn, params=(company_id,))
            conn.close()
            
            st.markdown("#### High-Risk Churn Prospects")
            st.markdown("Customers with Churn risk score >= 50% require prompt re-engagement.")
            
            # Use Streamlit's native data editor with risk meter styling
            st.dataframe(
                risk_df,
                column_config={
                    "ChurnRisk": st.column_config.ProgressColumn(
                        "Risk Probability",
                        help="ML Churn probability risk rating",
                        format="%.1f%%",
                        min_value=0.0,
                        max_value=1.0
                    )
                },
                hide_index=True,
                use_container_width=True
            )
        else:
            st.info("No churn predictions available.")
            
    # TAB 3: CUSTOMER SEGMENTS
    with tab3:
        st.subheader("Customer Demographics Clustering (K-Means Clustering)")
        if segment_recs:
            metrics = json.loads(segment_recs[0]['metrics_json'])
            st.metric("Silhouette Coefficient Index", f"{metrics.get('SilhouetteScore', 0):.3f}")
            
            conn = biz_service._get_connection()
            cluster_df = pd.read_sql_query("""
                SELECT c.name as Customer, c.tenure_months as Tenure, c.total_spend as TotalSpend, p.predicted_value as ClusterLabel
                FROM predictions p
                JOIN customers c ON p.source_id = c.id
                WHERE p.company_id = ? AND p.target_type = 'segmentation'
            """, conn, params=(company_id,))
            conn.close()
            
            fig = px.scatter(
                cluster_df,
                x='Tenure',
                y='TotalSpend',
                color='ClusterLabel',
                hover_name='Customer',
                title='Customer Cluster Scatter (Tenure vs Spending)',
                template='plotly_dark',
                color_discrete_sequence=['#8b5cf6', '#10b981', '#ef4444']
            )
            fig.update_layout(paper_bgcolor='rgba(0,0,0,0)', plot_bgcolor='rgba(0,0,0,0)')
            st.plotly_chart(fig, use_container_width=True)
            
            st.markdown("#### Group Profile Details")
            st.dataframe(cluster_df, hide_index=True, use_container_width=True)
        else:
            st.info("No customer segmentation details available.")
            
    # TAB 4: ANOMALY DETECTIONS
    with tab4:
        st.subheader("Statistical Outlier & Anomaly Detection (Isolation Forest)")
        if anomaly_recs:
            metrics = json.loads(anomaly_recs[0]['metrics_json'])
            
            cols = st.columns(2)
            cols[0].metric("Total Flags Found", f"{metrics.get('AnomalyCount', 0)} events")
            cols[1].metric("Percent Contamination Rate", f"{metrics.get('AnomalyRate', 0)*100:.2f}%")
            
            conn = biz_service._get_connection()
            anomaly_rows = pd.read_sql_query("""
                SELECT s.date as Date, s.revenue as Revenue, s.orders_count as OrdersCount
                FROM predictions p
                JOIN sales s ON p.source_id = s.id
                WHERE p.company_id = ? AND p.target_type = 'anomaly' AND p.predicted_value = '1'
                ORDER BY s.date DESC
            """, conn, params=(company_id,))
            conn.close()
            
            st.markdown("#### Flagged Outlier Invoices")
            st.markdown("These sales logs represent statistical deviations (e.g. extremely high sales spikes or negative sales discrepancies).")
            if not anomaly_rows.empty:
                st.dataframe(anomaly_rows, hide_index=True, use_container_width=True)
            else:
                st.success("No anomalies flagged.")
        else:
            st.info("No transaction anomaly reports available.")
