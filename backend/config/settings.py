from pydantic_settings import BaseSettings
from pydantic import Field
from typing import Optional


class Settings(BaseSettings):

    # App
    app_name: str = Field(default="FlowQuote Backend")
    app_version: str = Field(default="1.0.0")
    debug: bool = Field(default=False)

    # MongoDB
    mongodb_uri: str = Field(..., description="URI de conexao do MongoDB Atlas")
    mongodb_database: str = Field(default="flowquote")

    # CORS
    cors_origins: list[str] = Field(default=["*"])

    # AI Provider: "openai" ou "anthropic"
    ai_provider: str = Field(default="openai")

    # OpenAI
    openai_api_key: Optional[str] = Field(default=None)
    openai_base_url: Optional[str] = Field(default=None)
    openai_model: str = Field(default="gpt-4o-mini")

    # Anthropic
    anthropic_api_key: Optional[str] = Field(default=None)
    anthropic_model: str = Field(default="claude-sonnet-4-20250514")

    class Config:
        env_file = ".env"
        env_file_encoding = "utf-8"
        case_sensitive = False
        extra = "ignore"


settings = Settings()
