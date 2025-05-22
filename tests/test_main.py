"""Tests for WebSocket service and related components."""

import pytest
import os
from starlette.websockets import WebSocketDisconnect
from app.services.conversation_manager import ConversationManager
from app.services.ws_manager import WebSocketManager
from app.models.schemas import LLMRequest, TTSRequest


@pytest.mark.asyncio
async def test_websocket_connection(client):
    """Test basic WebSocket connection."""
    with client.websocket_connect("/ws/chat") as websocket:
        websocket.send_text("Hello")
        response = websocket.receive_text()
        assert response == "You said: Hello"


@pytest.mark.asyncio
async def test_graceful_disconnect(client):
    """Test WebSocket disconnection."""
    with client.websocket_connect("/ws/chat") as websocket:
        websocket.send_text("disconnect")
        with pytest.raises(WebSocketDisconnect):
            websocket.receive_text()


@pytest.mark.asyncio
async def test_invalid_message_type(client):
    """Test invalid message handling."""
    with client.websocket_connect("/ws/chat") as websocket:
        websocket.send_bytes(b"invalid")
        with pytest.raises(WebSocketDisconnect) as exc_info:
            websocket.receive_text()
        assert exc_info.value.code == 1003


@pytest.mark.asyncio
async def test_llm_service_success(mock_llm_service):
    """Test successful LLM response."""
    response = await mock_llm_service.get_response(LLMRequest(text="test"))
    assert "Processed: test" in response.text


@pytest.mark.asyncio
async def test_llm_service_failure(mock_llm_service):
    """Test LLM error case."""
    with pytest.raises(Exception, match="Simulated LLM failure"):
        await mock_llm_service.get_response(LLMRequest(text="fail"))


@pytest.mark.asyncio
async def test_tts_service_success(mock_tts_service):
    """Test successful TTS conversion."""
    response = await mock_tts_service.text_to_speech(TTSRequest(text="test"))
    assert b"audio_test" in response.audio


@pytest.mark.asyncio
async def test_tts_service_failure(mock_tts_service):
    """Test TTS error case."""
    with pytest.raises(Exception, match="Simulated TTS failure"):
        await mock_tts_service.text_to_speech(TTSRequest(text="fail"))


@pytest.mark.integration
@pytest.mark.asyncio
async def test_real_llm_tts_integration():
    """Test full pipeline with real services."""
    if not os.getenv("OPENAI_API_KEY"):
        pytest.skip("Integration test - no API key set")

    from app.services.llm_service import LLMService
    from app.services.tts_service import TTSService

    llm = LLMService()
    tts = TTSService()

    llm_response = await llm.get_response(LLMRequest(text="Hello world"))
    assert isinstance(llm_response.text, str)
    assert len(llm_response.text) > 5

    tts_response = await tts.text_to_speech(TTSRequest(text=llm_response.text))
    assert len(tts_response.audio) > 1000


@pytest.mark.asyncio
async def test_conversation_manager_simple(mock_llm_service, mock_tts_service):
    """Test basic conversation flow."""
    ws_manager = WebSocketManager()
    client_id = "test_client"

    class MockWebSocket:
        async def accept(self): pass
        async def send_text(self, msg): pass
        async def send_bytes(self, data): pass

    mock_ws = MockWebSocket()
    await ws_manager.connect(mock_ws, client_id)

    manager = ConversationManager(
        mock_llm_service,
        mock_tts_service,
        ws_manager,
        client_id
    )

    await manager.add_message("hello")
    assert manager.busy
    await manager.ready_for_next()
    assert not manager.busy
