import streamlit as st

def show_settings_page():
    st.markdown("## ⚙️ App Settings & API Configurations")
    st.markdown("Manage credentials, connect external model configurations, and view account roles.")
    
    user = st.session_state.get('user', {})
    
    col1, col2 = st.columns([2, 1])
    
    with col1:
        st.subheader("🤖 API Key Integration")
        st.markdown(
            "By default, the platform runs in **Hybrid Mode** with standard pre-configured local heuristics. "
            "To activate full **GPT-4o Agent Reasoning**, paste your OpenAI API Key below."
        )
        
        # Pull cached API Key
        saved_key = st.session_state.get('openai_api_key', "")
        
        api_key = st.text_input(
            "OpenAI API Key (starts with sk-...)", 
            value=saved_key, 
            type="password", 
            help="Your OpenAI API Key will be temporarily cached in the active session memory only."
        )
        
        if st.button("Save API Configuration", use_container_width=True):
            st.session_state['openai_api_key'] = api_key.strip()
            if api_key.strip():
                st.success("OpenAI API Key saved to session. Full GPT-4o Mode enabled!")
            else:
                st.info("API Key cleared. Local Hybrid Fallback Engine enabled.")
                
    with col2:
        st.subheader("👤 User Profile")
        if user:
            st.markdown(f"""
                <div class="action-card">
                    <p style="margin-bottom:6px;"><strong>Username:</strong> {user.get('username')}</p>
                    <p style="margin-bottom:6px;"><strong>Email:</strong> {user.get('email')}</p>
                    <p style="margin-bottom:6px;"><strong>Role:</strong> <span class="badge badge-active">{user.get('role')}</span></p>
                    <p style="margin-bottom:0px;"><strong>Company:</strong> {user.get('company', {}).get('name', 'None')}</p>
                </div>
            """, unsafe_allow_html=True)
            
            if st.button("Log Out Workspace", use_container_width=True):
                # Clear all user session states
                for key in list(st.session_state.keys()):
                    del st.session_state[key]
                st.rerun()
        else:
            st.info("No active session details.")
