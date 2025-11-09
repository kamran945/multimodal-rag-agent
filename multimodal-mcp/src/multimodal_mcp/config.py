from pathlib import Path
import os
from functools import lru_cache
from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    """
    Configuration for the multimodal MCP system.
    Supports both OpenAI and Groq as model providers.
    """

    model_config = SettingsConfigDict(
        env_file="multimodal-mcp/.env",
        extra="ignore",
        env_file_encoding="utf-8",
    )

    DEFAULT_VIDEO_TABLE_DIR: str = "global_video_table_dir"
    GLOBAL_VIDEO_TABLE_NAME: str = "global_video_table"
    GLOBAL_CAPTION_INDEX: str = "global_caption_embeddings"
    GLOBAL_AUDIO_CHUNKS_VIEW_NAME: str = "global_audio_view_table"
    GLOBAL_FRAME_INDEX_NAME: str = "global_frame_embeddings"
    GLOBAL_FRAME_VIEW_NAME: str = "global_frames_view_table"
    REGISTRY_TABLE_DIR: str = "global_video_registry"
    REGISTRY_TABLE_NAME: str = f"{REGISTRY_TABLE_DIR}.video_registry_table"

    # ------------------------------------------------------------------
    # Model Provider Configuration
    # ------------------------------------------------------------------
    MODEL_PROVIDER: str = "groq"
    EMBEDDING_MODEL_PROVIDER: str = "huggingface"

    # --- OpenAI Models ---
    OPENAI_API_KEY: str | None = None
    OPENAI_TRANSCRIPTION_MODEL: str = "gpt-4o-mini-transcribe"
    OPENAI_IMAGE_CAPTION_MODEL: str = "gpt-4o-mini"
    OPENAI_TEXT_EMBEDDING_MODEL: str = "text-embedding-3-small"
    OPENAI_IMAGE_EMBEDDING_MODEL: str = "openai/clip-vit-base-patch32"

    # --- Groq Models ---
    GROQ_API_KEY: str | None = None
    GROQ_TRANSCRIPTION_MODEL: str = "whisper-large-v3"
    # GROQ_IMAGE_CAPTION_MODEL: str = "meta-llama/llama-4-maverick-17b-128e-instruct"
    GROQ_IMAGE_CAPTION_MODEL: str = "meta-llama/llama-4-scout-17b-16e-instruct"

    # --- HuggingFace Models ---
    HUGGINGFACE_TEXT_EMBEDDING_MODEL: str = "all-MiniLM-L6-v2"
    HUGGINGFACE_IMAGE_EMBEDDING_MODEL: str = "openai/clip-vit-base-patch32"

    # ------------------------------------------------------------------
    # Audio Processing
    # ------------------------------------------------------------------
    AUDIO_CHUNK_DURATION_SEC: int = 10
    AUDIO_OVERLAP_SEC: int = 2
    AUDIO_MIN_CHUNK_DURATION_SEC: int = 1

    # ------------------------------------------------------------------
    # Frame Extraction
    # ------------------------------------------------------------------
    SPLIT_FRAMES_COUNT: int = 45
    NUM_FRAMES: int = 30

    # ------------------------------------------------------------------
    # Image Captioning
    # ------------------------------------------------------------------
    IMAGE_RESIZE_WIDTH: int = 1024
    IMAGE_RESIZE_HEIGHT: int = 768
    IMAGE_CAPTION_PROMPT: str = "Describe the image briefly."
    DELTA_SECONDS_FRAME_INTERVAL: float = 5.0

    # ------------------------------------------------------------------
    # Search Engine
    # ------------------------------------------------------------------
    SPEECH_SIMILARITY_SEARCH_TOP_K: int = 1
    CAPTION_SIMILARITY_SEARCH_TOP_K: int = 1
    IMAGE_SIMILARITY_SEARCH_TOP_K: int = 1

    # ------------------------------------------------------------------
    # MCP Tools
    # ------------------------------------------------------------------
    VIDEO_CLIP_SPEECH_SEARCH_TOP_K: int = 1
    VIDEO_CLIP_CAPTION_SEARCH_TOP_K: int = 1
    VIDEO_CLIP_IMAGE_SEARCH_TOP_K: int = 1
    QUESTION_ANSWER_TOP_K: int = 3

    # ------------------------------------------------------------------
    # Computed Properties
    # ------------------------------------------------------------------
    @property
    def AUDIO_TRANSCRIPTION_MODEL(self) -> str:
        return (
            self.GROQ_TRANSCRIPTION_MODEL
            if self.MODEL_PROVIDER == "groq"
            else self.OPENAI_TRANSCRIPTION_MODEL
        )

    @property
    def TEXT_EMBEDDING_MODEL(self) -> str:
        return (
            self.HUGGINGFACE_TEXT_EMBEDDING_MODEL
            if self.EMBEDDING_MODEL_PROVIDER == "huggingface"
            else self.OPENAI_TEXT_EMBEDDING_MODEL
        )

    @property
    def IMAGE_CAPTION_MODEL(self) -> str:
        return (
            self.GROQ_IMAGE_CAPTION_MODEL
            if self.MODEL_PROVIDER == "groq"
            else self.OPENAI_IMAGE_CAPTION_MODEL
        )

    @property
    def IMAGE_EMBEDDING_MODEL(self) -> str:
        return (
            self.HUGGINGFACE_IMAGE_EMBEDDING_MODEL
            if self.EMBEDDING_MODEL_PROVIDER == "huggingface"
            else self.OPENAI_IMAGE_EMBEDDING_MODEL
        )

    # ------------------------------------------------------------------
    # Shared Directory
    # ------------------------------------------------------------------
    # Get the project root
    PROJECT_ROOT: Path = Path(__file__).resolve().parents[3]
    # SHARED_MEDIA_DIR: str = str(PROJECT_ROOT / "shared_media")
    # SHARED_OUTPUT_VIDEO_DIR: str = str(PROJECT_ROOT / "shared_media")
    SHARED_MEDIA_DIR: str = os.getenv(
        "SHARED_MEDIA_DIR", str(PROJECT_ROOT / "shared_media")
    )
    SHARED_OUTPUT_VIDEO_DIR: str = os.getenv(
        "SHARED_OUTPUT_VIDEO_DIR", str(PROJECT_ROOT / "shared_media")
    )


# ----------------------------------------------------------------------
# Cached Settings Loader
# ----------------------------------------------------------------------
@lru_cache(maxsize=1)
def get_settings() -> Settings:
    """Return a cached settings instance."""
    return Settings()
