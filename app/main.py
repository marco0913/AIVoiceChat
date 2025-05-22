import json
from fastapi import FastAPI, WebSocket, WebSocketDisconnect
from fastapi.responses import FileResponse, JSONResponse
from fastapi.staticfiles import StaticFiles
from app.services.llm_service import LLMService
from app.services.tts_service import TTSService
from app.services.ws_manager import WebSocketManager
from app.services.conversation_manager import ConversationManager

app = FastAPI(title="Conversational WebSocket Service")
app.mount("/static", StaticFiles(directory="static"), name="static")

llm_service = LLMService()
tts_service = TTSService()
ws_manager = WebSocketManager()


@app.get("/")
async def get_interface():
    """Serve the chat interface HTML page."""
    try:
        return FileResponse("index.html")
    except Exception as e:
        return JSONResponse(500, {"error": f"Interface load failed: {e}"})


async def _handle_websocket_message(manager: ConversationManager, message: dict):
    """Route WebSocket messages to appropriate handlers."""
    msg_type = message.get("type")
    if msg_type == "message":
        text = message.get("text", "")
        await manager.add_message(text)
    elif msg_type == "ready_for_next":
        await manager.ready_for_next()
    else:
        await ws_manager.send_text(
            manager.client_id,
            f"Unknown message type: {msg_type}"
        )


@app.websocket("/ws/{client_id}")
async def websocket_endpoint(websocket: WebSocket, client_id: str):
    """Main WebSocket endpoint for real-time conversation handling."""
    await ws_manager.connect(websocket, client_id)

    manager = ConversationManager(
        llm_service=llm_service,
        tts_service=tts_service,
        ws_manager=ws_manager,
        client_id=client_id
    )

    try:
        while True:
            raw = await websocket.receive_text()
            try:
                message = json.loads(raw)
                await _handle_websocket_message(manager, message)
            except json.JSONDecodeError:
                await ws_manager.send_text(client_id, "Invalid message format")
    except WebSocketDisconnect:
        pass
    finally:
        ws_manager.disconnect(client_id)
