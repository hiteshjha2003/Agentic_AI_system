import streamlit as st
from utils.api import execute_actions
from components.status_messages import success
from components.header import show_header
from utils.session_state import init_session_state

# MUST be the FIRST Streamlit-related call
init_session_state()
show_header()

st.header("🛠️ Actions & Fixes")
st.write("This is the Actions and Fixes Analysis page – ready to use!")
st.info("Enter your query below and click Run Analysis.")

if "last_analysis" in st.session_state:
    res = st.session_state.last_analysis
    
    # Safety check: skip if result is invalid/None
    if res is None or not isinstance(res, dict):
        st.warning("No valid analysis result found. Please run an analysis first on the Code Analysis page.")
    else:
        actions = res.get("suggested_actions", [])
        if not actions:
            st.info("No suggested actions from the last analysis.")
        else:
            selected = st.multiselect(
                "Select actions to execute",
                [a.get("description", "Unnamed action") for a in actions],
                key="action_select"
            )

            if st.button("Execute Selected Actions", type="primary"):
                payload = [a for a in actions if a.get("description") in selected]
                result = execute_actions(payload)
                if result:
                    success("Actions executed")
                    st.json(result)
                else:
                    st.error("Execution failed – check backend logs")
else:
    st.info("Run an analysis first on the Code Analysis page to see suggested actions.")