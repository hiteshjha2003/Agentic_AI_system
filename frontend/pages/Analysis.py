# frontend-streamlit/pages/0_Analysis_Dashboard.py
import streamlit as st
from datetime import datetime
from components.chat_interface import render_chat
from components.header import show_header
from utils.session_state import init_session_state

# MUST be the FIRST Streamlit-related call
init_session_state()

show_header()

st.set_page_config(page_title="Analysis Dashboard", layout="wide")

st.title("📊 Analysis Dashboard")
st.markdown("Central overview of all recent analyses. Chat with results below.")

# ────────────────────────────────────────────────
# Helper to show "No data yet" card
# ────────────────────────────────────────────────
def empty_card(title: str, icon: str = "ℹ️"):
    with st.container(border=True):
        st.markdown(f"### {icon} {title}")
        st.info("No result yet. Run the corresponding analysis first.")
        st.caption(f"Last checked: {datetime.now().strftime('%H:%M:%S')}")

# ────────────────────────────────────────────────
# Layout: Two columns for overview
# ────────────────────────────────────────────────
col_left, col_right = st.columns([2, 1])

# ─── LEFT: Summary Cards ──────────────────────────────────────────────
with col_left:
    st.subheader("Latest Results")

    # 1. Code Analysis
    if "last_analysis" in st.session_state and st.session_state.last_analysis:
        res = st.session_state.last_analysis
        with st.expander("🔍 Code Analysis – Latest", expanded=True):
            st.markdown(f"**Query:** {res.get('query', '—')}")
            st.markdown(f"**Type:** {res.get('analysis_type', '—')}")
            st.markdown("**Summary**")
            st.markdown(res.get("summary", "No summary"))
            if st.button("View Full Details →", key="code_full"):
                st.switch_page("pages/Code_Analysis.py")
    else:
        empty_card("Code Analysis")

    # 2. Screenshot
    if "last_screenshot" in st.session_state and st.session_state.last_screenshot:
        res = st.session_state.last_screenshot
        with st.expander("📸 Screenshot Analysis – Latest", expanded=False):
            st.markdown(f"**Source:** {res.get('source', '—')}")
            st.markdown("**Extracted Text**")
            st.code(res.get("combined_extracted_text", "—")[:500] + "...", language=None)
            st.caption(f"Language: {res.get('detected_language', 'unknown')}")
    else:
        empty_card("Screenshot Analysis")

    # 3. Audio Transcription
    if "last_audio" in st.session_state and st.session_state.last_audio:
        res = st.session_state.last_audio
        with st.expander("🎙️ Audio Transcription – Latest", expanded=False):
            st.markdown("**Transcription**")
            st.markdown(res.get("transcription", "No transcription")[:600] + "...")
            if res.get("action_items"):
                st.markdown("**Detected Action Items**")
                for item in res["action_items"]:
                    st.write(f"- {item.get('text', '—')}")
    else:
        empty_card("Audio Transcription")

    # 4. Actions / Fixes (last executed or suggested)
    if "last_actions_result" in st.session_state and st.session_state.last_actions_result:
        res = st.session_state.last_actions_result
        with st.expander("🛠️ Actions & Fixes – Latest Execution", expanded=False):
            st.json(res)
    elif "last_analysis" in st.session_state and st.session_state.last_analysis:
        with st.expander("🛠️ Suggested Actions (from last analysis)", expanded=False):
            acts = st.session_state.last_analysis.get("suggested_actions", [])
            if acts:
                for act in acts:
                    st.markdown(f"**{act.get('action_type','—').upper()}** → {act.get('target_file','—')}")
                    st.caption(act.get("description", "—"))
            else:
                st.info("No actions suggested yet.")
    else:
        empty_card("Actions & Fixes")

# ─── RIGHT: Central Chat ──────────────────────────────────────────────
with col_right:
    st.subheader("💬 Ask about any result")
    st.caption("Chat with the latest analysis outputs (code, screenshot, audio, actions)")

    # Simple combined context from all features
    chat_context = ""
    if "last_analysis" in st.session_state and st.session_state.last_analysis:
        chat_context += f"Latest code analysis summary: {st.session_state.last_analysis.get('summary','')}\n"
    if "last_screenshot" in st.session_state and st.session_state.last_screenshot:
        chat_context += f"Screenshot text: {st.session_state.last_screenshot.get('combined_extracted_text','')[:300]}\n"
    if "last_audio" in st.session_state and st.session_state.last_audio:
        chat_context += f"Latest transcription: {st.session_state.last_audio.get('transcription','')[:300]}\n"

    render_chat(initial_context=chat_context.strip() or "No recent analysis data yet.")

# Footer / refresh hint
st.markdown("---")
st.caption("Refresh page or run new analysis to update dashboard.")
if st.button("Refresh Dashboard", type="secondary"):
    st.rerun()