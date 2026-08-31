from pathlib import Path

from fastapi import APIRouter, UploadFile, File, HTTPException
from backend.pipelines.file_processor import (
    generate_summary,
    read_file_bytes,
    validate_file,
)

router = APIRouter()

@router.post("/upload")
async def upload_file(file: UploadFile = File(...)):
    """
    Receives a file from the user
    Validates and profiles it without relying on server-local persistence
    Returns a summary of the data
    """

    # Step 1 - Get file size
    filename = Path(file.filename or "upload").name
    file_content = await file.read()
    file_size = len(file_content)

    # Step 2 - Validate the file
    validation = validate_file(filename, file_size)
    if not validation["valid"]:
        raise HTTPException(
            status_code=400,
            detail=validation["error"]
        )

    # Step 3 - Process the file in memory. Vercel function instances do not
    # provide durable storage between the upload and analysis requests.
    try:
        df = read_file_bytes(filename, file_content)
    except Exception as exc:
        raise HTTPException(
            status_code=400,
            detail=f"Could not read file: {str(exc)}"
        ) from exc

    # Step 4 - Generate and return summary
    summary = generate_summary(df, filename)

    return {
        "message": "File validated successfully",
        "summary": summary
    }
