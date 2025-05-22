from openai import AsyncOpenAI
from app.utils.config import settings
from app.models.schemas import LLMRequest, LLMResponse
from app.utils.exceptions import LLMServiceError


class LLMService:
    """Handles asynchronous communication with OpenAI's LLM API."""

    def __init__(self):
        self.client = AsyncOpenAI(api_key=settings.openai_api_key)
        self.model = settings.openai_llm_model

    async def get_response(self, request: LLMRequest) -> LLMResponse:
        """Generates a completion from the LLM for the given request.

        Args:
            request: Contains input text and optional conversation ID

        Returns:
            LLMResponse with generated text and conversation ID

        Raises:
            LLMServiceError: If the API request fails
        """
        try:
            response = await self.client.chat.completions.create(
                model=self.model,
                messages=[{"role": "user", "content": request.text}],
                max_tokens=50,
                temperature=0.7
            )
            return LLMResponse(
                text=response.choices[0].message.content,
                conversation_id=request.conversation_id
            )
        except Exception as e:
            raise LLMServiceError(str(e))
