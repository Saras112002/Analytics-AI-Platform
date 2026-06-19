import os
import shutil
from fastapi import APIRouter, UploadFile, File, HTTPException
from backend.pipelines.file_processor import validate_file, read_file, generate_summary
from backend.config import get_settings

settings = get_settings()

router = APIRouter()

@router.post("/upload")
async def upload_file(file: UploadFile = File(...)):
    """
    Receives a file from the user
    Validates it, saves it, processes it
    Returns a summary of the data
    """

    # Step 1 - Get file size
    file_content = await file.read()
    file_size = len(file_content)

    # Step 2 - Validate the file
    validation = validate_file(file.filename, file_size)
    if not validation["valid"]:
        raise HTTPException(
            status_code=400,
            detail=validation["error"]
        )

    # Step 3 - Save file to disk
    os.makedirs(settings.UPLOAD_DIR, exist_ok=True)
    filepath = os.path.join(settings.UPLOAD_DIR, file.filename)

    with open(filepath, "wb") as buffer:
        buffer.write(file_content)

    # Step 4 - Process the file
    df = read_file(filepath)

    # Step 5 - Generate and return summary
    summary = generate_summary(df, file.filename)

    return {
        "message": "File uploaded successfully",
        "summary": summary
    }