# frontend-streamlit/main.py
import streamlit as st
from utils.session_state import init_session_state

# Initialize session state FIRST
init_session_state()

st.set_page_config(
    page_title="SambaNova Code Agent",
    page_icon="🧠",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Load CSS
try:
    with open("style.css", encoding="utf-8") as f:
        st.markdown(f"<style>{f.read()}</style>", unsafe_allow_html=True)
except FileNotFoundError:
    st.warning("style.css not found")

# Import health check
from utils.api import check_backend_health

# ─── SIDEBAR ────────────────────────────────────────────────────────────
with st.sidebar:
    # Logo at top (centered, larger)
    try:
        st.image("assets/image.png", width=160)
        st.markdown("<div style='text-align: center; margin-top: -10px;'><small>Powered by</small></div>", unsafe_allow_html=True)
    except:
        st.caption("Logo not found – assets/image.png")

    st.markdown("<h3 style='text-align: center; color: var(--primary); margin: 0.5rem 0;'>SambaNova Agent</h3>", unsafe_allow_html=True)
    st.caption("Multimodal • Real-time • Powered by SambaNova", unsafe_allow_html=True)

    st.markdown("---")

    # Clean, consistent navigation with icons
    page = st.radio(
        label="Navigation",
        options=[
            "🏠 Home",
            "🔍 Code Analysis",
            "📸 Screenshot Analysis",
            "🎙️ Audio Transcription",
            "🛠️ Actions & Fixes",
            "⚙️ Settings"
        ],
        index=0,
        format_func=lambda x: x,  # keep full text with emojis
        label_visibility="collapsed",
        key="navigation_radio"
    )

    st.markdown("---")

    # Health status card
    health = check_backend_health()
    if health.get("status") == "healthy":
        st.success("Backend Connected", icon="✅")
    else:
        st.error("Backend Offline", icon="⚠️")

    # Reset button at bottom
    if st.button("🔄 Reset Session", type="secondary", use_container_width=True):
        for key in list(st.session_state.keys()):
            del st.session_state[key]
        init_session_state()
        st.rerun()

# ─── PAGE ROUTING – just import (no .run()) ─────────────────────────────
if page == "🏠 Home":
    import pages.Home

elif page == "🔍 Code Analysis":
    import pages.Code_Analysis

elif page == "📸 Screenshot Analysis":
    import pages.Screenshot_Analysis

elif page == "🎙️ Audio / Meeting":
    import pages.Audio_Transcription

elif page == "🛠️ Actions & Fixes":
    import pages.Actions_Fixes

elif page == "⚙️ Settings":
    import pages.Settings