from pathlib import Path
from dotenv import load_dotenv
import pytest
from fastapi import FastAPI, WebSocket
from fastapi.testclient import TestClient
from pydantic import BaseModel
from app.main import app as real_app
from app.models.schemas import LLMRequest, TTSRequest
from starlette.websockets import WebSocketDisconnect

# Load environment variables from .env file
load_dotenv(dotenv_path=Path(__file__).parent.parent / ".env")


class LLMRequest(BaseModel):
    """Mock LLM request schema for testing."""
    text: str
    conversation_id: str | None = None


class LLMResponse(BaseModel):
    """Mock LLM response schema for testing."""
    text: str
    conversation_id: str | None = None


class TTSRequest(BaseModel):
    """Mock TTS request schema for testing."""
    text: str


class AudioResponse(BaseModel):
    """Mock audio response schema for testing."""
    audio: bytes
    format: str = "mp3"


class MockLLMService:
    """Mock LLM service that simulates success/failure responses."""

    async def get_response(self, request: LLMRequest) -> LLMResponse:
        """Return mock response or raise error for 'fail' inputs."""
        if "fail" in request.text:
            raise Exception("Simulated LLM failure")
        return LLMResponse(text=f"Processed: {request.text}")


class MockTTSService:
    """Mock TTS service that simulates success/failure responses."""

    async def text_to_speech(self, request: TTSRequest) -> AudioResponse:
        """Return mock audio or raise error for 'fail' inputs."""
        if "fail" in request.text:
            raise Exception("Simulated TTS failure")
        return AudioResponse(audio=f"audio_{request.text}".encode())


@pytest.fixture
def test_app():
    """Fixture providing a minimal FastAPI app with WebSocket endpoint."""
    app = FastAPI()

    @app.websocket("/ws/chat")
    async def chat_endpoint(websocket: WebSocket):
        """Basic echo WebSocket endpoint for testing."""
        await websocket.accept()
        try:
            while True:
                message = await websocket.receive()
                if message["type"] == "websocket.disconnect":
                    break
                if message["type"] != "websocket.receive":
                    continue
                if "text" not in message:
                    await websocket.close(code=1003)
                    break
                if message["text"] == "disconnect":
                    await websocket.close(code=1000)
                    break
                await websocket.send_text(f"You said: {message['text']}")
        except WebSocketDisconnect:
            pass

    return app


@pytest.fixture
def mock_llm_service():
    """Fixture providing a mocked LLM service instance."""
    return MockLLMService()


@pytest.fixture
def mock_tts_service():
    """Fixture providing a mocked TTS service instance."""
    return MockTTSService()


@pytest.fixture
def client(request, test_app):
    """Fixture providing a test client for integration or unit tests.

    Returns:
        TestClient: Real app client for integration tests,
                   mock app client for unit tests
    """
    if request.node.get_closest_marker("integration"):
        return TestClient(real_app)
    return TestClient(test_app)
