import streamlit as st

def success(msg):
    st.success(msg, icon="✅")

def error(msg):
    st.error(msg, icon="❌")

def info(msg):
    st.info(msg, icon="ℹ️")