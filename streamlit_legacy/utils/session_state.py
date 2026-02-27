# frontend-streamlit/utils/session_state.py
import streamlit as st
import os

def init_session_state():
    """
    Initialize all session state keys with safe defaults.
    Uses environment variables as override if present.
    """
    defaults = {
        "backend_url": os.getenv("SAMBANOVA_BACKEND_URL", "http://localhost:8000"),
        "api_key": os.getenv("SAMBANOVA_API_KEY", ""),
        "workspace_id": "default",
        "github_pat": "",
        "last_analysis": None,
        "last_screenshot": None,
        "last_audio": None,
        "last_actions_result": None,
        "analysis_query": "",
        "theme": "dark",
        "chat_history": [],
        "selected_file": None,
        "show_logo": True,
    }

    for key, value in defaults.items():
        if key not in st.session_state:
            st.session_state[key] = value

    # # Optional: You can also load from st.secrets if you want more security
    # # (create .streamlit/secrets.toml file in frontend-streamlit folder)
    # if "SAMBANOVA_BACKEND_URL" in st.secrets:
    #     st.session_state.backend_url = st.secrets["SAMBANOVA_BACKEND_URL"]
    # if "SAMBANOVA_API_KEY" in st.secrets:
    #     st.session_state.api_key = st.secrets["SAMBANOVA_API_KEY"]