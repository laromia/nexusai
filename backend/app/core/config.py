from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    APP_NAME: str = "NexusAI"
    APP_VERSION: str = "1.0.0"
    API_V1_PREFIX: str = "/api/v1"

    ENVIRONMENT: str = "development"
    DEBUG: bool = True

    OPENAI_API_KEY: str = ""
    GEMINI_API_KEY: str = ""

    OPENAI_MODEL: str = "gpt-4.1-mini"
    GEMINI_MODEL: str = "gemini-2.5-flash"

    PROVIDER_TIMEOUT: float = 30.0

    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        extra="ignore"
    )


settings = Settings()