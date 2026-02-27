import streamlit as st
from components.header import show_header

from utils.session_state import init_session_state

# MUST be the FIRST Streamlit-related call
init_session_state()
show_header()

st.header("⚙️ Settings")
st.write("This is the Settings  page – ready to use!")
st.info("Enter your credentials below.")

st.subheader("Backend")
st.session_state.backend_url = st.text_input("Backend URL", st.session_state.backend_url)
st.session_state.api_key = st.text_input("API Key", st.session_state.api_key, type="password")
st.session_state.workspace_id = st.text_input("Workspace ID", st.session_state.workspace_id)

st.subheader("GitHub")
st.session_state.github_pat = st.text_input("GitHub PAT (repo scope)", st.session_state.github_pat, type="password")
if st.button("Preview PR Comment"):
    st.code(f"Would post comment using PAT: {st.session_state.github_pat[:8]}…", language="text")

st.subheader("Appearance")
theme = st.radio("Theme", ["dark", "light"], index=0 if st.session_state.theme == "dark" else 1)
if theme != st.session_state.theme:
    st.session_state.theme = theme
    st.success("Theme changed (restart app to see full effect)")

st.caption("VS Code integration: launch via the minimal extension (see README)")