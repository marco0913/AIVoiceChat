import asyncio
from app.models.schemas import LLMRequest, TTSRequest
from app.utils.exceptions import InvalidInputError, LLMServiceError, TTSServiceError


class ConversationManager:
    def __init__(self, llm_service, tts_service, ws_manager, client_id: str):
        self.llm_service = llm_service
        self.tts_service = tts_service
        self.ws_manager = ws_manager
        self.client_id = client_id
        self._busy = False
        self._queue: asyncio.Queue[str] = asyncio.Queue()

    @property
    def busy(self) -> bool:
        return self._busy

    async def add_message(self, text: str):
        """Add a message to the processing queue"""
        if self._busy:
            await self._queue.put(text)
            await self.ws_manager.send_text(
                self.client_id,
                "Please wait until current audio finishes."
            )
        else:
            await self._process_message(text)

    async def ready_for_next(self):
        """Signal that client is ready for next message"""
        self._busy = False
        if not self._queue.empty():
            next_text = await self._queue.get()
            await self._process_message(next_text)

    async def _process_message(self, text: str):
        """Process a single message through the entire pipeline"""
        self._busy = True
        try:
            await self._validate_input(text)
            llm_response = await self._call_llm(text)
            await self._process_tts(llm_response.text)
        except (LLMServiceError, TTSServiceError) as e:
            await self._handle_error(str(e))
        except Exception as e:
            await self._handle_error(f"Unexpected error: {e}")

    async def _validate_input(self, text: str):
        """Validate the input text"""
        if not text.strip():
            raise InvalidInputError("Empty message received")

    async def _call_llm(self, text: str):
        """Call the LLM service"""
        try:
            return await self.llm_service.get_response(LLMRequest(text=text))
        except Exception as e:
            raise LLMServiceError(f"LLM processing failed: {e}")

    async def _process_tts(self, text: str):
        """Process text through TTS and send audio"""
        try:
            tts_response = await self.tts_service.text_to_speech(TTSRequest(text=text))
            await self.ws_manager.send_bytes(self.client_id, tts_response.audio)
        except Exception as e:
            raise TTSServiceError(f"TTS conversion failed: {e}")

    async def _handle_error(self, error_msg: str):
        """Handle any errors that occur during processing"""
        await self.ws_manager.send_text(self.client_id, error_msg)
        self._busy = False
        if not self._queue.empty():
            next_text = await self._queue.get()
            await self._process_message(next_text)
