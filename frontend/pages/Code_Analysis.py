import streamlit as st
from utils.api import analyze, ingest_codebase
from components.diff_renderer import render_diff
from utils.helpers import download_markdown, download_pdf
from components.status_messages import success, error
from datetime import datetime
from utils.session_state import init_session_state

init_session_state()

st.header("🔍 Code Analysis")
st.write("Upload or select a repository to analyze.")

# ======================================================
# 1️⃣ Repository Ingestion Section
# ======================================================

st.subheader("📁 Repository Setup")

repo_path = st.text_input(
    "Enter full repository folder path",
    placeholder="/Users/hiteshj/Desktop/my_project"
)

if st.button("📥 Ingest Repository"):
    if not repo_path:
        error("Please provide repository path")
    else:
        with st.spinner("Ingesting repository..."):
            result = ingest_codebase(repo_path)

            if result and "error" not in result:
                success("Repository ingestion started successfully")
                st.session_state.repo_ingested = True
            else:
                error(result.get("error", "Failed to ingest repository"))

# ======================================================
# 2️⃣ Code Analysis Section
# ======================================================

if st.session_state.get("repo_ingested", False):

    st.divider()
    st.subheader("🧠 Run Analysis")

    query = st.text_area(
        "What should the agent do?",
        height=150,
        placeholder="Debug this 500 error…"
    )

    analysis_type = st.selectbox(
        "Goal",
        ["debug", "review", "refactor", "explain", "test_generate"]
    )

    if st.button("🚀 Run Analysis", type="primary"):
        if not query:
            error("Please enter a query")
        else:
            with st.spinner("Running AI analysis..."):
                result = analyze(
                    query=query,
                    analysis_type=analysis_type,
                    include_codebase=True
                )

                if result and "error" not in result:
                    st.session_state.last_analysis = result
                    success("Analysis complete")
                else:
                    error(result.get("error", "Analysis failed"))

# ======================================================
# 3️⃣ Display Results
# ======================================================

if st.session_state.get("last_analysis"):

    res = st.session_state.last_analysis

    if not isinstance(res, dict):
        st.warning("Invalid analysis result.")
        st.stop()


    st.subheader("Summary")
    st.markdown(res.get("summary", "No summary available"))

    with st.expander("Detailed Analysis", expanded=True):
        st.markdown(res.get("detailed_analysis", "No detailed analysis available"))

    st.subheader("Suggested Actions")

    for act in res.get("suggested_actions", []):
        with st.expander(
            f"{act.get('action_type','ACTION').upper()} → "
            f"{act.get('target_file','Unknown')} "
            f"({act.get('confidence',0):.0%})"
        ):
            st.markdown(act.get("reasoning", "No reasoning provided"))

            if act.get("diff"):
                render_diff(act["diff"])

            if act.get("new_content"):
                st.code(act["new_content"], language="python")

    if res.get("detailed_analysis"):
        col1, col2 = st.columns(2)
        with col1:
            download_markdown(
                res["detailed_analysis"],
                f"analysis_{datetime.now():%Y%m%d}.md"
            )
        with col2:
            download_pdf(
                res["detailed_analysis"],
                f"analysis_{datetime.now():%Y%m%d}.pdf"
            )
