import streamlit as st
from backend.auth import AuthService

def show_auth_page():
    st.markdown('<div class="action-card">', unsafe_allow_html=True)
    st.markdown("<h2 style='text-align: center; color: #ffffff;'>🚀 BusinessPilotAI</h2>", unsafe_allow_html=True)
    st.markdown("<p style='text-align: center; color: #94a3b8;'>Agentic Business Intelligence Platform for Autonomous Decision Support</p>", unsafe_allow_html=True)
    st.markdown('</div>', unsafe_allow_html=True)
    
    auth_service = AuthService()
    tab1, tab2 = st.tabs(["🔒 Secure Login", "📝 Create Account"])
    
    with tab1:
        st.subheader("Login to your Workspace")
        login_user = st.text_input("Username or Email", key="login_user_input")
        login_pass = st.text_input("Password", type="password", key="login_pass_input")
        
        if st.button("Log In", use_container_width=True):
            if login_user and login_pass:
                success, response = auth_service.login_user(login_user, login_pass)
                if success:
                    st.session_state['user'] = response
                    st.success(f"Welcome back, {response['username']}!")
                    time_refresh = st.empty()
                    st.rerun()
                else:
                    st.error(response)
            else:
                st.warning("Please enter your credentials.")
                
    with tab2:
        st.subheader("Register a new Business Profile")
        reg_user = st.text_input("Username", key="reg_user_input")
        reg_email = st.text_input("Email Address", key="reg_email_input")
        reg_pass = st.text_input("Password", type="password", key="reg_pass_input")
        reg_role = st.selectbox("Role", ["Analyst", "Manager", "Administrator"], key="reg_role_select")
        
        if st.button("Sign Up", use_container_width=True):
            if reg_user and reg_email and reg_pass:
                success, msg = auth_service.register_user(reg_user, reg_email, reg_pass, reg_role)
                if success:
                    st.success(msg + " Please log in under the Login tab.")
                else:
                    st.error(msg)
            else:
                st.warning("All registration inputs are required.")
