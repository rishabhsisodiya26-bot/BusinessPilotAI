import streamlit as st
import pandas as pd
import plotly.express as px
from backend.api import BusinessService

def show_dashboard(company_id: int):
    st.markdown("## 📊 Executive BI Dashboard")
    st.markdown("Real-time business performance analytics, alerts, and descriptive trend aggregations.")
    
    service = BusinessService()
    kpis = service.get_dashboard_kpis(company_id)
    
    # Custom HTML metrics injection with styles
    col1, col2, col3, col4 = st.columns(4)
    
    with col1:
        rev_trend = f"+{kpis['revenue_change_pct']:.1f}%" if kpis['revenue_change_pct'] >= 0 else f"{kpis['revenue_change_pct']:.1f}%"
        trend_class = "positive" if kpis['revenue_change_pct'] >= 0 else "negative"
        st.markdown(f"""
            <div class="kpi-card">
                <div class="kpi-title">Total Revenue</div>
                <div class="kpi-value">${kpis['total_revenue']:,.2f}</div>
                <div class="kpi-delta {trend_class}">{rev_trend} vs prev 30d</div>
            </div>
        """, unsafe_allow_html=True)
        
    with col2:
        ords_trend = f"+{kpis['orders_change_pct']:.1f}%" if kpis['orders_change_pct'] >= 0 else f"{kpis['orders_change_pct']:.1f}%"
        trend_class = "positive" if kpis['orders_change_pct'] >= 0 else "negative"
        st.markdown(f"""
            <div class="kpi-card">
                <div class="kpi-title">Transactions</div>
                <div class="kpi-value">{kpis['total_orders']:,}</div>
                <div class="kpi-delta {trend_class}">{ords_trend} vs prev 30d</div>
            </div>
        """, unsafe_allow_html=True)
        
    with col3:
        # Load churn rate if customer predictions exist, else default to DB
        churn_recs = service.get_predictions_by_type(company_id, 'customer_churn')
        churn_rate = 0.0
        if churn_recs:
            churned = sum(1 for r in churn_recs if r['predicted_value'] == '1')
            total = len(churn_recs)
            churn_rate = (churned / total * 100) if total > 0 else 0.0
        else:
            # Fallback to general DB seed calculations
            conn = service._get_connection()
            cursor = conn.cursor()
            cursor.execute("SELECT COUNT(*) FROM customers WHERE company_id = ? AND status = 'Churned'", (company_id,))
            churned = cursor.fetchone()[0]
            cursor.execute("SELECT COUNT(*) FROM customers WHERE company_id = ?", (company_id,))
            total = cursor.fetchone()[0]
            churn_rate = (churned / total * 100) if total > 0 else 0.0
            conn.close()
            
        st.markdown(f"""
            <div class="kpi-card">
                <div class="kpi-title">Churn Rate</div>
                <div class="kpi-value">{churn_rate:.1f}%</div>
                <div class="kpi-delta" style="color: #94a3b8;">Active churn risk profile</div>
            </div>
        """, unsafe_allow_html=True)
        
    with col4:
        st.markdown(f"""
            <div class="kpi-card">
                <div class="kpi-title">Inventory Stock</div>
                <div class="kpi-value">{kpis['active_inventory']:,} units</div>
                <div class="kpi-delta" style="color: #94a3b8;">Warehouse units online</div>
            </div>
        """, unsafe_allow_html=True)
        
    # Charts Section
    st.subheader("📈 Revenue and Order Time-Series Trends")
    sales_df = service.get_sales_chart_data(company_id)
    
    if not sales_df.empty:
        # Build Plotly line chart
        fig = px.line(
            sales_df, 
            x='Date', 
            y='Revenue',
            title='Daily Sales Revenue Trend ($)',
            template='plotly_dark',
            color_discrete_sequence=['#6366f1']
        )
        fig.update_layout(
            paper_bgcolor='rgba(0,0,0,0)',
            plot_bgcolor='rgba(0,0,0,0)',
            font=dict(family='Outfit', size=12),
            xaxis=dict(showgrid=False),
            yaxis=dict(gridcolor='rgba(255,255,255,0.05)')
        )
        st.plotly_chart(fig, use_container_width=True)
    else:
        st.info("No historical sales records to plot.")
        
    # Bottom Section: Alerts & Products
    col_left, col_right = st.columns([1, 1])
    
    with col_left:
        st.subheader("⚠️ Stock Level Alerts")
        alerts = service.get_inventory_alerts(company_id)
        if alerts:
            for item in alerts:
                st.error(f"🚨 **{item['name']}** ({item['category']}) is low on stock! Current: **{item['current_stock']} units** (Reorder threshold: {item['reorder_point']})")
        else:
            st.success("All product stock levels are currently above reorder points.")
            
    with col_right:
        st.subheader("📦 Product Categories Summary")
        conn = service._get_connection()
        prod_cat_df = pd.read_sql_query("""
            SELECT category as Category, COUNT(*) as Count, SUM(current_stock) as TotalStock 
            FROM products 
            WHERE company_id = ? 
            GROUP BY category
        """, conn, params=(company_id,))
        conn.close()
        
        if not prod_cat_df.empty:
            st.dataframe(prod_cat_df, hide_index=True, use_container_width=True)
        else:
            st.info("No product catalogs registered.")
