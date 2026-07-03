import os
from fastapi import APIRouter, HTTPException
from pydantic import BaseModel
from backend.pipelines.file_processor import read_file, generate_summary
from backend.agents.insight_agent import insight_agent
from backend.config import get_settings
from backend.agents.orchestrator import run_all

settings = get_settings()
router = APIRouter()


class AnalyzeRequest(BaseModel):
    """
    Defines what the user must send to this endpoint
    """
    filename: str


@router.post("/analyze")
async def analyze_file(request: AnalyzeRequest):
    """
    Takes a previously uploaded filename
    Returns AI-generated business insights
    """

    # Step 1 - Build full filepath
    filepath = os.path.join(settings.UPLOAD_DIR, request.filename)

    # Step 2 - Check if file exists
    if not os.path.exists(filepath):
        raise HTTPException(
            status_code=404,
            detail=f"File '{request.filename}' not found. Upload it first."
        )

    # Step 3 - Read the file
    try:
        df = read_file(filepath)
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"Could not read file: {str(e)}"
        )

    # Step 4 - Generate summary (same as upload endpoint)
    summary = generate_summary(df, request.filename)

    # Step 5 — fan out to all agents
    analysis = run_all(summary)

# Step 6
    return {
    "message": "Analysis complete",
    "filename": request.filename,
    "summary": summary,
    "ai_analysis": analysis,   # was "ai_insights"
}