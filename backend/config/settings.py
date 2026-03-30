from pydantic_settings import BaseSettings
from pydantic import Field, model_validator
from typing import Optional
import base64


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

    # ActiveCampaign
    activecampaign_api_key: Optional[str] = Field(default=None)
    activecampaign_api_url: Optional[str] = Field(default=None)

    # WhatsApp (API direta Meta)
    whatsapp_access_token: Optional[str] = Field(default=None)
    whatsapp_phone_number_id: Optional[str] = Field(default=None)
    whatsapp_waba_id: Optional[str] = Field(default=None)
    whatsapp_template_name: str = Field(default="teste0004")

    # Email (Resend)
    resend_api_key: Optional[str] = Field(default=None)
    email_from: str = Field(default="onboarding@resend.dev")

    # Google Calendar
    google_service_account_json: Optional[str] = Field(default=None)
    google_service_account_json_b64: Optional[str] = Field(default=None)
    google_calendar_id: Optional[str] = Field(default=None)
    google_delegate_email: Optional[str] = Field(default=None, description="Email do usuario Workspace para delegacao (necessario para criar Google Meet)")

    @model_validator(mode="after")
    def decode_google_sa_b64(self):
        if not self.google_service_account_json and self.google_service_account_json_b64:
            self.google_service_account_json = base64.b64decode(
                self.google_service_account_json_b64
            ).decode("utf-8")
        return self

    class Config:
        env_file = ".env"
        env_file_encoding = "utf-8"
        case_sensitive = False
        extra = "ignore"


settings = Settings()
