# backend/app/main.py
from fastapi import FastAPI, WebSocket, WebSocketDisconnect, UploadFile, File, Depends, BackgroundTasks, HTTPException
import uuid
from fastapi.middleware.cors import CORSMiddleware
from contextlib import asynccontextmanager
import asyncio
import json
from typing import Optional

from app.config import get_settings
from app.services.sambanova_client import SambaNovaOrchestrator
from app.services.ingestion.audio_processor import AudioProcessor
from app.services.ingestion.vision_processor import VisionProcessor
from app.services.ingestion.code_ingester import CodeIngester
from app.services.memory.vector_store import CodebaseVectorStore
from app.models.schemas import (
    AnalysisRequest, AnalysisResponse, SuggestedAction,
    IngestedContext, IngestionType, CodebaseIngestRequest
)
from app.api.routes import ingest


# Global service instances
services = {}


@asynccontextmanager
async def lifespan(app: FastAPI):
    """Initialize and cleanup services."""
    # Startup
    services["sambanova"] = SambaNovaOrchestrator()
    services["audio"] = AudioProcessor()
    services["vision"] = VisionProcessor()
    services["code_ingester"] = CodeIngester()
    services["vector_store"] = CodebaseVectorStore()
    
    # Populate route service registries to avoid circular imports
    ingest.services.update(services)
    
    print("🚀 SambaNova Code Agent backend initialized")
    yield
    
    # Cleanup
    print("👋 Shutting down...")


app = FastAPI(
    title="SambaNova Code Agent",
    description="Multimodal code review and debug agent",
    version="1.0.0",
    lifespan=lifespan
)

app.include_router(ingest.router)


@app.post("/ingest/codebase")
async def ingest_codebase(
    request: CodebaseIngestRequest,
    background_tasks: BackgroundTasks
):
    """Trigger async codebase ingestion."""
    background_tasks.add_task(
        _ingest_codebase_task,
        request.repo_path,
        request.workspace_id
    )
    
    return {
        "status": "processing",
        "workspace_id": request.workspace_id,
        "message": "Codebase ingestion started in background"
    }


async def _ingest_codebase_task(repo_path: str, workspace_id: str):
    """Background task for codebase ingestion."""
    chunks = []
    
    async for chunk in services["code_ingester"].ingest_repository(repo_path):
        if chunk.get("type") == "error":
            print(f"Error processing {chunk['file_path']}: {chunk['error']}")
            continue
        chunks.append(chunk)
        
        # Batch process every 100 chunks
        if len(chunks) >= 100:
            await services["vector_store"].ingest_code_chunks(workspace_id, chunks)
            chunks = []
    
    # Process remaining
    if chunks:
        await services["vector_store"].ingest_code_chunks(workspace_id, chunks)
    
    print(f"✅ Completed ingestion for workspace {workspace_id}")


# ═════════════════════════════════════════════════════════════════
# ANALYSIS ENDPOINTS
# ═════════════════════════════════════════════════════════════════

@app.post("/analyze", response_model=AnalysisResponse)
async def analyze(request: AnalysisRequest, workspace_id: str = "default"):
    """
    Main analysis endpoint combining all capabilities.
    """
    start_time = asyncio.get_event_loop().time()
    
    # 1. Retrieve relevant context
    # Ensure at least 1 result is requested to avoid ChromaDB error
    top_k_value = 10 if request.include_codebase else 1
    contexts = await services["vector_store"].hybrid_search(
    workspace_id=workspace_id,
    query=request.query,
    code_location=request.code_location,
    top_k=top_k_value
    )
    
    # 2. Generate analysis with SambaNova
    if request.stream:
        # Handled by WebSocket
        raise HTTPException(status_code=400, detail="Use /ws for streaming")
    
    # Non-streaming analysis
    analysis_text = ""
    async for chunk in services["sambanova"].stream_analysis(
        query=request.query,
        context=contexts,
        analysis_type=request.analysis_type
    ):
        analysis_text += chunk
    
    # 3. Generate suggested actions
    tools = [
        {
            "type": "function",
            "function": {
                "name": "edit_file",
                "description": "Propose a code edit",
                "parameters": {
                    "type": "object",
                    "properties": {
                        "file_path": {"type": "string"},
                        "line_start": {"type": "integer"},
                        "line_end": {"type": "integer"},
                        "replacement": {"type": "string"},
                        "explanation": {"type": "string"}
                    }
                }
            }
        },
        {
            "type": "function",
            "function": {
                "name": "create_test",
                "description": "Generate a test case",
                "parameters": {
                    "type": "object",
                    "properties": {
                        "test_file": {"type": "string"},
                        "test_code": {"type": "string"},
                        "description": {"type": "string"}
                    }
                }
            }
        }
    ]
    
    actions = await services["sambanova"].generate_actions(
        query=request.query,
        relevant_code=contexts,
        analysis_type=request.analysis_type,
        available_tools=tools
    )
    formatted_actions = []
    for a in actions:
        raw_type = a["action_type"]
        
        # Improved mapping – ensure literals match SuggestedAction model
        allowed_types = {
            "edit", "create", "delete", "test", "pr_comment", "slack_notify",
            "edit_file", "create_test", "create_pr_comment", "search_codebase",
            "optimize", "explain", "refactor", "create_file"
        }
        
        mapped_type = raw_type
        if raw_type == "edit_file":
            mapped_type = "edit"
        elif raw_type in ("create_test", "generate_test"):
            mapped_type = "test"
        elif raw_type in ("create_pr_comment", "pr_comment", "add_pr_comment"):
            mapped_type = "pr_comment"
        elif raw_type == "slack_notify":
            mapped_type = "slack_notify"
        elif raw_type == "create_file":
            mapped_type = "create"
        elif raw_type == "search_codebase":
            mapped_type = "search_codebase"
            
        # Fallback for unexpected types to avoid validation crash
        if mapped_type not in allowed_types:
            mapped_type = "edit"  # Safest fallback
            
        # Optional: skip unknown types or log them
        # if mapped_type not in ["edit", "create", "delete", "test", "pr_comment", "slack_notify"]:
        #     print(f"Warning: Skipping unknown action type '{raw_type}'")
            
        formatted_actions.append(
            SuggestedAction(
                action_type=mapped_type,
                target_file=a["arguments"].get("file_path", a["arguments"].get("test_file", "unknown")),
                description=a["arguments"].get("explanation", a["arguments"].get("description", "")),
                diff=a["arguments"].get("replacement"),
                reasoning=a["reasoning"],
                confidence=0.85
            )
        )
    
    
    execution_time = int((asyncio.get_event_loop().time() - start_time) * 1000)
    
    return AnalysisResponse(
        request_id=str(uuid.uuid4()),
        summary=analysis_text[:500] + "...",
        detailed_analysis=analysis_text,
        relevant_contexts=[
            IngestedContext(
                id=c["id"],
                type=IngestionType.CODE_SNIPPET,
                source=c["metadata"].get("file_path", "unknown"),
                content=c["content"],
                metadata=c["metadata"]
            ) for c in contexts[:3]
        ],
        suggested_actions=formatted_actions,
        follow_up_questions=[
            "Would you like me to generate a test case for this fix?",
            "Should I check if this pattern exists in other files?",
            "Can you provide the full error traceback?"
        ],
        execution_time_ms=execution_time
    )


# ═════════════════════════════════════════════════════════════════
# WEBSOCKET FOR REAL-TIME STREAMING
# ═════════════════════════════════════════════════════════════════

@app.websocket("/ws")
async def websocket_endpoint(websocket: WebSocket):
    """WebSocket for real-time streaming analysis."""
    await websocket.accept()
    
    try:
        while True:
            # Receive message
            data = await websocket.receive_json()
            
            if data.get("type") == "analyze":
                request = AnalysisRequest(**data["payload"])
                workspace_id = data.get("workspace_id", "default")
                
                # Stream analysis
                await websocket.send_json({
                    "type": "status",
                    "content": "Retrieving context..."
                })
                
                # Get context
                contexts = await services["vector_store"].hybrid_search(
                    workspace_id=workspace_id,
                    query=request.query,
                    code_location=request.code_location,
                    top_k=10
                )
                
                await websocket.send_json({
                    "type": "context",
                    "content": f"Found {len(contexts)} relevant code snippets",
                    "files": [c["metadata"]["file_path"] for c in contexts[:3]]
                })
                
                # Stream analysis
                await websocket.send_json({
                    "type": "status",
                    "content": "Analyzing with SambaNova..."
                })
                
                analysis_buffer = ""
                async for chunk in services["sambanova"].stream_analysis(
                    query=request.query,
                    context=contexts,
                    analysis_type=request.analysis_type
                ):
                    analysis_buffer += chunk
                    await websocket.send_json({
                        "type": "analysis_chunk",
                        "content": chunk
                    })
                
                # Generate actions
                await websocket.send_json({
                    "type": "status",
                    "content": "Generating suggested actions..."
                })
                
                # Send final
                await websocket.send_json({
                    "type": "complete",
                    "full_analysis": analysis_buffer,
                    "actions": []  # Simplified for streaming
                })
                
            elif data.get("type") == "agent_loop":
                # Advanced autonomous mode
                result = await services["sambanova"].agent_loop(
                    initial_query=data["query"],
                    context_retriever=lambda q: services["vector_store"].search(
                        workspace_id=data.get("workspace_id", "default"),
                        query=q
                    ),
                    action_executor=lambda a: {"status": "simulated", "action": a}
                )
                
                await websocket.send_json({
                    "type": "agent_complete",
                    "result": result
                })
                
    except WebSocketDisconnect:
        print("Client disconnected")
    except Exception as e:
        await websocket.send_json({
            "type": "error",
            "content": str(e)
        })


# ═════════════════════════════════════════════════════════════════
# HEALTH & UTILS
# ═════════════════════════════════════════════════════════════════

@app.get("/health")
async def health():
    return {
        "status": "healthy",
        "services": {
            "sambanova": "connected",
            "vector_store": "connected"
        }
    }


if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)