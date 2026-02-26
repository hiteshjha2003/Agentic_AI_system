#!/usr/bin/env python3
"""
CLI tester for SambaNova Code Agent backend features
Run with: python cli_test.py <command>

Requires: pip install requests typer rich python-dotenv pillow
"""

import os
import sys
import json
from pathlib import Path
import requests
from rich.console import Console
from rich.table import Table
from rich.panel import Panel
from dotenv import load_dotenv
import typer
from PIL import Image
import io

load_dotenv()

console = Console()
app = typer.Typer(help="SambaNova Code Agent CLI Tester")

BASE_URL = os.getenv("BACKEND_URL", "http://localhost:8000").rstrip("/")
API_KEY = os.getenv("SAMBANOVA_API_KEY", "")
HEADERS = {"Content-Type": "application/json"}
if API_KEY:
    HEADERS["X-API-Key"] = API_KEY

WORKSPACE = "default"

def request(method: str, endpoint: str, json_data=None, files=None, params=None):
    url = f"{BASE_URL}{endpoint}"
    try:
        if method.upper() == "GET":
            r = requests.get(url, headers=HEADERS, params=params)
        elif method.upper() == "POST":
            if files:
                r = requests.post(url, headers={**HEADERS, "Content-Type": None}, files=files, data=params)
            else:
                r = requests.post(url, json=json_data, headers=HEADERS, params=params)
        else:
            raise ValueError("Only GET/POST supported in this tester")

        r.raise_for_status()
        return r.json()
    except requests.exceptions.RequestException as e:
        console.print(f"[bold red]Request failed:[/bold red] {e}")
        if hasattr(e.response, 'text'):
            console.print(e.response.text[:800])
        sys.exit(1)

@app.command()
def health():
    """Check if backend is alive"""
    data = request("GET", "/health")
    console.print(Panel(json.dumps(data, indent=2), title="Health Check", border_style="green"))

@app.command()
def analyze_simple():
    """Quick test of /analyze endpoint"""
    payload = {
        "query": "Explain what this function does: def add(a, b): return a + b",
        "analysis_type": "explain",
        "include_codebase": True,
        "stream": False
    }
    console.print("[yellow]Sending simple explain request...[/yellow]")
    result = request("POST", "/analyze", json_data=payload, params={"workspace_id": WORKSPACE})
    console.print(Panel(json.dumps(result, indent=2), title="Analysis Result", border_style="blue"))

@app.command()
@app.command()
def upload_screenshot(image_path: str, context: str = "Error screenshot from VS Code"):
    """Test screenshot ingestion + vision analysis"""
    path = Path(image_path)
    if not path.is_file():
        console.print(f"[red]File not found: {image_path}[/red]")
        return

    try:
        # Open and force convert to PNG bytes
        img = Image.open(path)
        buffered = io.BytesIO()
        img.convert("RGB").save(buffered, format="PNG")
        image_bytes = buffered.getvalue()
        mime = "image/png"
        filename = path.stem + ".png"  # force .png
    except Exception as e:
        console.print(f"[red]Failed to open/convert image: {e}[/red]")
        return

    files = {"file": (filename, image_bytes, mime)}
    params = {"context": context, "workspace_id": WORKSPACE}

    console.print(f"[yellow]Uploading converted PNG ({len(image_bytes)} bytes)...[/yellow]")
    result = request("POST", "/ingest/screenshot", files=files, params=params)

    # ── Pretty Print Result ─────────────────────────────────────────────────
    if result.get("status") == "success":
        console.print(Panel("[bold green]Success![/bold green]", style="green"))

        analysis = result.get("analysis", {})
        vision = analysis.get("vision_analysis", {})

        # Extract key parts (customize based on your SambaNova response)
        raw_response = vision.get("raw_response", "No response text")
        extracted_text = vision.get("extracted_text", "No extracted text")

        # Show structured output
        console.print("[bold cyan]Screenshot Analysis Result[/bold cyan]")
        console.print(f"[bold]Source:[/bold] {result.get('source', '—')}")
        console.print(f"[bold]Extracted Text:[/bold]")
        console.print(extracted_text.strip() or "[dim]None[/dim]")

        console.print("\n[bold]Raw Vision Response (summary):[/bold]")
        # Show first 500 chars of raw response nicely
        console.print(raw_response[:800] + "..." if len(raw_response) > 800 else raw_response)

        # If you have structured fields from SambaNova (e.g. issue_type)
        classification = analysis.get("issue_classification", {})
        if classification:
            console.print("\n[bold]Issue Classification:[/bold]")
            console.print(f"Type: {classification.get('type', '—')}")
            console.print(f"Severity: {classification.get('severity', '—')}")

    else:
        console.print(Panel(
            json.dumps(result, indent=2),
            title="Error",
            border_style="red"
        ))
    
@app.command()
def upload_audio(audio_path: str, participants: str = "Alice, Bob, Charlie"):
    """Test audio transcription + action extraction"""
    path = Path(audio_path)
    if not path.is_file():
        console.print(f"[red]File not found: {audio_path}[/red]")
        return

    # Read entire file into memory
    with open(path, "rb") as f:
        audio_bytes = f.read()

    # Choose MIME based on extension
    ext = path.suffix.lower()
    mime = "audio/mpeg" if ext == ".mp3" else "audio/wav"

    files = {"file": (path.name, audio_bytes, mime)}
    params = {"participants": participants, "workspace_id": WORKSPACE}

    console.print(f"[yellow]Uploading {path.name} as {mime} ({len(audio_bytes)} bytes)...[/yellow]")
    result = request("POST", "/ingest/audio", files=files, params=params)
    console.print(Panel(json.dumps(result, indent=2), title="Audio Result", border_style="green"))

@app.command()
def ingest_codebase(repo_path: str, workspace_id: str = "default"):
    """Trigger codebase ingestion (async background task)"""
    repo = Path(repo_path)
    if not repo.is_dir():
        console.print(f"[red]Repo path not found or not a directory: {repo_path}[/red]")
        return

    params = {
        "repo_path": str(repo.absolute()),
        "workspace_id": workspace_id
    }

    console.print(f"[yellow]Starting ingestion of {repo}...[/yellow]")
    result = request("POST", "/ingest/codebase", params=params)
    console.print(Panel(json.dumps(result, indent=2), title="Ingestion Started", border_style="blue"))

@app.command()
def list_endpoints():
    """Show all available test commands"""
    table = Table(title="Available CLI Commands")
    table.add_column("Command", style="cyan")
    table.add_column("Description", style="magenta")
    table.add_column("Example", style="green")

    table.add_row("health", "Check server status", "python cli_test.py health")
    table.add_row("analyze-simple", "Quick code explanation test", "python cli_test.py analyze-simple")
    table.add_row("upload-screenshot", "Test vision endpoint", "python cli_test.py upload-screenshot screenshot.png")
    table.add_row("upload-audio", "Test audio transcription", "python cli_test.py upload-audio meeting.mp3")
    table.add_row("ingest-codebase", "Trigger repo ingestion", "python cli_test.py ingest-codebase /path/to/repo")
    table.add_row("list-endpoints", "Show this help", "python cli_test.py list-endpoints")

    console.print(table)

if __name__ == "__main__":
    if len(sys.argv) == 1:
        console.print("[bold yellow]No command given. Showing help:[/bold yellow]")
        list_endpoints()
    else:
        app()