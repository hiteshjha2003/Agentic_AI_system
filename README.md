# README.md: Multimodel Code Review & Agentic Platform

![SambaNova Code Agent Logo](https://via.placeholder.com/150?text=SN+Code+Agent)

## 📖 Table of Contents
- [Project Overview](#project-overview)
- [Key Features](#key-features)
- [Architecture Overview](#architecture-overview)
  - [High-Level Diagram](#high-level-diagram)
  - [Component Breakdown](#component-breakdown)
- [Project Structure](#project-structure)
- [Prerequisites](#prerequisites)
  - [General Requirements](#general-requirements)
  - [Backend-Specific](#backend-specific)
- [Installation](#installation)
  - [Backend Local Setup](#backend-local-setup)
  - [Frontend Local Setup](#frontend-local-setup)
  - [Docker Setup](#docker-setup)
- [Configuration](#configuration)
  - [Environment Variables](#environment-variables)
  - [.env File Example](#env-file-example)
- [Running the Application](#running-the-application)
  - [Running the Backend](#running-the-backend)
  - [Running the Modern Frontend](#running-the-modern-frontend)
  - [Running Legacy Streamlit](#running-legacy-streamlit)
- [Testing the Server and Features](#testing-the-server-and-features)
  - [Using Swagger UI](#using-swagger-ui)
  - [Using the CLI Tester](#using-the-cli-tester)
  - [Manual CURL/Postman Tests](#manual-curlpostman-tests)
- [Usage Guide](#usage-guide)
  - [Backend API Endpoints](#backend-api-endpoints)
  - [WebSocket for Real-Time Streaming](#websocket-for-real-time-streaming)
  - [Frontend Interface](#frontend-interface)
  - [Ingesting Data](#ingesting-data)
  - [Performing Analysis](#performing-analysis)
  - [Executing Actions](#executing-actions)
- [Implementation Details](#implementation-details)
  - [Backend Implementation](#backend-implementation)
  - [SambaNova Integration](#sambanova-integration)
  - [Ingestion Services](#ingestion-services)
  - [Analysis Engine](#analysis-engine)
  - [Memory Layer](#memory-layer)
  - [Frontend Implementation](#frontend-implementation)
- [Troubleshooting](#troubleshooting)
- [Contributing](#contributing)
- [License](#license)

---

## Project Overview
This project implements a **Real-Time Multimodal Code Review + Debug Agent** powered by SambaNova's AI capabilities. The backend serves as the core engine for processing multimodal inputs (code, screenshots, audio) and generating AI-driven insights. It is built with Python and FastAPI, integrating SambaNova Cloud for chat completions, embeddings, vision, and function calling. Data persistence is handled via ChromaDB for vector storage and a date-based JSON system for history.

The application features a **Modern Frontend** (HTML/CSS/JS) for a premium, responsive experience, while retaining a `streamlit_legacy` directory for the original implementation.

## Key Features
- **Multimodal Ingestion**: Support for screenshots (Vision analysis), audio (Transcription + Action extraction), and codebases (Semantic parsing).
- **AI-Driven Insights**: Leverage SambaNova's models for context-aware code reviews, debugging, and refactoring.
- **Autonomous Actions**: AI-generated code edits with robust JSON-safe formatting to prevent parsing errors.
- **Date-Based History**: Optimized storage grouping all actions for a specific day into a single `YYYY-MM-DD.json` file in the root `database/` folder.
- **Memory & Search**: Hybrid semantic search over codebase using SambaNova embeddings and ChromaDB.
- **Real-Time Streaming**: WebSocket support for live analysis updates.

## Architecture Overview
The system follows a modular client-server architecture:

### High-Level Diagram
```
┌────────────────────────────────────────────────────────────────────────────┐
│ Modern Frontend (HTML/JS/CSS)       ← WebSocket / HTTP → FastAPI Backend    │
│ (Premium Interactive UI)                                                   │
└────────────────────────────────────────────────────────────────────────────┘
                       ▲
                       │
                       ▼
┌────────────────────────────────────────────────────────────────────────────┐
│ Python FastAPI Backend                                                     │
│ ┌─────────────┐ ┌─────────────┐ ┌─────────────┐ ┌──────────┐             │
│ │ Ingestion   │ │ Analysis    │ │ Action      │ │ Memory    │             │
│ │ Service     │→ │ Engine      │→ │ Service    │→ │ Layer     │             │
│ └─────────────┘ └─────────────┘ └─────────────┘ └──────────┘             │
│          ↕               ↕               ↕               ↕                 │
│ ┌────────────────────────────────────────────────────────────────────────┐ │
│ │ SambaNova Cloud (LLM, Vision, Embeddings)                              │ │
│ └────────────────────────────────────────────────────────────────────────┘ │
└────────────────────────────────────────────────────────────────────────────┘
```

### Component Breakdown
- **Backend (FastAPI)**: Core API server, AI orchestration, and background tasks.
- **Modern Frontend (HTML/JS)**: New premium UI with modular JavaScript components.
- **Streamlit Legacy**: The original Python-based frontend maintained for reference.
- **Memory Layer**: ChromaDB for code/conversation embeddings and a local JSON database for daily history.

## Project Structure
Detailed breakdown of the current codebase:

```
sambanova-coder-agent/
├── backend/                        # FastAPI Core
│   ├── app/
│   │   ├── api/                    # API Routes & Dependencies
│   │   │   ├── routes/
│   │   │   │   ├── actions.py      # Action execution
│   │   │   │   ├── analyze.py      # Analysis engine
│   │   │   │   ├── chat.py         # WebSocket streaming
│   │   │   │   └── ingest.py       # Ingest pipelines
│   │   │   └── dependencies.py
│   │   ├── models/                 # Pydantic Schemas
│   │   │   ├── enums.py
│   │   │   └── schemas.py
│   │   ├── services/               # Core Logic
│   │   │   ├── ingestion/ 
│   │   │   │   ├── audio.py        # Audio processing
│   │   │   │   ├── code.py         # Code processing
│   │   │   │   ├── vision.py       # Vision processing
│   │   │   │   └── utils.py        # Ingestion utils
│   │   │   ├── analysis/           # Action generation & Context
│   │   │   │   ├── actions.py      # Action execution
│   │   │   │   ├── analyze.py      # Analysis engine
│   │   │   │   ├── chat.py         # WebSocket streaming
│   │   │   │   └── ingest.py       # Ingest pipelines
│   │   │   ├── memory/             # VectorStore & Conversation
│   │   │   │   ├── history_manager.py  # Date-based JSON storage
│   │   │   │   └── sambanova_client.py # Unified AI client
│   │   │   └── utils/
│   │   │       ├── telemetry.py    # Telemetry & Code parsing
│   │   │       └── utils.py        # General utils
│   │   └── main.py                 # FastAPI Entry point
│   ├── cli_test.py                 # CLI Verification tool
│   ├── requirements.txt
│   └── utils.py    
|-- database/                       # Database json files
|-- docs/                           # Documentation
|-- frontend/                       # Modern HTML/JS UI
│   ├── assets/                     # Media & Logos
│   ├── js/                         # Logic Layer
│   │   ├── pages/                  # Page-specific JS modules
│   │   ├── api.js                  # Backend API wrappers
│   │   ├── app.js                  # Main JS Entry
│   │   ├── router.js               # SPWA Routing
│   │   └── templates.js            # UI Rendering
│   ├── index.html                  # Root HTML
│   ├── style.css                   # Custom Premium CSS
│   └── main.py                     # Legacy Entry (Left for transition)
├── streamlit_legacy/               # Original Streamlit implementation
│   ├── pages/
│   │   ├── pages/
│   │   │   ├── Analysis.py
│   │   │   ├── Home.py
│   │   │   ├── Settings.py
│   │   │   ├── Screenshot_Analysis.py
│   │   │   ├── Actions_Fixes.py
│   │   │   ├── Audio_Transcription.py
│   │   │   ├── Code_Analysis.py
│   │   │   # Streamlit multipage files
│   │   ├── components/
│   │   │   ├── chat_interfaces.py
│   │   │   ├── code_viewer.py
│   │   │   ├── diff_renderer.py
│   │   │   ├── header.py
│   │   │   ├── status_messages.py
│   │   │   # Streamlit UI elements
│   │   └── utils/
│   │   │   ├── __init__.py
│   │   │   ├── session_state.py
│   │   │   ├── api.py
│   │   │   ├── helpers.py
│   │   │   ├── session.py
│   │   │   # Legacy Helper logic
│   ├── main.py                     # Legacy Entry (Left for transition)
├── pyproject.toml                  # Project Metadata
├── Dockerfile                      # Dockerfile
├── docker-compose.yml              # Docker Compose file 
├── .gitignore                      # Git ignore file
├── .env                            # Environment variables
├── .env.example                    # Environment variables example
├── README.md                       # README file
```

## Prerequisites
### General Requirements
- **Python**: 3.11+
- **SambaNova API Key**: Required for all AI features.
- **Ports**: 8000 (Backend), 8080 (Modern Frontend), 8501 (Legacy Streamlit).
- **Docker**: Required for Docker-based deployment.
- **Docker Compose**: Required for Docker-based deployment.
- **Docker Hub**: Required for Docker-based deployment.
- **Docker Hub API Key**: Required for Docker-based deployment.
- **Hardware**: CPU sufficient; GPU recommended for faster Whisper (audio) or SambaNova calls.

### Backend-Specific
- **Dependencies**: `pip install -r backend/requirements.txt`.
- **PYTHONPATH**: Must include the `backend` directory during execution.

## Installation
### Backend Local Setup
```bash

#Clone and navigate:
git clone https://github.com/your-repo/sambanova-code-agent.git

#Navigate to sambanova-code-agent/backend
cd sambanova-code-agent/backend 

#Create and activate venv
python -m venv venv

source venv/bin/activate

#Install dependencies
pip install -r requirements.txt
or
# Install system packages (as above).
pip install .

#Set PYTHONPATH
export PYTHONPATH=.

#Run uvicorn
uvicorn app.main:app --reload --port 8000
```

### Frontend Local Setup
The modern frontend is static; serve it via any simple HTTP server:
```bash
cd frontend
python3 -m http.server 8080

or 

#Navigate to sambanova-code-agent/frontend

#Run streamlit
cd sambanova-code-agent/streamlit_legacy

streamlit run main.py

```

### Frontend Local Setup
Serve the modern frontend via any simple HTTP server:
```bash
cd frontend
python3 -m http.server 8080
```

To run the legacy Streamlit interface:
```bash
cd streamlit_legacy
streamlit run main.py
```

## Configuration
### Environment Variables
Configure your `.env` in the `backend/` directory:
- `SAMBANOVA_API_KEY`: Your secret key. (https://cloud.sambanova.ai)
- `CHROMA_PERSIST_DIR`: Path for vector storage.
- `PYTHONPATH`: Set to `./backend`.


## Testing the Server and Features
### Using Swagger UI
Run backend, visit `http://localhost:8000/docs`. Test endpoints interactively.

### Using the CLI Tester
Navigate to `backend/`:
```bash
python cli_test.py health
python cli_test.py upload-screenshot /path/to/image.png
```

### Manual CURL/Postman Tests
**Health**: `curl http://localhost:8000/health`
**Analyze**: 
```bash
curl -X POST http://localhost:8000/analyze -H "Content-Type: application/json" -d '{"query": "Explain this code", "analysis_type": "explain"}'
```

## Usage Guide
### Backend API Endpoints
- `/health` (GET): Server status.
- `/ingest/screenshot` (POST): Form-data file upload for vision analysis.
- `/ingest/audio` (POST): Form-data file upload for transcription.
- `/analyze` (POST): JSON request for code analysis.
- `/actions/execute` (POST): JSON request to execute suggested changes.

### WebSocket for Real-Time Streaming
Connect to `ws://localhost:8000/ws` for streaming analysis chunks.

### Frontend Interface
- **Home**: Quick navigation and overview.
- **Analysis**: Query code, view results, and export reports (MD/PDF).
- **Screenshot**: Crop and ingest error images for AI troubleshooting.
- **Audio**: Transcribe meeting audio and extract action items.
- **Settings**: Configure API keys, backend URL, and themes.

## Implementation Details
### Backend Implementation
- **SambaNova Integration**: `services/sambanova_client.py` provides a unified async client with retry logic for Chat, Vision, and Embeddings.
- **Ingestion Services**:
    - **Audio**: `ingestion/audio.py` uses Whisper for transcription and extracts tasks.
    - **Vision**: `ingestion/vision.py` leverages SambaNova Vision models for UI/error analysis.
    - **Code**: `ingestion/code.py` uses Tree-Sitter for AST-based indexing.
- **Analysis Engine**: Uses hybrid search (Semantic + Keyword) and SambaNova reasoning.
- **Memory Layer**: `memory/vector_store.py` manages ChromaDB for code/conversation embeddings.

### Frontend Implementation
- **Modern UI**: Modular JS architecture with real-time WebSocket support for streaming responses.
- **Legacy Streamlit**: Multi-page Python app with custom components for diff rendering and code viewing.

## Troubleshooting
- **Import Errors**: Ensure `PYTHONPATH=.` is set when running the backend or Streamlit.
- **JSON Errors**: Mitigated with improved error handling in `sambanova_client.py`.
- **Backend Offline**: Check if `SAMBANOVA_API_KEY` is set correctly in `.env`.

---
## License
MIT. See LICENSE.

*Created with focus on Visual Excellence and Premium Architecture.*