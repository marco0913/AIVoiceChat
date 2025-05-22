class OpenAIError(Exception):
    """Base exception for OpenAI API errors"""


class LLMServiceError(OpenAIError):
    """Exception for LLM service errors"""


class TTSServiceError(OpenAIError):
    """Exception for TTS service errors"""


class WebSocketError(Exception):
    """Exception for WebSocket related errors"""


class InvalidInputError(Exception):
    """Exception for invalid user input"""

    def __init__(self, message: str = "Invalid input provided"):
        self.message = message
        super().__init__(self.message)
