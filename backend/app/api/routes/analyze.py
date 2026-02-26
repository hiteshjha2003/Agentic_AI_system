# backend/app/api/routes/analyze.py
# Similar to above, optional if consolidated in main.py

from fastapi import APIRouter
from app.models.schemas import AnalysisRequest, AnalysisResponse

router = APIRouter(prefix="/analyze", tags=["analysis"])

@router.post("/", response_model=AnalysisResponse)
async def analyze(request: AnalysisRequest, workspace_id: str = "default"):

    return AnalysisResponse(
        summary="Test summary",
        detailed_analysis="Detailed explanation here",
        suggested_actions=[]
    )
