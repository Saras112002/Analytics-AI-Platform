import json
import os
import time
from pathlib import Path
from typing import Optional

from fastapi import APIRouter, File, Form, HTTPException, UploadFile
from pydantic import BaseModel, Field

from backend.pipelines.file_processor import (
    generate_summary,
    read_file,
    read_file_bytes,
    validate_file,
)
from backend.agents.orchestrator import orchestrator
from backend.config import get_settings
from backend.ml.anomaly_detector import detect_anomalies
from backend.ml.feature_analyzer import analyze_drivers
settings = get_settings()
router = APIRouter()

class FullAnalysisRequest(BaseModel):
    """
    Defines what the user sends. They choose which analyses to run
    and (optionally) which column to predict.
    """
    filename: str
    analyses: list[str] = Field(
        default_factory=lambda: ["anomalies", "drivers", "summary"]
    )
    target_column: Optional[str] = None


def _run_analysis(df, filename: str, analyses: list[str], target_column: Optional[str]):
    """Run the analysis pipeline for an already-loaded dataframe."""
    summary = generate_summary(df, filename)
    if "anomalies" in analyses:
        summary["anomaly_evidence"] = detect_anomalies(df)
    if "drivers" in analyses:
        summary["driver_evidence"] = analyze_drivers(df, target=target_column)

    start_time = time.time()
    try:
        analysis = orchestrator.run(summary)
    except Exception as exc:
        raise HTTPException(
            status_code=500,
            detail=f"AI orchestration failed: {str(exc)}"
        ) from exc
    elapsed = round(time.time() - start_time, 2)

    return {
        "message": "Full analysis complete",
        "filename": filename,
        "execution_time_seconds": elapsed,
        "data_summary": summary,
        "analysis": analysis,
        "disclaimer": "AI-generated draft. All figures must be verified against source data before use in decisions.",
    }


@router.post("/full-analysis-file")
async def full_analysis_file(
    file: UploadFile = File(...),
    analyses: str = Form('["anomalies", "drivers", "summary"]'),
    target_column: Optional[str] = Form(None),
):
    """Analyze a multipart upload in one serverless invocation."""
    filename = Path(file.filename or "upload").name
    content = await file.read()
    validation = validate_file(filename, len(content))
    if not validation["valid"]:
        raise HTTPException(status_code=400, detail=validation["error"])

    try:
        requested_analyses = json.loads(analyses)
    except json.JSONDecodeError as exc:
        raise HTTPException(status_code=400, detail="Invalid analyses value") from exc
    allowed_analyses = {"anomalies", "drivers", "summary"}
    if not isinstance(requested_analyses, list) or not all(
        isinstance(item, str) and item in allowed_analyses
        for item in requested_analyses
    ):
        raise HTTPException(status_code=400, detail="Invalid analyses value")

    try:
        df = read_file_bytes(filename, content)
    except Exception as exc:
        raise HTTPException(
            status_code=400,
            detail=f"Could not read file: {str(exc)}"
        ) from exc

    return _run_analysis(df, filename, requested_analyses, target_column)


@router.post("/full-analysis")
async def full_analysis(request: FullAnalysisRequest):
    """
    Runs the complete agent team on an uploaded file
    Returns executive brief + detailed findings from all agents
    """

    # Step 1 - Build full filepath
    filename = Path(request.filename).name
    filepath = os.path.join(settings.UPLOAD_DIR, filename)

    # Step 2 - Check if file exists
    if not os.path.exists(filepath):
        raise HTTPException(
            status_code=404,
            detail=f"File '{filename}' not found. Upload it first."
        )

    # Step 3 - Read the file
    try:
        df = read_file(filepath)
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"Could not read file: {str(e)}"
        )

    return _run_analysis(
        df,
        filename,
        request.analyses,
        request.target_column,
    )
