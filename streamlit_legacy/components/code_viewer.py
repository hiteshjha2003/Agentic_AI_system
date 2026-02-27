import streamlit as st

def render_code_viewer(code: str, language: str = "python"):
    st.code(code, language=language)