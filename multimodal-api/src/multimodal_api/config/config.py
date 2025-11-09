from pathlib import Path
import os
from functools import lru_cache
from pydantic import Field
from pydantic_settings import BaseSettings, SettingsConfigDict

from dotenv import load_dotenv

load_dotenv()


class Settings(BaseSettings):
    model_config = SettingsConfigDict(
        env_file="agent-api/.env", extra="ignore", env_file_encoding="utf-8"
    )

    # ------------------------------------------------------------------
    # Models
    # ------------------------------------------------------------------
    GROQ_MODEL: str = "groq"
    ROUTING_MODEL: str = "meta-llama/llama-4-scout-17b-16e-instruct"
    TOOL_SELECTOR_MODEL: str = "meta-llama/llama-4-scout-17b-16e-instruct"
    GENERAL_RESPONSE_MODEL: str = "meta-llama/llama-4-scout-17b-16e-instruct"

    # ------------------------------------------------------------------
    # Summarization node settings
    # ------------------------------------------------------------------
    SUMMARIZER_MODEL: str = "meta-llama/llama-4-scout-17b-16e-instruct"
    MAX_TOKENS_BEFORE_SUMMARY: int = 5000
    MESSAGES_TO_KEEP: int = 10

    # ------------------------------------------------------------------
    # MCP Server Configuration
    # ------------------------------------------------------------------
    # MCP_SERVER: str = "http://localhost:9090/mcp"
    # MCP_TRANSPORT_MECHANISM: str = "streamable_http"
    # MCP_SERVER_NAME: str = "multimodal-mcp"
    MCP_SERVER: str = os.getenv("MCP_SERVER", "http://localhost:9090/mcp")
    MCP_SERVER_NAME: str = os.getenv("MCP_SERVER_NAME", "multimodal-mcp")
    MCP_TRANSPORT_MECHANISM: str = os.getenv(
        "MCP_TRANSPORT_MECHANISM", "streamable_http"
    )

    # ------------------------------------------------------------------
    # Media Files
    # ------------------------------------------------------------------
    PROJECT_ROOT: Path = Path(__file__).resolve().parents[4]
    # SHARED_MEDIA_DIR: str = str(PROJECT_ROOT / "shared_media")
    SHARED_MEDIA_DIR: str = os.getenv(
        "SHARED_MEDIA_DIR", str(PROJECT_ROOT / "shared_media")
    )


@lru_cache(maxsize=1)
def get_settings() -> Settings:
    """
    Get the application settings.

    Returns:
        Settings: The application settings.
    """
    return Settings()
