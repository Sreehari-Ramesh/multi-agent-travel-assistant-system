import os
from functools import lru_cache
from pydantic import Field, ConfigDict
from pydantic_settings import BaseSettings
from dotenv import load_dotenv
load_dotenv()

class Settings(BaseSettings):
    model_config = ConfigDict(extra="ignore")
    app_name: str = "dubai-travel-multi-agent"
    api_prefix: str = "/api"

    # Gemini / ADK
    openai_api_key: str = Field(..., env="OPENAI_API_KEY")
    adk_model: str = "gpt-4.1-2025-04-14"

    # CORS / frontend
    frontend_origin: str | None = Field(default=None, env="FRONTEND_ORIGIN")

    # Email escalation (simple SMTP config)
    smtp_host: str | None = Field(default=None, env="SMTP_HOST")
    smtp_port: int | None = Field(default=None, env="SMTP_PORT")
    smtp_username: str | None = Field(default=None, env="SMTP_USERNAME")
    smtp_password: str | None = Field(default=None, env="SMTP_PASSWORD")
    smtp_from_email: str | None = Field(default=None, env="SMTP_FROM_EMAIL")
    supervisor_email: str | None = Field(default=None, env="SUPERVISOR_EMAIL")

    # IMAP (ADD THIS BLOCK)
    supervisor_imap_host: str | None = Field(default=None, env="SUPERVISOR_IMAP_HOST")
    supervisor_imap_port: int | None = Field(default=None, env="SUPERVISOR_IMAP_PORT")
    supervisor_imap_email: str | None = Field(default=None, env="SUPERVISOR_IMAP_EMAIL")
    supervisor_imap_app_password: str | None = Field(default=None, env="SUPERVISOR_IMAP_APP_PASSWORD")

    # class Config:
    #     env_file = ".env"
    #     env_file_encoding = "utf-8"


@lru_cache
def get_settings() -> Settings:
    return Settings()

