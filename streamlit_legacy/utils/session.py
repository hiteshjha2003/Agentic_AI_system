# Simple session state helpers
import streamlit as st

def init_session():
    defaults = {
        "analysis_result": None,
        "suggested_actions": [],
        "chat_history": [],
        "workspace_id": "default",
        "selected_file": None,
    }
    for k, v in defaults.items():
        if k not in st.session_state:
            st.session_state[k] = v