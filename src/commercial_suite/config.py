"""Environment-based configuration for optional external APIs."""

from __future__ import annotations

import os
from dataclasses import dataclass


@dataclass(frozen=True)
class Settings:
    llm_api_key: str = ""
    llm_model: str = "gpt-4o-mini"
    llm_api_base: str = "https://api.openai.com/v1"
    tts_api_key: str = ""
    image_api_key: str = ""


def load_settings() -> Settings:
    """Read optional API settings from the environment (.env is not auto-loaded)."""
    return Settings(
        llm_api_key=os.environ.get("LLM_API_KEY", ""),
        llm_model=os.environ.get("LLM_MODEL", "gpt-4o-mini"),
        llm_api_base=os.environ.get("LLM_API_BASE", "https://api.openai.com/v1"),
        tts_api_key=os.environ.get("TTS_API_KEY", ""),
        image_api_key=os.environ.get("IMAGE_API_KEY", ""),
    )
