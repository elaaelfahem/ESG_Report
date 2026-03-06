"""
Pipeline Router: Trigger and monitor the ESG pipeline.
"""
import asyncio
import uuid
from datetime import datetime
from typing import Dict, Any, List, Optional
from fastapi import APIRouter, HTTPException, BackgroundTasks
from pydantic import BaseModel

from backend.services.orchestrator import run_esg_pipeline
from backend.core.websocket import manager
from backend.core.config import setup_logging


logger = setup_logging(__name__)
router = APIRouter(prefix="/api/pipeline", tags=["pipeline"])

# In-memory pipeline run storage
pipeline_runs: Dict[str, Dict[str, Any]] = {}


class PipelineRequest(BaseModel):
    topic: str = "Sustainability Report 2024"
    questions: Optional[List[str]] = None


def _run_pipeline_task(run_id: str, topic: str, questions: list):
    """Run the pipeline in a background thread."""
    pipeline_runs[run_id]["status"] = "running"
    pipeline_runs[run_id]["started_at"] = datetime.now().isoformat()
    
    def progress_callback(stage, status, detail, progress):
        pipeline_runs[run_id]["current_stage"] = stage
        pipeline_runs[run_id]["progress"] = progress
        pipeline_runs[run_id]["detail"] = detail
        # We also send via WebSocket from the sync thread
        try:
            loop = asyncio.new_event_loop()
            asyncio.set_event_loop(loop)
            loop.run_until_complete(
                manager.send_progress(stage, status, detail, progress)
            )
            loop.close()
        except Exception:
            pass  # WebSocket send may fail if no clients connected
    
    try:
        result = run_esg_pipeline(topic, questions, progress_callback)
        pipeline_runs[run_id]["status"] = "complete"
        pipeline_runs[run_id]["result"] = result
        pipeline_runs[run_id]["completed_at"] = datetime.now().isoformat()
        pipeline_runs[run_id]["progress"] = 100
    except Exception as e:
        logger.error(f"Pipeline run {run_id} failed: {e}")
        pipeline_runs[run_id]["status"] = "error"
        pipeline_runs[run_id]["error"] = str(e)
        pipeline_runs[run_id]["completed_at"] = datetime.now().isoformat()


@router.post("/run")
async def run_pipeline(request: PipelineRequest, background_tasks: BackgroundTasks):
    """Trigger the full ESG pipeline in the background."""
    run_id = str(uuid.uuid4())[:8]
    
    pipeline_runs[run_id] = {
        "id": run_id,
        "topic": request.topic,
        "questions": request.questions,
        "status": "queued",
        "progress": 0,
        "current_stage": "init",
        "detail": "",
        "created_at": datetime.now().isoformat(),
    }
    
    background_tasks.add_task(_run_pipeline_task, run_id, request.topic, request.questions)
    
    return {
        "run_id": run_id,
        "status": "queued",
        "message": "Pipeline started. Connect to /ws/progress for real-time updates.",
    }


@router.get("/status/{run_id}")
async def get_pipeline_status(run_id: str):
    """Get the status of a pipeline run."""
    if run_id not in pipeline_runs:
        raise HTTPException(status_code=404, detail="Pipeline run not found")
    
    run = pipeline_runs[run_id]
    
    # Don't send full result in status — use /reports endpoint for that
    response = {k: v for k, v in run.items() if k != "result"}
    response["has_result"] = "result" in run
    
    return response


@router.get("/runs")
async def list_pipeline_runs():
    """List all pipeline runs."""
    runs = []
    for run_id, run in pipeline_runs.items():
        runs.append({
            "id": run_id,
            "topic": run.get("topic"),
            "status": run.get("status"),
            "progress": run.get("progress", 0),
            "created_at": run.get("created_at"),
            "completed_at": run.get("completed_at"),
        })
    return {"runs": runs}


@router.get("/result/{run_id}")
async def get_pipeline_result(run_id: str):
    """Get the full result of a completed pipeline run."""
    if run_id not in pipeline_runs:
        raise HTTPException(status_code=404, detail="Pipeline run not found")
    
    run = pipeline_runs[run_id]
    if run["status"] != "complete":
        raise HTTPException(status_code=400, detail=f"Pipeline is {run['status']}, not complete")
    
    return run.get("result", {})
