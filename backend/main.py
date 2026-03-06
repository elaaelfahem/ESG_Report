"""
ESG Multi-Agent Reporting Suite — FastAPI Backend
"""
import os
from contextlib import asynccontextmanager
from fastapi import FastAPI, WebSocket, WebSocketDisconnect
from fastapi.middleware.cors import CORSMiddleware
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

from backend.routers import upload, pipeline, reports
from backend.core.websocket import manager
from backend.core.config import setup_logging, ORGANIZATION, REPORT_YEAR

logger = setup_logging(__name__)


@asynccontextmanager
async def lifespan(app: FastAPI):
    """Startup and shutdown events."""
    logger.info(" ESG Backend starting...")
    logger.info(f"   Organization: {ORGANIZATION}")
    logger.info(f"   Report Year: {REPORT_YEAR}")
    yield
    logger.info(" ESG Backend shutting down...")


app = FastAPI(
    title="ESG Multi-Agent Reporting Suite",
    description="AI-powered ESG report generation using RAG and multi-agent orchestration",
    version="1.0.0",
    lifespan=lifespan,
)

# CORS — allow React dev server
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Include routers
app.include_router(upload.router)
app.include_router(pipeline.router)
app.include_router(reports.router)


# WebSocket endpoint for real-time progress
@app.websocket("/ws/progress")
async def websocket_endpoint(websocket: WebSocket):
    await manager.connect(websocket)
    try:
        while True:
            # Keep connection alive, wait for client messages
            data = await websocket.receive_text()
            # Client can send "ping" to keep alive
            if data == "ping":
                await websocket.send_json({"type": "pong"})
    except WebSocketDisconnect:
        manager.disconnect(websocket)


# Health check
@app.get("/api/health")
async def health_check():
    return {
        "status": "healthy",
        "service": "ESG Multi-Agent Reporting Suite",
        "organization": ORGANIZATION,
        "report_year": REPORT_YEAR,
    }


@app.get("/api/config")
async def get_config():
    """Get non-sensitive configuration."""
    from backend.core.config import (
        KPI_CATEGORIES, FRAMEWORKS, LLM_MODEL,
        EMBEDDING_MODEL, CHUNK_SIZE, CHUNK_OVERLAP,
    )
    return {
        "organization": ORGANIZATION,
        "report_year": REPORT_YEAR,
        "llm_model": LLM_MODEL,
        "embedding_model": EMBEDDING_MODEL,
        "chunk_size": CHUNK_SIZE,
        "chunk_overlap": CHUNK_OVERLAP,
        "kpi_categories": KPI_CATEGORIES,
        "frameworks": {k: v["name"] for k, v in FRAMEWORKS.items()},
    }
