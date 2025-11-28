from __future__ import annotations

import os
from functools import lru_cache
from typing import Optional

from pydantic import BaseModel, Field
from dotenv import load_dotenv


load_dotenv()


class Settings(BaseModel):
    """Application configuration sourced from environment variables."""

    database_url: str = Field(
        default=os.getenv("DATABASE_URL", "sqlite:///./medassist.db")
    )
    gemini_api_key: Optional[str] = Field(
        default=os.getenv("GEMINI_API_KEY"), description="Google Gemini API key."
    )
    gemini_model: str = Field(
        default=os.getenv("GEMINI_MODEL", "gemini-2.5-flash"),
        description="Gemini model name to use for LLM calls.",
    )
    log_level: str = Field(
        default=os.getenv("LOG_LEVEL", "INFO"), description="Application log level."
    )
    app_name: str = Field(default="MedAssist API")


@lru_cache
def get_settings() -> Settings:
    """Return a cached Settings instance."""

    return Settings()

