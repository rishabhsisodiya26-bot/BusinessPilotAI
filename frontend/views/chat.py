import streamlit as st
import time
import pandas as pd
from agents.ceo_agent import CEOAgent
from backend.api import BusinessService

def show_chat_page(company_id: int):
    st.markdown("## 💬 AI Business Consultant Chat")
    st.markdown("Query the Agentic AI Team. The CEO Agent coordinates sub-agents to analyze data, fit models, and compile advice.")
    
    biz_service = BusinessService()
    
    # Check if user has dynamically configured an API key in settings
    api_key = st.session_state.get('openai_api_key', None)
    
    # 1. Chat Prompt Shortcuts
    st.markdown("💡 **Ask the Consultants:**")
    shortcut_cols = st.columns(3)
    query_to_run = ""
    
    with shortcut_cols[0]:
        if st.button("Why are sales dropping?", use_container_width=True):
            query_to_run = "Why are sales dropping? Check trends and anomalies."
            
    with shortcut_cols[1]:
        if st.button("Which customers may leave?", use_container_width=True):
            query_to_run = "Which customers are at risk of churn? Show retention strategy."
            
    with shortcut_cols[2]:
        if st.button("How can I increase profit?", use_container_width=True):
            query_to_run = "How can we optimize profit margins, pricing, and inventory levels?"
            
    # Text input
    user_query = st.chat_input("Type your question for the business advisor team here...")
    
    if user_query:
        query_to_run = user_query
        
    if query_to_run:
        # Render User message
        st.markdown(f"""
            <div class="chat-container">
                <div class="chat-bubble user">
                    <div class="chat-sender">You</div>
                    <div>{query_to_run}</div>
                </div>
            </div>
        """, unsafe_allow_html=True)
        
        # Show progression spinner
        with st.status("🧠 Orchestrating AI Consultant Team...", expanded=True) as status:
            time.sleep(0.5)
            status.update(label="📅 CEO Agent parsing prompt & delegating tasks...", state="running")
            time.sleep(0.6)
            status.update(label="📊 Data Analyst Agent inspecting database tables & running EDA...", state="running")
            time.sleep(0.6)
            status.update(label="🤖 ML Prediction Agent loading cached models & verifying metrics...", state="running")
            time.sleep(0.6)
            status.update(label="💼 Business Advisor Agent compiling SWOT analysis & recommendations...", state="running")
            time.sleep(0.5)
            
            # Execute workflow
            ceo = CEOAgent()
            if api_key:
                ceo.set_api_key(api_key)
                
            result = ceo.execute_workflow(query_to_run, company_id=company_id)
            status.update(label="✅ Summary Synthesis Complete!", state="complete")
            
        # Render Agent response
        st.markdown("---")
        st.markdown(result['executive_summary'])
        
        # Save generated report automatically to history
        biz_service.save_report_meta(
            company_id=company_id,
            name=f"AI Consult: {query_to_run[:25]}...",
            report_type="Executive Summary",
            file_path=f"chat_sess_{result['session_id'][:8]}.txt",
            summary=result['executive_summary'][:300] + "..."
        )
        
        # Agent execution timeline logs
        st.markdown("---")
        with st.expander("🕵️ Agent Audit Execution Timeline (Audit Logs)", expanded=False):
            st.markdown(f"""
                <div class="log-step">
                    <strong>CEOAgent Initialized</strong><br>
                    Query: <em>"{query_to_run}"</em><br>
                    Session ID: <code>{result['session_id']}</code>
                </div>
                <div class="log-step">
                    <strong>DataAnalystAgent Action</strong><br>
                    Descriptive statistics, data cleaning, and missing value checks completed.
                </div>
                <div class="log-step">
                    <strong>MLPredictionAgent Action</strong><br>
                    Regression forecasts, binary classification metrics, cluster profiles, and anomaly rates retrieved.
                </div>
                <div class="log-step">
                    <strong>BusinessAdvisorAgent Action</strong><br>
                    SWOT matrices, risk assessments, and marketing/fulfillment checklists structured.
                </div>
                <div class="log-step">
                    <strong>CEOAgent Synthesis Complete</strong><br>
                    Compiled insights into Unified Executive Summary. Total execution time: <code>{result['total_latency']:.2f}s</code>.
                </div>
            """, unsafe_allow_html=True)
            
    # Show history of audit logs below
    st.markdown("---")
    st.subheader("📋 Historical Agent Execution Log Audit")
    audit_logs = biz_service.get_agent_audit_logs()
    
    if audit_logs:
        log_list = []
        for l in audit_logs[:10]:
            log_list.append({
                "Timestamp": l['created_at'],
                "Agent": l['agent_name'],
                "Query": l['input_query'][:40] + "...",
                "Latency": f"{l['latency_seconds']:.2f}s"
            })
        st.dataframe(pd.DataFrame(log_list), hide_index=True, use_container_width=True)
    else:
        st.info("No prior agent logs found in audit tables.")
