# frontend-streamlit/utils/helpers.py
import streamlit as st
from io import BytesIO
from datetime import datetime

def download_markdown(text: str, filename: str = "analysis.md", key_suffix: str = "md"):
    """
    Safe Markdown download with unique key and timestamped filename.
    """
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    actual_filename = f"analysis_{timestamp}.md" if "analysis" in filename.lower() else filename

    st.download_button(
        label="📥 Download as Markdown (.md)",
        data=text,
        file_name=actual_filename,
        mime="text/markdown",
        key=f"download_markdown_{key_suffix}"  # unique per call type
    )

def download_pdf(text: str, filename: str = "analysis.pdf", key_suffix: str = "pdf"):
    """
    Safe PDF download with unique key. Falls back gracefully without creating duplicate buttons.
    """
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    actual_filename = f"analysis_{timestamp}.pdf" if "analysis" in filename.lower() else filename

    try:
        from reportlab.lib.pagesizes import letter
        from reportlab.pdfgen import canvas

        buffer = BytesIO()
        c = canvas.Canvas(buffer, pagesize=letter)
        
        # Improved: basic multi-line support (wrap text)
        text_lines = text.split('\n')
        y = 750
        for line in text_lines:
            # Simple word wrap (approx 90 chars per line)
            while len(line) > 90:
                c.drawString(50, y, line[:90])
                line = line[90:]
                y -= 15
                if y < 50:
                    c.showPage()
                    y = 750
            c.drawString(50, y, line)
            y -= 15
            if y < 50:
                c.showPage()
                y = 750
        
        c.save()
        buffer.seek(0)

        st.download_button(
            label="📥 Download as PDF (.pdf)",
            data=buffer,
            file_name=actual_filename,
            mime="application/pdf",
            key=f"download_pdf_{key_suffix}"  # different unique key
        )

    except ImportError:
        st.warning("PDF export requires 'reportlab'. Run: `pip install reportlab` in your terminal.")
        # Do NOT call download_markdown() here → prevents duplicate button
        st.info("You can copy the text or use the Markdown download instead.")
    except Exception as e:
        st.error(f"PDF generation failed: {str(e)}")
        st.info("Falling back to text copy. Use Markdown download for full content.")