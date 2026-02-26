import os
import requests
import json
import websocket
from typing import Dict, Any, List, Optional

# ---------------------------------------------------
# Configuration
# ---------------------------------------------------

BACKEND_URL = os.getenv("SAMBANOVA_BACKEND_URL", "http://localhost:8000")
API_KEY = os.getenv("SAMBANOVA_API_KEY")

DEFAULT_TIMEOUT = 120


def _get_headers() -> Dict[str, str]:
    """
    Builds authorization headers if API key exists.
    """
    headers = {}

    if API_KEY:
        headers["Authorization"] = f"Bearer {API_KEY}"

    return headers


def _handle_response(response: requests.Response) -> Dict[str, Any]:
    """
    Safely parse backend response.
    """
    try:
        response.raise_for_status()
        return response.json()
    except requests.exceptions.HTTPError:
        try:
            return response.json()
        except Exception:
            return {"error": response.text}
    except Exception as e:
        return {"error": str(e)}


# ---------------------------------------------------
# Health Check
# ---------------------------------------------------

def check_backend_health() -> Dict[str, Any]:
    try:
        url = f"{BACKEND_URL}/health"
        response = requests.get(url, timeout=10)
        return _handle_response(response)
    except Exception as e:
        return {"error": str(e)}


# ---------------------------------------------------
# Screenshot Ingestion
# ---------------------------------------------------

def ingest_screenshot(image_bytes: bytes, context: str = "") -> Dict[str, Any]:
    try:
        url = f"{BACKEND_URL}/ingest/screenshot"

        files = {
            "file": ("screenshot.png", image_bytes, "image/png")
        }

        data = {
            "context": context
        }

        response = requests.post(
            url,
            headers=_get_headers(),
            files=files,
            data=data,
            timeout=DEFAULT_TIMEOUT
        )

        return _handle_response(response)

    except Exception as e:
        return {"error": str(e)}


# ---------------------------------------------------
# Audio Ingestion
# ---------------------------------------------------

def ingest_audio(audio_bytes: bytes, participants: str = "") -> Dict[str, Any]:
    try:
        url = f"{BACKEND_URL}/ingest/audio"

        files = {
            "file": ("audio.wav", audio_bytes, "audio/wav")
        }

        data = {
            "participants": participants
        }

        response = requests.post(
            url,
            headers=_get_headers(),
            files=files,
            data=data,
            timeout=DEFAULT_TIMEOUT
        )

        return _handle_response(response)

    except Exception as e:
        return {"error": str(e)}


# ---------------------------------------------------
# Codebase Ingestion
# ---------------------------------------------------

def ingest_codebase(repo_path: str) -> Dict[str, Any]:
    try:
        url = f"{BACKEND_URL}/ingest/codebase"

        payload = {
            "repo_path": repo_path
        }

        response = requests.post(
            url,
            headers={**_get_headers(), "Content-Type": "application/json"},
            json=payload,
            timeout=DEFAULT_TIMEOUT
        )

        return _handle_response(response)

    except Exception as e:
        return {"error": str(e)}


# ---------------------------------------------------
# Analysis
# ---------------------------------------------------

# def analyze_query(
#     query: str,
#     analysis_type: str = "explain",
#     context: Optional[str] = None
# ) -> Dict[str, Any]:

#     try:
#         url = f"{BACKEND_URL}/analyze"

#         payload = {
#             "query": query,
#             "analysis_type": analysis_type,
#             "context": context
#         }

#         response = requests.post(
#             url,
#             headers={**_get_headers(), "Content-Type": "application/json"},
#             json=payload,
#             timeout=DEFAULT_TIMEOUT
#         )

#         return _handle_response(response)

#     except Exception as e:
#         return {"error": str(e)}

def analyze(
    query: str,
    analysis_type: str = "explain",
    include_codebase: bool = False,
    conversation_id: str = None
):

    try:
        url = f"{BACKEND_URL}/analyze"

        payload = {
            "query": query,
            "analysis_type": analysis_type,
            "include_codebase": include_codebase,
            "conversation_id": conversation_id,
        }

        response = requests.post(
            url,
            headers={**_get_headers(), "Content-Type": "application/json"},
            json=payload,
            timeout=DEFAULT_TIMEOUT
        )

        return _handle_response(response)

    except Exception as e:
        return {"error": str(e)}



# ---------------------------------------------------
# Execute Actions
# ---------------------------------------------------

def execute_actions(actions: List[Dict[str, Any]]) -> Dict[str, Any]:
    try:
        url = f"{BACKEND_URL}/actions/execute"

        response = requests.post(
            url,
            headers={**_get_headers(), "Content-Type": "application/json"},
            json=actions,
            timeout=DEFAULT_TIMEOUT
        )

        return _handle_response(response)

    except Exception as e:
        return {"error": str(e)}


# ---------------------------------------------------
# WebSocket Streaming (Optional)
# ---------------------------------------------------

def stream_analysis_ws(payload: Dict[str, Any], on_message_callback):
    """
    Connect to WebSocket and stream analysis.
    `on_message_callback` will receive each message.
    """

    ws_url = BACKEND_URL.replace("http", "ws") + "/ws"

    if API_KEY:
        ws_url += f"?token={API_KEY}"

    try:
        ws = websocket.WebSocketApp(
            ws_url,
            on_message=lambda ws, msg: on_message_callback(json.loads(msg)),
        )

        ws.run_forever()

    except Exception as e:
        print("WebSocket Error:", str(e))
