from fastapi import WebSocket
from typing import Dict
from app.utils.exceptions import WebSocketError


class WebSocketManager:
    """Manages active WebSocket connections and message routing."""

    def __init__(self):
        self.active_connections: Dict[str, WebSocket] = {}

    async def connect(self, websocket: WebSocket, client_id: str):
        """Accepts new WebSocket connection and registers it."""
        await websocket.accept()
        self.active_connections[client_id] = websocket

    def disconnect(self, client_id: str):
        """Removes a WebSocket connection from active connections."""
        if client_id in self.active_connections:
            del self.active_connections[client_id]

    async def send_text(self, client_id: str, message: str):
        """Sends text message to specified client."""
        if client_id not in self.active_connections:
            raise WebSocketError(
                f"No active connection for client {client_id}")

        websocket = self.active_connections[client_id]
        await websocket.send_text(message)

    async def send_bytes(self, client_id: str, data: bytes):
        """Sends binary data to specified client."""
        if client_id not in self.active_connections:
            raise WebSocketError(
                f"No active connection for client {client_id}")

        websocket = self.active_connections[client_id]
        await websocket.send_bytes(data)
