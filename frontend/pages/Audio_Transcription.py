import streamlit as st
from utils.api import ingest_audio
from components.status_messages import success
from components.header import show_header
from utils.session_state import init_session_state

# MUST be the FIRST Streamlit-related call
init_session_state()
show_header()

st.header("🎙️ Audio / Meeting Transcription")
st.write("This is the Audio Meeting Transcription Analysis page – ready to use!")
st.info("Enter your query below and click Run Analysis.")

uploaded = st.file_uploader("Upload meeting audio", type=["wav","mp3"])
participants = st.text_input("Participants (comma-separated)")

if uploaded and st.button("Transcribe & Extract Actions"):
    result = ingest_audio(uploaded.getvalue(), participants)
    if result:
        success("Transcription complete")
        st.markdown("**Transcription**")
        st.write(result.get("transcription", ""))
        st.subheader("Action Items")
        for a in result.get("action_items", []):
            st.write(f"- {a.get('text')} (confidence: {a.get('confidence')})")