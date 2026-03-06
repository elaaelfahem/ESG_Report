"""
Reports Router: List, view, and download generated reports (Markdown + PDF).
"""
import os
from fastapi import APIRouter, HTTPException
from fastapi.responses import FileResponse, Response

from backend.core.config import REPORTS_DIR, setup_logging

logger = setup_logging(__name__)
router = APIRouter(prefix="/api/reports", tags=["reports"])


@router.get("/")
async def list_reports():
    """List all generated reports (both .md and .pdf)."""
    reports = []
    if os.path.isdir(REPORTS_DIR):
        seen_stems = {}
        for filename in sorted(os.listdir(REPORTS_DIR), reverse=True):
            filepath = os.path.join(REPORTS_DIR, filename)
            stem = filename.rsplit('.', 1)[0]
            ext = filename.rsplit('.', 1)[-1] if '.' in filename else ''

            if ext in ('md', 'pdf', 'html'):
                entry = seen_stems.setdefault(stem, {
                    "stem": stem,
                    "filename": filename,  # primary filename (md)
                    "md_filename": None,
                    "pdf_filename": None,
                    "html_filename": None,
                    "size_bytes": 0,
                    "modified_at": os.path.getmtime(filepath),
                })
                entry[f"{ext}_filename"] = filename
                if ext == 'md':
                    entry["filename"] = filename
                    entry["size_bytes"] = os.path.getsize(filepath)
                    entry["modified_at"] = os.path.getmtime(filepath)

        reports = list(seen_stems.values())

    return {"reports": reports, "total": len(reports)}


@router.get("/{filename}")
async def get_report(filename: str):
    """Get the content of a specific Markdown report."""
    # Try to find the file (md or pdf)
    filepath = os.path.join(REPORTS_DIR, filename)

    if not os.path.exists(filepath):
        raise HTTPException(status_code=404, detail="Report not found")

    if filename.endswith('.pdf'):
        raise HTTPException(
            status_code=400,
            detail="Use the /download endpoint to retrieve PDF files."
        )

    with open(filepath, "r", encoding="utf-8") as f:
        content = f.read()

    return {
        "filename": filename,
        "content": content,
        "size_bytes": os.path.getsize(filepath),
    }


@router.get("/{filename}/download")
async def download_report(filename: str):
    """Download a report (Markdown or PDF)."""
    filepath = os.path.join(REPORTS_DIR, filename)

    if not os.path.exists(filepath):
        raise HTTPException(status_code=404, detail="Report not found")

    if filename.endswith('.pdf'):
        return FileResponse(
            path=filepath,
            filename=filename,
            media_type="application/pdf",
        )
    elif filename.endswith('.html'):
        return FileResponse(
            path=filepath,
            filename=filename,
            media_type="text/html",
        )
    else:
        return FileResponse(
            path=filepath,
            filename=filename,
            media_type="text/markdown",
        )


@router.get("/{stem}/pdf")
async def get_pdf_report(stem: str):
    """Download the PDF version of a report by its stem name."""
    pdf_filename = stem if stem.endswith('.pdf') else f"{stem}.pdf"
    filepath = os.path.join(REPORTS_DIR, pdf_filename)

    if not os.path.exists(filepath):
        raise HTTPException(
            status_code=404,
            detail=f"PDF report '{pdf_filename}' not found. Run the pipeline to generate it."
        )

    return FileResponse(
        path=filepath,
        filename=pdf_filename,
        media_type="application/pdf",
    )


@router.delete("/{filename}")
async def delete_report(filename: str):
    """Delete a report (and its PDF/HTML if they exist)."""
    filepath = os.path.join(REPORTS_DIR, filename)

    if not os.path.exists(filepath):
        raise HTTPException(status_code=404, detail="Report not found")

    os.remove(filepath)
    logger.info(f"Deleted report: {filename}")

    # Also remove associated files
    stem = filename.rsplit('.', 1)[0]
    deleted = [filename]
    for ext in ('pdf', 'html'):
        companion = os.path.join(REPORTS_DIR, f"{stem}.{ext}")
        if os.path.exists(companion):
            os.remove(companion)
            deleted.append(f"{stem}.{ext}")

    return {"message": f"Deleted: {', '.join(deleted)}"}
