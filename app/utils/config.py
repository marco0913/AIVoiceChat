from pydantic_settings import BaseSettings


class Settings(BaseSettings):
    openai_api_key: str
    openai_llm_model: str = "gpt-3.5-turbo"
    openai_tts_model: str = "tts-1"
    openai_tts_voice: str = "fable"

    class Config:
        env_file = ".env"


settings = Settings()
