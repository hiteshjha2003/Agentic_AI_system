# README.md: Real-Time Multimodal Code Review + Debug Agent

![SambaNova Code Agent Logo](https://via.placeholder.com/150?text=SN+Code+Agent) <!-- Placeholder for logo; replace with actual if available -->

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
  - [Frontend-Specific (Streamlit)](#frontend-specific-streamlit)
  - [VS Code Extension Launcher](#vs-code-extension-launcher)
- [Installation](#installation)
  - [Backend Local Setup](#backend-local-setup)
  - [Frontend (Streamlit) Local Setup](#frontend-streamlit-local-setup)
  - [VS Code Extension Setup](#vs-code-extension-setup)
  - [Docker Setup (Backend Only)](#docker-setup-backend-only)
- [Configuration](#configuration)
  - [Environment Variables](#environment-variables)
  - [.env File Example](#env-file-example)
- [Running the Application](#running-the-application)
  - [Running the Backend](#running-the-backend)
    - [Local Development Mode](#local-development-mode)
    - [Production Mode](#production-mode)
    - [Docker Mode](#docker-mode)
  - [Running the Frontend (Streamlit)](#running-the-frontend-streamlit)
    - [Standalone Mode](#standalone-mode)
    - [With Custom Environment Variables](#with-custom-environment-variables)
  - [Running Combined (Backend + Frontend + VS Code Launcher)](#running-combined-backend--frontend--vs-code-launcher)
    - [Step-by-Step Integration](#step-by-step-integration)
    - [Testing the Combined Setup](#testing-the-combined-setup)
  - [Shutting Down](#shutting-down)
  - [Testing the Server and Features](#testing-the-server-and-features)
    - [Using Swagger UI](#using-swagger-ui)
    - [Using the CLI Tester](#using-the-cli-tester)
    - [Manual CURL/Postman Tests](#manual-curlpostman-tests)
- [Usage Guide](#usage-guide)
  - [Backend API Endpoints](#backend-api-endpoints)
  - [WebSocket for Real-Time Streaming](#websocket-for-real-time-streaming)
  - [Frontend (Streamlit) Interface](#frontend-streamlit-interface)
  - [Ingesting Data](#ingesting-data)
  - [Performing Analysis](#performing-analysis)
  - [Executing Actions](#executing-actions)
  - [Advanced Features in Frontend](#advanced-features-in-frontend)
- [Implementation Details](#implementation-details)
  - [Backend Implementation](#backend-implementation)
    - [SambaNova Integration](#sambanova-integration)
    - [Ingestion Services](#ingestion-services)
    - [Analysis Engine](#analysis-engine)
    - [Memory Layer](#memory-layer)
    - [Utilities and Helpers](#utilities-and-helpers)
  - [Frontend (Streamlit) Implementation](#frontend-streamlit-implementation)
    - [Pages and Navigation](#pages-and-navigation)
    - [Components](#components)
    - [Utils](#utils)
    - [Styling and Themes](#styling-and-themes)
  - [VS Code Extension Launcher](#vs-code-extension-launcher-1)
- [Troubleshooting](#troubleshooting)
  - [Common Backend Issues](#common-backend-issues)
  - [Common Frontend Issues](#common-frontend-issues)
  - [Combined Setup Issues](#combined-setup-issues)
- [Contributing](#contributing)
- [License](#license)

## Project Overview
This project implements a **Real-Time Multimodal Code Review + Debug Agent** powered by SambaNova's AI capabilities. The backend serves as the core engine for processing multimodal inputs (code, screenshots, audio) and generating AI-driven insights, suggestions, and actions. It is built with Python and FastAPI, integrating SambaNova Cloud for advanced AI tasks like chat completions, embeddings, vision analysis, and function calling. Data persistence is handled via ChromaDB for vector storage, enabling efficient semantic searches.

The frontend is a Streamlit-based web application that provides an interactive UI for users to ingest data, perform analyses, view results, and execute actions. It connects directly to the backend via HTTP and WebSockets for real-time interactions.

A minimal VS Code extension acts as a launcher to start the Streamlit frontend seamlessly within the development environment, bridging the gap between the backend API and a user-friendly interface.

This system is optimized for high-performance code analysis in development workflows:
- **Multimodal Inputs**: Handle code snippets, error screenshots, meeting audio, and more.
- **AI-Driven Insights**: Use SambaNova's models for debugging, reviews, refactoring, explanations, and test generation.
- **Autonomous Capabilities**: Includes an agent loop for iterative code searching, editing, and verification.
- **Scalability and Real-Time**: Asynchronous processing, retries, batching, and streaming for responsive UX.

Target audience: Developers, teams using VS Code, and organizations leveraging SambaNova for AI-accelerated coding tools. The combined setup allows running everything locally or in containers for easy deployment.

## Key Features
- **Ingestion Pipelines**: Support for screenshots (vision analysis), audio (transcription and action extraction), codebases (semantic parsing), error logs, and PR descriptions.
- **Analysis Types**: Debug, review, refactor, explain, or generate tests with rich contextual awareness from vector stores.
- **Action Generation**: AI-suggested edits, file creations/deletions, tests, PR comments, or notifications via function calling.
- **Memory and Search**: Vector-based semantic search over codebases and conversation history using SambaNova embeddings and ChromaDB.
- **Real-Time Streaming**: WebSocket support for live analysis updates in the frontend.
- **Integrations**: Backend ready for GitHub (PR comments), Slack, Email; frontend includes previews and settings for GitHub PAT.
- **Frontend Enhancements**: Interactive UI with chat, diff viewers, image cropping, theme toggles, exports (MD/PDF), and progress indicators.
- **Security**: API key authentication; expandable to JWT or OAuth.
- **Telemetry and Monitoring**: Basic logging; extensible to tools like Prometheus.
- **Testing Tools**: Built-in CLI tester for verifying all endpoints from the terminal.

## Architecture Overview
The architecture is modular, with a FastAPI backend handling core logic, a Streamlit frontend for user interaction, and a VS Code extension for seamless launching. The backend is monolithic for simplicity but follows service-oriented patterns internally.

### High-Level Diagram
Updated to include frontend and launcher:

```
┌────────────────────────────────────────────────────────────────────────────┐
│ VS Code (with Launcher Extension)                                          │
│                                                                            │
│  ┌─────────────────────┐                                                   │
│  │ Streamlit Frontend  │ ← WebSocket / HTTP → FastAPI Backend             │
│  │ (Interactive UI)    │                                                   │
│  └─────────────────────┘                                                   │
└────────────────────────────────────────────────────────────────────────────┘
                       ▲
                       │ Launch command
                       ▼
┌────────────────────────────────────────────────────────────────────────────┐
│ Python FastAPI Backend                                                     │
│ ┌─────────────┐ ┌─────────────┐ ┌─────────────┐ ┌──────────┐             │
│ │ Ingestion   │ │ Analysis    │ │ Action      │ │ Memory    │             │
│ │ Service     │→ │ Engine      │→ │ Service    │→ │ Layer     │             │
│ └─────────────┘ └─────────────┘ └─────────────┘ └──────────┘             │
│ ↑ ↑ ↑ ↑ ↓                                                                 │
│ ┌────┴────┐ ┌────┴────┐ │ ┌────┴────┐ │                                 │
│ │ Audio   │ │ Vision   │ │ │ GitHub  │ │                                 │
│ │Whisper  │ │        │ │ │ Slack   │ │                                 │
│ └─────────┘ └─────────┘ │ │ Email   │ │                                 │
│                          └───────────┘                                   │
│ ┌──────────────────┐                                                      │
│ │ SambaNova Cloud │                                                      │
│ │ • Chat/Comps    │                                                      │
│ │ • Embeddings    │                                                      │
│ │ • Func Calling  │                                                      │
│ └──────────────────┘                                                      │
└────────────────────────────────────────────────────────────────────────────┘
```

- **Flow Explanation**:
  1. **VS Code Launcher Extension**: Activates on command, spawns Streamlit process, and opens the frontend in a browser or embedded view.
  2. **Streamlit Frontend**: Provides UI for user inputs (queries, uploads). Sends requests to backend via HTTP (e.g., /analyze, /ingest/*) or WebSocket (/ws for streaming).
  3. **Ingestion Service**: Processes uploads (audio with Whisper, vision with SambaNova/OCR, code with Tree-Sitter).
  4. **Analysis Engine**: Retrieves contexts from Memory, uses SambaNova for reasoning and streaming responses back to frontend.
  5. **Action Service**: Generates and executes actions (e.g., edits, PR comments) via SambaNova function calling; frontend previews and triggers.
  6. **Memory Layer**: ChromaDB stores embeddings for fast searches; queried during analysis.
  7. **External Integrations**: Backend placeholders for GitHub/Slack; frontend handles PAT input and previews.

For visual tools: Use Draw.io to export this ASCII as SVG. The backend is the core; frontend is a consumer.

### Component Breakdown
- **Backend (FastAPI)**: API server, AI orchestration, data processing.
- **Frontend (Streamlit)**: Interactive web app for end-users, with pages for analysis, uploads, actions, and settings.
- **VS Code Launcher Extension**: Minimal TypeScript extension to start Streamlit and integrate with VS Code commands.
- **SambaNova Client**: Unified async client for all SambaNova API calls.
- **Ingestion Services**: Modular processors for audio, vision, code.
- **Analysis Services**: Context retrieval, re-ranking, action generation.
- **Memory Services**: Vector and conversation stores with ChromaDB.
- **Utils**: Shared helpers for parsing, telemetry, etc.
- **CLI Tester**: Command-line tool for backend verification.

## Project Structure
Optimized to include frontend and extension:

```
sambanova-code-agent/
├── backend/
│   ├── app/
│   │   ├── __init__.py
│   │   ├── main.py                 # FastAPI app entry
│   │   ├── config.py               # Pydantic settings and env vars
│   │   ├── models/
│   │   │   ├── __init__.py
│   │   │   ├── schemas.py          # Pydantic models (requests/responses)
│   │   │   └── enums.py            # Enums for types (IngestionType, etc.)
│   │   ├── services/
│   │   │   ├── __init__.py
│   │   │   ├── sambanova_client.py # SambaNova API orchestrator
│   │   │   ├── ingestion/
│   │   │   │   ├── __init__.py
│   │   │   │   ├── audio_processor.py  # Whisper transcription + actions
│   │   │   │   ├── vision_processor.py # Pillow + Tesseract + SambaNova vision
│   │   │   │   └── code_ingester.py    # Tree-Sitter parsing for codebases
│   │   │   ├── analysis/
│   │   │   │   ├── __init__.py
│   │   │   │   ├── context_engine.py   # Hybrid search + re-ranking
│   │   │   │   └── action_generator.py # Function calling for actions
│   │   │   └── memory/
│   │   │       ├── __init__.py
│   │   │       ├── vector_store.py     # ChromaDB for code embeddings
│   │   │       └── conversation_store.py # ChromaDB for session history
│   │   ├── api/
│   │   │   ├── __init__.py
│   │   │   ├── routes/
│   │   │   │   ├── __init__.py
│   │   │   │   ├── ingest.py           # Ingestion routes
│   │   │   │   ├── analyze.py          # Analysis routes
│   │   │   │   ├── actions.py          # Action execution routes
│   │   │   │   └── chat.py             # WebSocket routes
│   │   │   └── dependencies.py         # FastAPI dependencies (e.g., auth)
│   │   └── utils/
│   │       ├── __init__.py
│   │       ├── code_parser.py          # AST parsing and diffs
│   │       └── telemetry.py            # Function timing logs
│   ├── cli_test.py                     # CLI for testing all features
│   ├── requirements.txt                # Backend dependencies
│   ├── Dockerfile                      # Backend Docker build
│   └── docker-compose.yml              # Docker Compose for backend + volumes
├── frontend-streamlit/
│   ├── pages/
│   │   ├── 1_Home.py                   # Welcome and quick actions
│   │   ├── 2_Code_Analysis.py          # Query analysis + results
│   │   ├── 3_Screenshot_Analysis.py    # Upload + crop + ingest
│   │   ├── 4_Audio_Transcription.py    # Audio upload + transcription
│   │   ├── 5_Actions_&_Fixes.py        # Execute suggested actions
│   │   └── 6_Settings.py               # Config (API key, GitHub, theme)
│   ├── components/
│   │   ├── __init__.py
│   │   ├── chat_interface.py           # WebSocket streaming chat
│   │   ├── code_viewer.py              # Code display
│   │   ├── diff_renderer.py            # Diff viewer
│   │   └── status_messages.py          # Styled alerts
│   ├── utils/
│   │   ├── __init__.py
│   │   ├── api.py                      # Backend API wrappers
│   │   ├── session_state.py            # Streamlit session init
│   │   └── helpers.py                  # Downloads (MD/PDF)
│   ├── style.css                       # Custom dark theme CSS
│   └── main.py                         # Streamlit entry + navigation
├── extension/
│   ├── src/
│   │   └── extension.ts                # Launcher command
│   ├── package.json                    # Extension manifest
│   ├── tsconfig.json                   # TypeScript config
│   └── README.md                       # Extension-specific docs
└── README.md                              # This file
```

## Prerequisites

### General Requirements
- **Python**: 3.11+ (required for both backend and frontend).
- **Git**: For cloning the repo.
- **Virtual Environment Tool**: `venv` (built-in) or `virtualenv`.
- **Docker**: Optional, for backend containerization.
- **SambaNova API Key**: Obtain from [SambaNova Cloud](https://cloud.sambanova.ai/).
- **Ports**: 8000 (backend), 8501 (Streamlit frontend); ensure free.
- **Hardware**: CPU sufficient; GPU recommended for faster Whisper (audio) or SambaNova calls.

### Backend-Specific

- **Dependencies**: Listed in `backend/requirements.txt` (FastAPI, OpenAI, ChromaDB, etc.).
- **CLI Tester Extras**: `pip install typer rich requests python-dotenv` for `cli_test.py`.

### Frontend-Specific (Streamlit)
- **Dependencies**: Streamlit, streamlit-cropper, Pillow (add to a separate requirements.txt if desired):
  ```
  pip install streamlit streamlit-cropper pillow
  ```
- **Browser**: Modern browser for accessing http://localhost:8501.

### VS Code Extension Launcher
- **VS Code**: Version 1.85+.
- **Node.js**: 20.x for building the extension.
- **Dependencies**: Listed in `extension/package.json` (@types/vscode, typescript, vsce).
- **Build Tool**: npm/yarn for compiling TypeScript.

## Installation

### Backend Local Setup
1. Clone and navigate:
   ```
   git clone https://github.com/your-repo/sambanova-code-agent.git
   cd sambanova-code-agent/backend
   ```
2. Create/activate venv:
   ```
   python -m venv venv
   source venv/bin/activate  # Windows: venv\Scripts\activate
   ```
3. Install deps:
   ```
   pip install -r requirements.txt
   ```
4. Install system packages (as above).

### Frontend (Streamlit) Local Setup
1. Navigate:
   ```
   cd ../frontend-streamlit  # From backend folder
   ```
2. Use same venv or create new:
   ```
   pip install streamlit streamlit-cropper pillow
   ```
3. Test: `streamlit run main.py` (should open browser at http://localhost:8501).

### VS Code Extension Setup
1. Navigate:
   ```
   cd ../extension
   ```
2. Install Node deps:
   ```
   npm install
   ```
3. Compile:
   ```
   npm run compile
   ```
4. Package (for VSIX install):
   ```
   npm run package
   ```
5. Install in VS Code: `code --install-extension sambanova-code-agent-launcher-0.1.0.vsix` or sideload via VS Code Extensions view.

### Docker Setup (Backend Only)
1. Build:
   ```
   docker build -t sambanova-backend .
   ```
2. Run (simple):
   ```
   docker run -p 8000:8000 -v $(pwd)/chroma_db:/data/chroma -e SAMBANOVA_API_KEY=yourkey sambanova-backend
   ```
3. Or with Compose:
   ```
   docker-compose up -d
   ```
   - Persists data in volume.
   - Mount repos for ingestion: `-v /local/repos:/repos`.

## Configuration

### Environment Variables
- Backend (in `.env` or export):
  - `SAMBANOVA_API_KEY`: Required for SambaNova calls.
  - `SAMBANOVA_BASE_URL`: Default `https://api.sambanova.ai/v1`.
  - `SAMBANOVA_MODEL_*`: Vision/Chat/Embedding models (defaults as in config.py).
  - `CHROMA_PERSIST_DIR`: Vector DB path (default `./chroma_db`).
  - `WHISPER_MODEL`: Audio model size (default `base`).
  - `MAX_TOKENS`, `TEMPERATURE`, `TOP_P`: SambaNova params.
- Frontend (optional, in env or Streamlit config):
  - `SAMBANOVA_BACKEND_URL`: Points to backend (default `http://localhost:8000`).
  - `SAMBANOVA_API_KEY`: Same as backend for auth.

### .env File Example
For backend (in `backend/`):
```
SAMBANOVA_API_KEY=sk-XXXXXXXXXXXXXXXX
SAMBANOVA_BASE_URL=https://api.sambanova.ai/v1
CHROMA_PERSIST_DIR=./chroma_db
WHISPER_MODEL=base
MAX_TOKENS=4096
TEMPERATURE=0.2
TOP_P=0.1
```
For frontend (in `frontend-streamlit/`):
```
SAMBANOVA_BACKEND_URL=http://localhost:8000
SAMBANOVA_API_KEY=sk-XXXXXXXXXXXXXXXX
```

## Running the Application

### Running the Backend
The backend must run first as the frontend depends on it for API calls.

#### Local Development Mode
- Navigate to `backend/`.
- Activate venv.
- Run:
  ```
  uvicorn app.main:app --host 0.0.0.0 --port 8000 --reload
  ```
- Features: Auto-reload on code changes; debug logs in console.
- Access: http://localhost:8000/health (should return {"status": "healthy"}).

#### Production Mode
- Run:
  ```
  uvicorn app.main:app --host 0.0.0.0 --port 8000 --workers 4
  ```
- Features: Multi-worker for concurrency; no reload.

#### Docker Mode
- Run:
  ```
  docker-compose up -d
  ```
- Features: Isolated env; persistent volumes for ChromaDB.
- Logs: `docker logs -f <container_id>`.

### Running the Frontend (Streamlit)
The frontend can run standalone or launched via VS Code.

#### Standalone Mode
- Navigate to `frontend-streamlit/`.
- Run:
  ```
  streamlit run main.py
  ```
- Features: Opens browser automatically; hot-reload on changes.
- Access: http://localhost:8501 (default port).

#### With Custom Environment Variables
- Export env vars first (e.g., `export SAMBANOVA_BACKEND_URL=http://localhost:8000`).
- Then run as above.

### Running Combined (Backend + Frontend + VS Code Launcher)
For integrated workflow: Backend serves API, VS Code launches Streamlit, which calls backend.

#### Step-by-Step Integration
1. **Start Backend**: As in "Local Development Mode" (port 8000).
2. **Install/Activate Extension**:
   - Open VS Code.
   - Install the VSIX (from `npm run package`) or sideload folder.
3. **Launch from VS Code**:
   - Press Ctrl+Shift+P (Cmd+Shift+P on Mac).
   - Run command: "SambaNova: Open Agent UI (Streamlit)".
   - This spawns Streamlit process and opens http://localhost:8501 in browser.
4. **Interact**:
   - In Streamlit: Enter queries, upload files – it calls backend APIs.
   - Real-time: Chat page uses WebSocket to backend /ws.
   - GitHub: Settings page stores PAT; actions page previews/comments.

#### Testing the Combined Setup
- Health: In Streamlit sidebar, see "Backend OK".
- Test Flow: Upload screenshot in Streamlit → see result from backend.
- Stop: Ctrl+C in terminals; extension kills Streamlit on deactivate.

### Shutting Down
- Backend: Ctrl+C or `docker-compose down`.
- Frontend: Ctrl+C.
- Extension: VS Code deactivate kills Streamlit process.

### Testing the Server and Features
#### Using Swagger UI
- Run backend, visit http://localhost:8000/docs.
- Test endpoints interactively (auth with API key if set).

#### Using the CLI Tester
- Navigate to `backend/`.
- Run:
  ```
  python cli_test.py health
  ```
- Full commands: `python cli_test.py list-endpoints`.
- Example: `python cli_test.py upload-screenshot /path/to/image.png`.

#### Manual CURL/Postman Tests
- Health: `curl http://localhost:8000/health`.
- Analyze: `curl -X POST http://localhost:8000/analyze -H "Content-Type: application/json" -d '{"query": "Test query", "analysis_type": "explain"}'`.
- Upload: Use Postman for file POSTs.

## Usage Guide

### Backend API Endpoints
Detailed with examples (use Postman or CURL):
- `/health` (GET): Server status. Response: {"status": "healthy"}.
- `/ingest/screenshot` (POST): Upload image. Form: file= (binary), context=str. Response: {id, analysis}.
- `/ingest/audio` (POST): Upload audio. Form: file= (binary), participants=str. Response: {transcription, action_items}.
- `/ingest/codebase` (POST): Trigger ingestion. JSON: {"repo_path": "/path"}. Response: {status: "processing"}.
- `/analyze` (POST): Perform analysis. JSON: AnalysisRequest. Response: AnalysisResponse.
- `/actions/execute` (POST): Execute actions. JSON: [SuggestedAction]. Response: {results}.
- Full schemas in `models/schemas.py`.

### WebSocket for Real-Time Streaming
- Connect: ws://localhost:8000/ws.
- Send: {"type": "analyze", "payload": AnalysisRequest}.
- Receive: {"type": "analysis_chunk", "content": str}, etc.

### Frontend (Streamlit) Interface
- Home: Quick buttons to other pages.
- Code Analysis: Enter query, select type, run – shows results, actions, exports.
- Screenshot: Upload, crop, context – ingests to backend.
- Audio: Upload, participants – transcribes via backend.
- Actions: Select/execute from last analysis.
- Settings: Configure URL/key, GitHub PAT (previews comments), theme.

### Ingesting Data
- Backend: POST to /ingest/*.
- Frontend: Use upload pages – handles files, calls backend.

### Performing Analysis
- Backend: POST /analyze with JSON.
- Frontend: Fill form on Code Analysis page – streams results via WS.

### Executing Actions
- Backend: POST /actions/execute.
- Frontend: On Actions page – select from results, execute.

## Implementation Details

### Backend Implementation
Detailed code breakdowns in files.

#### SambaNova Integration
- `services/sambanova_client.py`: Async client with retry, model routing, vision/embedding/function/streaming/agent loop.

#### Ingestion Services
- Audio: `ingestion/audio_processor.py` – Whisper transcribe, heuristic actions.
- Vision: `ingestion/vision_processor.py` – Pillow preprocess, Tesseract fallback, SambaNova analyze.
- Code: `ingestion/code_ingester.py` – Tree-Sitter AST, chunking.

#### Analysis Engine
- `analysis/context_engine.py`: Hybrid search, re-rank.
- `analysis/action_generator.py`: Tool-based actions.

#### Memory Layer
- `memory/vector_store.py`: ChromaDB upserts/searches.
- `memory/conversation_store.py`: Session-based storage.

#### Utilities and Helpers
- `utils/code_parser.py`: AST, diffs.
- `utils/telemetry.py`: Timing logs.

### Frontend (Streamlit) Implementation
- `main.py`: Entry, sidebar nav.
- Pages: Modular, import on demand.
- Components: Reusable (chat with WS, diff/code viewers).
- Utils: API wrappers, session init, helpers (downloads).

#### Styling and Themes
- `style.css`: Dark theme; toggle in settings (reload for full effect).

### VS Code Extension Launcher
- `extension.ts`: Spawns Streamlit, handles stdout for URL.

## Troubleshooting
### Common Backend Issues
- Key invalid: Check .env, SambaNova dashboard.
- ChromaDB fail: Chmod dir, reinstall chromadb.
- Whisper error: FFmpeg path, model size.

### Common Frontend Issues
- Backend not found: Check URL in settings.
- WS fail: Ensure backend runs, no proxy issues.
- Cropper missing: Install streamlit-cropper.

### Combined Setup Issues
- Launcher fail: Check Python path in VS Code, Streamlit installed.
- Port conflict: Change Streamlit port with `--server.port 8502`.

## Contributing
- Issues/PRs welcome.
- Code style: Black (Python), Prettier (TS).
- Tests: Add pytest for backend.

## License
MIT. See LICENSE.