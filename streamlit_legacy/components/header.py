import streamlit as st

def show_header():
    try:
        st.image("assets/image.png", width=220)
    except:
        st.caption("Logo missing – expected in assets/image.png")
    st.markdown("---")