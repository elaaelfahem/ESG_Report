"""
Upload Router: Handles PDF file uploads.
"""
import os
import shutil
from typing import List
from fastapi import APIRouter, UploadFile, File, HTTPException

from backend.core.config import DATA_FOLDER, setup_logging

logger = setup_logging(__name__)
router = APIRouter(prefix="/api", tags=["upload"])


@router.post("/upload")
async def upload_files(files: List[UploadFile] = File(...)):
    """Upload one or more PDF files to the data directory."""
    if not files:
        raise HTTPException(status_code=400, detail="No files provided")
    
    uploaded = []
    errors = []
    
    for file in files:
        if not file.filename.lower().endswith(".pdf"):
            errors.append(f"{file.filename}: Not a PDF file")
            continue
        
        try:
            file_path = os.path.join(DATA_FOLDER, file.filename)
            with open(file_path, "wb") as buffer:
                content = await file.read()
                buffer.write(content)
            
            uploaded.append({
                "filename": file.filename,
                "size_bytes": len(content),
                "path": file_path,
            })
            logger.info(f"Uploaded: {file.filename} ({len(content)} bytes)")
        except Exception as e:
            errors.append(f"{file.filename}: {str(e)}")
            logger.error(f"Upload failed: {file.filename} — {e}")
    
    return {
        "uploaded": uploaded,
        "errors": errors,
        "total_uploaded": len(uploaded),
        "total_errors": len(errors),
    }


@router.get("/files")
async def list_files():
    """List all uploaded PDF files."""
    files = []
    if os.path.isdir(DATA_FOLDER):
        for filename in os.listdir(DATA_FOLDER):
            if filename.lower().endswith(".pdf"):
                filepath = os.path.join(DATA_FOLDER, filename)
                files.append({
                    "filename": filename,
                    "size_bytes": os.path.getsize(filepath),
                })
    
    return {"files": files, "total": len(files)}


@router.delete("/files/{filename}")
async def delete_file(filename: str):
    """Delete an uploaded PDF file."""
    filepath = os.path.join(DATA_FOLDER, filename)
    if not os.path.exists(filepath):
        raise HTTPException(status_code=404, detail="File not found")
    
    os.remove(filepath)
    logger.info(f"Deleted: {filename}")
    return {"message": f"Deleted {filename}"}
