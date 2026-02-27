# Stage 1: Base Python image with shared dependencies
FROM python:3.11-slim as python-base

# Prevent Python from writing .pyc files and enable unbuffered logging
ENV PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1 \
    PYTHONPATH=/app/backend

WORKDIR /app

# Install system dependencies for OCR, vision, and audio processing
RUN apt-get update && apt-get install -y \
    tesseract-ocr \
    ffmpeg \
    libsm6 \
    libxext6 \
    curl \
    && rm -rf /var/lib/apt/lists/*

# Install Python dependencies (cached if requirements.txt doesn't change)
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# --- BACKEND SERVICE ---
FROM python-base as backend
COPY backend/ /app/backend/
# Ensure the root database and chroma directories exist
RUN mkdir -p /app/database /app/chroma_db
EXPOSE 8000
CMD ["uvicorn", "app.main:app", "--host", "0.0.0.0", "--port", "8000"]

# --- STREAMLIT LEGACY SERVICE ---
FROM python-base as streamlit
COPY streamlit_legacy/ /app/streamlit_legacy/
COPY frontend/main.py /app/streamlit_legacy/main.py
EXPOSE 8501
HEALTHCHECK CMD curl --fail http://localhost:8501/_stcore/health
CMD ["streamlit", "run", "streamlit_legacy/main.py", "--server.port", "8501", "--server.address", "0.0.0.0"]

# --- MODERN FRONTEND (NGINX) ---
FROM nginx:alpine as frontend
# Copy the static HTML/JS/CSS to Nginx's default public directory
COPY frontend/ /usr/share/nginx/html/
# Remove Python-specific files from the web server directory
RUN rm /usr/share/nginx/html/main.py
EXPOSE 80