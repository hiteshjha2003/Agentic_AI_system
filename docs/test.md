# README.md: Real-Time Multimodal Code Review + Debug Agent

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
  - [Frontend-Specific (Modern HTML/JS)](#frontend-specific-modern-htmljs)
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
- [Usage Guide](#usage-guide)
  - [Ingesting Data](#ingesting-data)
  - [Performing Analysis](#performing-analysis)
  - [Executing Actions](#executing-actions)
- [Implementation Details](#implementation-details)
  - [Backend Implementation](#backend-implementation)
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
The architecture is modular, separating the FastAPI backend from multiple frontend consumers.

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
│   └── utils.py                    # General utils
├── frontend/                       # Modern HTML/JS UI
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
├── database/                       # Grouped History (YYYY-MM-DD.json)
├── chroma_db/                      # Vector DB persistence
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

## Configuration
### Environment Variables
Configure your `.env` in the `backend/` directory:
- `SAMBANOVA_API_KEY`: Your secret key.(cloud.sambanova.ai)
- `CHROMA_PERSIST_DIR`: Path for vector storage (default: `./chroma_db`).
- `PYTHONPATH`: Set to `./backend`.



## Usage Guide
1. **Ingestion**: Use the "Screenshots" or "Audio" pages to feed context to the agent.
2. **Analysis**: Enter code queries. The agent will retrieve relevant code from ChromaDB and provide a detailed analysis.
3. **Actions**: Click suggested actions (Edit/Create/Test) to have the agent modify the codebase autonomously.

## Implementation Details
### Backend Implementation
- **SambaNova Client**: unified async client with retry logic for Chat, Vision, and Embeddings.
- **History Management**: Automatically consolidates all entries into one file per date to reduce file system clutter.
- **Action Generation**: Uses strict prompting and error handling to ensure AI-generated code edits are valid JSON.

### Frontend Implementation
- **Modular JS**: Follows a clean router-based architecture for smooth page transitions without reloads.
- **WebSocket Integration**: Direct streaming support for real-time AI responses.

## Troubleshooting
- **Import Errors**: Ensure `PYTHONPATH=.` is set when running the backend.
- **JSONDecodeError**: This has been mitigated with improved error handling in `sambanova_client.py`.
- **Database Path**: Ensure the root `database/` folder is writable; it is automatically created on first ingestion.

---
*Created with focus on Visual Excellence and Premium Architecture.*