import streamlit as st
import os
import pandas as pd
from backend.api import BusinessService
from utils.report_generator import ReportGenerator

DB_PATH = os.path.join(".", "database", "database.db")
REPORTS_DIR = os.path.join(".", "reports")

def show_reports_page(company_id: int):
    st.markdown("## 📋 Professional Report Archive")
    st.markdown("Download generated executive advice files or trigger direct raw tabular data extractions.")
    
    biz_service = BusinessService()
    reports = biz_service.get_saved_reports(company_id)
    
    tab1, tab2 = st.tabs(["📝 Executive PDFs", "💾 Raw Table Exports"])
    
    with tab1:
        st.subheader("Saved AI Advisor Summaries")
        
        if reports:
            for rep in reports:
                st.markdown(f"""
                    <div class="action-card">
                        <h4>📄 {rep['name']}</h4>
                        <p style="color: #94a3b8; font-size: 0.85rem;">Type: <strong>{rep['report_type']}</strong> | Log Date: {rep['created_at']}</p>
                        <p style="color: #e2e8f0; font-size: 0.9rem;">{rep['content_summary']}</p>
                    </div>
                """, unsafe_allow_html=True)
                
                # Dynamic PDF Compilation and Download
                # To avoid writing large files continuously, we compile on demand when download button clicked
                filename = f"report_{rep['name'].lower().replace(' ', '_').replace(':', '')[:15]}.pdf"
                pdf_path = os.path.join(REPORTS_DIR, filename)
                
                # Make simple download button compile reportlab pdf
                try:
                    ReportGenerator.generate_pdf_report(rep['name'], rep['content_summary'], pdf_path)
                    with open(pdf_path, "rb") as pdf_file:
                        st.download_button(
                            label=f"⬇️ Download {rep['name']} PDF",
                            data=pdf_file,
                            file_name=filename,
                            mime="application/pdf",
                            key=f"dl_{rep['created_at']}"
                        )
                except Exception as e:
                    st.error(f"Failed to generate download file: {e}")
        else:
            st.info("No saved summaries found. Run a chat query to generate consulting logs.")
            
    with tab2:
        st.subheader("Export SQLite Tables to CSV")
        st.markdown("Download active tables in flat CSV format for external analysis.")
        
        export_categories = {
            "Sales Aggregate History": "SELECT date, revenue, orders_count, inventory_level FROM sales WHERE company_id = ?",
            "Active Customer Registry": "SELECT name, email, tenure_months, total_spend, status FROM customers WHERE company_id = ?",
            "Active Product Catalog": "SELECT name, category, unit_cost, unit_price, current_stock FROM products WHERE company_id = ?",
            "Multi-Agent Execution Logs": "SELECT session_id, agent_name, input_query, output_response, latency_seconds, created_at FROM agent_logs"
        }
        
        choice = st.selectbox("Select Target Database Table", list(export_categories.keys()))
        query = export_categories[choice]
        
        if st.button(f"🚀 Prepare {choice} Export", use_container_width=True):
            with st.spinner("Extracting records from SQLite..."):
                filename = f"export_{choice.lower().replace(' ', '_')}.csv"
                export_path = os.path.join(REPORTS_DIR, filename)
                
                try:
                    if "?" in query:
                        # Feed company ID parameter
                        ReportGenerator.export_table_to_csv(
                            query.replace("?", str(company_id)), DB_PATH, export_path
                        )
                    else:
                        ReportGenerator.export_table_to_csv(query, DB_PATH, export_path)
                        
                    with open(export_path, "rb") as csv_file:
                        st.download_button(
                            label=f"⬇️ Download {choice} CSV",
                            data=csv_file,
                            file_name=filename,
                            mime="text/csv",
                            key="csv_dl_btn"
                        )
                    st.success("CSV table extraction prepared successfully!")
                except Exception as e:
                    st.error(f"Export failed: {e}")
stream_path = REPORTS_DIR
if not os.path.exists(stream_path):
    os.makedirs(stream_path)
