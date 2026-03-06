"""
WebSocket manager for broadcasting real-time progress to the frontend.
"""
import asyncio
import json
from typing import List
from fastapi import WebSocket


class ConnectionManager:
    """Manages WebSocket connections for real-time pipeline progress."""
    
    def __init__(self):
        self.active_connections: List[WebSocket] = []
    
    async def connect(self, websocket: WebSocket):
        await websocket.accept()
        self.active_connections.append(websocket)
    
    def disconnect(self, websocket: WebSocket):
        if websocket in self.active_connections:
            self.active_connections.remove(websocket)
    
    async def broadcast(self, message: dict):
        """Send a message to all connected clients."""
        disconnected = []
        for connection in self.active_connections:
            try:
                await connection.send_json(message)
            except Exception:
                disconnected.append(connection)
        
        for conn in disconnected:
            self.disconnect(conn)
    
    async def send_progress(self, stage: str, status: str, detail: str = "", progress: float = 0):
        """Send a structured progress update."""
        await self.broadcast({
            "type": "progress",
            "stage": stage,
            "status": status,
            "detail": detail,
            "progress": progress,
        })


# Singleton instance
manager = ConnectionManager()
