from openai import AsyncOpenAI
from app.utils.config import settings
from app.models.schemas import TTSRequest, AudioResponse
from app.utils.exceptions import TTSServiceError


class TTSService:
    """Handles text-to-speech conversion using OpenAI's audio API."""

    def __init__(self):
        self.client = AsyncOpenAI(api_key=settings.openai_api_key)
        self.model = settings.openai_tts_model
        self.voice = settings.openai_tts_voice

    async def text_to_speech(self, request: TTSRequest) -> AudioResponse:
        """Converts text to speech audio.

        Args:
            request: Contains text to synthesize and format preferences

        Returns:
            AudioResponse with MP3 audio data

        Raises:
            TTSServiceError: If audio generation fails
        """
        try:
            response = await self.client.audio.speech.create(
                model=self.model,
                voice=self.voice,
                input=request.text,
                response_format="mp3"
            )
            audio_data = await response.aread()
            return AudioResponse(audio=audio_data)
        except Exception as e:
            raise TTSServiceError(str(e))
