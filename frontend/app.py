import streamlit as st
import os

# Set page config as the very first Streamlit call
st.set_page_config(
    page_title="BusinessPilotAI - Agentic BI Platform",
    page_icon="🚀",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Load Custom Premium Stylesheet
def local_css(file_name):
    if os.path.exists(file_name):
        with open(file_name, "r") as f:
            st.markdown(f"<style>{f.read()}</style>", unsafe_allow_html=True)

# Path resolves from execution root
local_css("./frontend/styles.css")

# Import Views
from frontend.views.auth_view import show_auth_page
from frontend.views.dashboard import show_dashboard
from frontend.views.upload import show_upload_page
from frontend.views.predictions import show_predictions_page
from frontend.views.chat import show_chat_page
from frontend.views.reports import show_reports_page
from frontend.views.settings import show_settings_page

def main():
    # 1. Authentication Gating
    if 'user' not in st.session_state:
        show_auth_page()
        return

    # Extract user contexts
    user = st.session_state['user']
    company = user.get('company', {})
    company_id = company.get('id', 1)
    company_name = company.get('name', 'My Company')
    
    # 2. Sidebar Navigation UI
    st.sidebar.markdown(f"""
        <div style="text-align: center; margin-bottom: 20px;">
            <h3 style="color: #6366f1; margin-bottom: 5px;">🚀 BusinessPilotAI</h3>
            <span style="color: #94a3b8; font-size: 0.85rem;">Agentic Decision Support</span><br>
            <span style="color: #10b981; font-size: 0.8rem; font-weight:600;">● Active Session</span>
        </div>
    """, unsafe_allow_html=True)
    
    # User Profile Card
    st.sidebar.markdown(f"""
        <div style="background: rgba(30, 41, 59, 0.45); border: 1px solid rgba(255, 255, 255, 0.05); padding: 12px; border-radius: 8px; margin-bottom: 20px;">
            <div style="color: #94a3b8; font-size: 0.75rem; text-transform: uppercase;">Company Workspace</div>
            <div style="color: #ffffff; font-weight: 600; font-size: 0.95rem;">{company_name}</div>
            <div style="color: #64748b; font-size: 0.8rem; margin-top: 5px;">User: <strong>{user['username']}</strong> ({user['role']})</div>
        </div>
    """, unsafe_allow_html=True)
    
    # Navigation Radio Buttons
    menu_options = [
        "📊 Dashboard",
        "📥 Dataset Upload",
        "🤖 Predictive Intelligence",
        "💬 Agentic Chat",
        "📋 Report Archive",
        "⚙️ Settings"
    ]
    choice = st.sidebar.radio("Navigation Menu", menu_options)
    
    # 3. View Routing
    if choice == "📊 Dashboard":
        show_dashboard(company_id)
    elif choice == "📥 Dataset Upload":
        show_upload_page(company_id)
    elif choice == "🤖 Predictive Intelligence":
        show_predictions_page(company_id)
    elif choice == "💬 Agentic Chat":
        show_chat_page(company_id)
    elif choice == "📋 Report Archive":
        show_reports_page(company_id)
    elif choice == "⚙️ Settings":
        show_settings_page()
        
    # Injected footer
    st.markdown("""
        <div class="footer">
            BusinessPilotAI &copy; 2026 - Agentic Business Intelligence Platform | Powered by Machine Learning & GPT-4o
        </div>
    """, unsafe_allow_html=True)

if __name__ == "__main__":
    main()
