import streamlit as st

def render_diff(diff_text: str):
    st.code(diff_text, language="diff")