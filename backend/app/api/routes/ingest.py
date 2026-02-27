from fastapi import APIRouter, UploadFile, File, Query, HTTPException
from typing import Optional, Dict, Any
import uuid
from app.models.schemas import IngestedContext, IngestionType
import json


# Use a service registry or global variable that will be populated later
services = {}

router = APIRouter(prefix="/ingest", tags=["ingestion"])

@router.post("/screenshot")

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

    res = {
        "id": str(uuid.uuid4()),
        "analysis": vision_result,
        "extracted_text": content_str,
        "status": "processed"
    }

    # Save to history
    services["history"].save_entry("screenshot", res, query=context)

    return res

@router.post("/audio")
async def ingest_audio(
    file: UploadFile = File(...),
    workspace_id: str = "default",
    participants: Optional[str] = None
):
    """Process meeting audio for transcription and actions."""
    if not file.filename:
        raise HTTPException(status_code=400, detail="Filename missing")
        
    content_bytes = await file.read()
    print(f"📊 [Audio Ingest] Received file: {file.filename} ({len(content_bytes)} bytes)")
    
    if not content_bytes:
        raise HTTPException(status_code=400, detail="Empty audio file")
        
    participant_list = participants.split(",") if participants else []
    
    try:
        audio_result = await services["audio"].process_meeting_audio(
            audio_bytes=content_bytes,
            filename=file.filename,
            participants=participant_list
        )
    except Exception as e:
        # Detailed logging for the terminal
        import traceback
        error_type = type(e).__name__
        print(f"❌ [Audio Ingest] {error_type}: {str(e)}")
        traceback.print_exc()
        
        error_msg = str(e)
        if "BadRequestError" in error_type or "BadRequestError" in error_msg:
             raise HTTPException(status_code=400, detail=f"SambaNova rejected audio: {error_msg}")
        raise HTTPException(status_code=500, detail=f"Audio Service Error: {error_msg}")
    
    # Store in context if needed
    ingested = IngestedContext(
        type=IngestionType.AUDIO,
        source=file.filename,
        content=audio_result.get("transcription", ""),
        metadata={
            "action_items": audio_result.get("action_items", []),
            "meeting_summary": audio_result.get("summary", ""),
            "participants": participant_list
        }
    )
    
    # Optional: create embedding for the transcript
    if ingested.content:
        await services["sambanova"].create_embedding(ingested.content)

    res = {
        "id": ingested.id,
        "status": "processed",
        "analysis": audio_result,
        "transcription": audio_result.get("transcription"),
        "action_items": audio_result.get("action_items"),
        "summary": audio_result.get("summary")
    }

    # Save to history
    services["history"].save_entry("audio", res, query=f"Meeting: {file.filename}")

    return res