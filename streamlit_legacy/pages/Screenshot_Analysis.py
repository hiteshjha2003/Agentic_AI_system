import streamlit as st
from PIL import Image
from streamlit_cropper import st_cropper
from utils.api import ingest_screenshot
from components.status_messages import success, error
from components.header import show_header
from utils.session_state import init_session_state
import io

# -------------------------------
# Initialize
# -------------------------------
init_session_state()
show_header()

st.header("📸 Screenshot Analysis")
st.caption(
    "Upload a screenshot → get text extraction, layout description, issue classification & more"
)

uploaded = st.file_uploader(
    "Upload screenshot",
    type=["png", "jpg", "jpeg", "webp"]
)

if uploaded:
    try:
        img = Image.open(uploaded)
        st.image(img, caption="Original Screenshot", use_column_width=True)

        crop = st.checkbox("Crop before analysis", value=False)

        # -------------------------------
        # Cropping Logic
        # -------------------------------
        if crop:
            cropped_img = st_cropper(
                img,
                realtime_update=True,
                box_color="#6366f1"
            )

            if (
                cropped_img is None
                or cropped_img.size[0] <= 0
                or cropped_img.size[1] <= 0
            ):
                st.warning("Invalid crop dimensions – using original image")
                display_img = img
            else:
                display_img = cropped_img
        else:
            display_img = img

        context = st.text_input(
            "Optional context (e.g., 'VS Code error', 'Terminal output')",
            ""
        )

        # -------------------------------
        # Analyze Button
        # -------------------------------
        if st.button("🚀 Analyze Screenshot", type="primary"):

            with st.spinner("Preparing and uploading..."):

                try:
                    if (
                        display_img.size[0] <= 0
                        or display_img.size[1] <= 0
                    ):
                        raise ValueError("Image has invalid dimensions")

                    # Convert to PNG bytes
                    buffered = io.BytesIO()
                    display_img.save(
                        buffered,
                        format="PNG",
                        optimize=True
                    )
                    bytes_data = buffered.getvalue()

                    # Call backend
                    result = ingest_screenshot(bytes_data, context)

                    # DEBUG (optional)
                    # st.json(result)

                    if not result:
                        error("No response from backend")
                        st.stop()

                    analysis = result.get("analysis", {})

                    # ✅ FIXED STATUS CHECK
                    if analysis.get("status") == "success":

                        success(f"Processed! ID: {result.get('id')}")

                        vision = analysis.get("vision_analysis", {})

                        # -------------------------------
                        # Extracted Text
                        # -------------------------------
                        st.subheader("📝 Extracted Text")

                        extracted_raw = vision.get(
                            "extracted_text",
                            "No text extracted"
                        )

                        if isinstance(extracted_raw, list):
                            extracted_text = "\n".join(
                                str(line)
                                for line in extracted_raw
                                if line
                            )
                        else:
                            extracted_text = str(extracted_raw)

                        if extracted_text.strip():
                            st.markdown(extracted_text)
                        else:
                            st.markdown("[No readable text found]")

                        # -------------------------------
                        # Detailed Explanation
                        # -------------------------------
                        detailed = analysis.get("detailed_explanation") or vision.get("detailed_explanation")
                        if detailed:
                            st.subheader("📖 Detailed Explanation")
                            st.markdown(detailed)
                            
                        # -------------------------------
                        # Architectural Components
                        # -------------------------------
                        components = analysis.get("architectural_components") or vision.get("architectural_components")
                        if components:
                            st.subheader("🏗️ Architectural Components")
                            cols = st.columns(min(len(components), 3))
                            for i, comp in enumerate(components):
                                cols[i % 3].info(comp)

                        # -------------------------------
                        # Layout Description
                        # -------------------------------
                        st.subheader("🖼️ Layout & Visual Description")
                        st.markdown(
                            vision.get(
                                "layout_description",
                                "No description available"
                            )
                        )

                        # -------------------------------
                        # Issue Classification
                        # -------------------------------
                        issue = analysis.get(
                            "issue_classification",
                            {}
                        )

                        if issue and issue.get("type") != "unknown":
                            st.subheader("⚠️ Issue Classification")
                            col1, col2 = st.columns(2)

                            col1.metric(
                                "Type",
                                issue.get("type", "—")
                            )
                            col2.metric(
                                "Severity",
                                issue.get("severity", "—")
                            )

                        # -------------------------------
                        # Hypotheses
                        # -------------------------------
                        hypotheses = analysis.get(
                            "hypotheses",
                            []
                        )

                        if hypotheses:
                            st.subheader("💡 Hypotheses / Suggestions")
                            for hyp in hypotheses:
                                st.markdown(f"- {hyp}")

                        # -------------------------------
                        # Debug JSON
                        # -------------------------------
                        with st.expander("Raw Response (debug)"):
                            st.json(result)

                        st.session_state.last_screenshot = result

                    else:
                        error(
                            result.get(
                                "error",
                                "Backend returned non-success status"
                            )
                        )
                        with st.expander("Debug Response"):
                            st.json(result)

                except Exception as e:
                    error(f"Processing failed: {str(e)}")

    except Exception as e:
        error(f"Failed to load image: {str(e)}")

st.caption(
    "Tip: Crop to focus on code/error area. Max size ~2048px recommended."
)
