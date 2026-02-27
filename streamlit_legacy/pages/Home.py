# frontend-streamlit/pages/Home.py
import streamlit as st

st.title("🚀 Welcome to SambaNova Code Agent")
st.markdown("Your AI-powered multimodal code companion — debug, review, refactor, and understand faster.")

# Hero section
st.markdown("""
<div style="text-align: center; padding: 2rem 0; background: linear-gradient(135deg, #1e293b, #0f172a); border-radius: 16px; margin: 2rem 0;">
    <h2 style="color: #818cf8;">Analyze smarter. Build better.</h2>
    <p style="font-size: 1.2rem; color: #94a3b8; max-width: 800px; margin: 1rem auto;">
        Code, screenshots, audio meetings — all in one place, powered by SambaNova.
    </p>
</div>
""", unsafe_allow_html=True)

# Quick action cards
st.subheader("Get Started")
cols = st.columns(3)

with cols[0]:
    with st.container(border=True):
        st.markdown("### 🔍 Code Analysis")
        st.caption("Debug, review, refactor, explain, generate tests")
        if st.button("Start Code Analysis", use_container_width=True, key="home_code"):
            st.switch_page("pages/Code_Analysis.py")

with cols[1]:
    with st.container(border=True):
        st.markdown("### 📸 Screenshot Analysis")
        st.caption("Upload error screens, UI, terminal output")
        if st.button("Start Screenshot", use_container_width=True, key="home_ss"):
            st.switch_page("pages/Screenshot_Analysis.py")

with cols[2]:
    with st.container(border=True):
        st.markdown("### 🎙️ Audio / Meeting")
        st.caption("Transcribe discussions, extract actions")
        if st.button("Start Audio", use_container_width=True, key="home_audio"):
            st.switch_page("pages/Audio_Transcription.py")

# Status / tips
st.markdown("---")
col1, col2 = st.columns(2)
with col1:
    st.info("Backend connected → Ready to analyze")
with col2:
    st.caption("Tip: Use Settings to change backend URL or API key")

st.markdown("<div style='text-align: center; padding: 2rem 0; color: #94a3b8;'>Choose a tool from the sidebar or click above to begin.</div>", unsafe_allow_html=True)