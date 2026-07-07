import os
import time
from fastapi import APIRouter, HTTPException
from pydantic import BaseModel
from backend.pipelines.file_processor import read_file, generate_summary
from backend.agents.orchestrator import orchestrator
from backend.config import get_settings
from backend.ml.anomaly_detector import detect_anomalies
settings = get_settings()
router = APIRouter()


class FullAnalysisRequest(BaseModel):
    """
    Defines what the user must send to this endpoint
    """
    filename: str


@router.post("/full-analysis")
async def full_analysis(request: FullAnalysisRequest):
    """
    Runs the complete agent team on an uploaded file
    Returns executive brief + detailed findings from all agents
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

    # Step 4 - Generate data summary
    summary = generate_summary(df, request.filename)
    summary["anomaly_evidence"] = detect_anomalies(df)

    # Step 5 - Run the full orchestrator (all 4 agents)
    start_time = time.time()
    try:
        analysis = orchestrator.run(summary)
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"AI orchestration failed: {str(e)}"
        )
    elapsed = round(time.time() - start_time, 2)

    # Step 6 - Return everything
    return {
        "message": "Full analysis complete",
        "filename": request.filename,
        "execution_time_seconds": elapsed,
        "data_summary": summary,
        "analysis": analysis,
        "disclaimer": "AI-generated draft. All figures must be verified against source data before use in decisions.",
    }