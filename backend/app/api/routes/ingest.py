# backend/app/api/routes/ingest.py
from fastapi import APIRouter, UploadFile, File, Query ,app
from typing import Optional
import uuid
from app.models.schemas import IngestedContext, IngestionType
import json


from app.main import services  # Import services from main (or better: use Depends later)

router = APIRouter(prefix="/ingest", tags=["ingestion"])

@app.post("/ingest/screenshot")

async def ingest_screenshot(
    file: UploadFile = File(...),
    workspace_id: str = "default",
    context: Optional[str] = None
):
    """Process screenshot of code/error."""
    content_bytes = await file.read()
    
    vision_result = await services["vision"].process_screenshot(
        image_bytes=content_bytes,
        source=file.filename,
        nearby_code=context
    )
    
    if vision_result.get("status") == "failed":
        return vision_result

    # Force content to be a string – handle list, dict, None safely
    raw_content = vision_result.get("combined_extracted_text") or vision_result.get("extracted_text", "")
    if isinstance(raw_content, list):
        content_str = "\n".join(str(item) for item in raw_content if item)
    elif isinstance(raw_content, dict):
        content_str = json.dumps(raw_content, indent=2)
    else:
        content_str = str(raw_content).strip()

    ingested = IngestedContext(
        type=IngestionType.SCREENSHOT,
        source=file.filename,
        content=content_str,  # ← now always a valid string
        metadata={
            "vision_analysis": vision_result.get("vision_analysis", {}),
            "issue_type": vision_result.get("issue_classification", {}).get("type", "unknown"),
            "severity": vision_result.get("issue_classification", {}).get("severity", "unknown")
        }
    )
    
    # Optional: create embedding only if there's meaningful text
    if content_str:
        embedding = await services["sambanova"].create_embedding(content_str)
        # TODO: store ingested + embedding in vector DB

    return {
        "id": str(uuid.uuid4()),
        "analysis": vision_result,
        "extracted_text": content_str,
        "status": "processed"
    }