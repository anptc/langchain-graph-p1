"""Application settings. Secrets stay in the environment, never in specialist code."""

from __future__ import annotations

from functools import lru_cache

from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        extra="ignore",
    )

    google_cloud_project: str | None = None
    google_cloud_location: str = "us-central1"
    gemini_model: str = "gemini-2.5-flash"
    google_genai_use_vertexai: bool = True

    alphavantage_api_key: str | None = None

    default_user_id: str = "local-dev"
    default_tenant_id: str = "local"
    # Comma-separated scopes, or * for every catalogued agent. Demo stand-in for IdP claims.
    default_scopes: str = "*"
    default_role: str = "admin"

    http_user_agent: str = "enterprise-agent"
    http_timeout_seconds: int = 30
    tool_json_max_chars: int = 4000


@lru_cache
def get_settings() -> Settings:
    return Settings()
