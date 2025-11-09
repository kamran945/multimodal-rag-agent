"""
Input validation utilities for MCP video tools.

Centralizes all validation logic for better testability and reusability.
"""

import base64
from pathlib import Path
from typing import List, Optional
from loguru import logger

from multimodal_mcp.config import get_settings

logger = logger.bind(name="MCPValidators")
settings = get_settings()


class ValidationError(Exception):
    """Custom exception for validation failures."""

    pass


class VideoPathValidator:
    """Validates video file paths for security and accessibility."""

    @staticmethod
    def validate(video_path: str) -> Path:
        """
        Validate video path exists and is within shared_media directory.

        Args:
            video_path: Path to video file

        Returns:
            Resolved Path object

        Raises:
            ValidationError: If path is invalid
        """
        if not video_path or not video_path.strip():
            raise ValidationError("Video path cannot be empty")

        try:
            path = Path(video_path).resolve()
        except Exception as e:
            raise ValidationError(f"Invalid video path format: {e}")

        # Security: Ensure path is within shared_media
        shared_media = Path(settings.SHARED_MEDIA_DIR).resolve()
        try:
            path.relative_to(shared_media)
        except ValueError:
            raise ValidationError("Video path must be within shared_media directory")

        # Check existence
        if not path.exists():
            raise ValidationError(f"Video file not found: {video_path}")

        if not path.is_file():
            raise ValidationError(f"Path is not a file: {video_path}")

        return path


class UserQueryValidator:
    """Validates user text queries."""

    MAX_QUERY_LENGTH = 2000

    @staticmethod
    def validate(query: str) -> str:
        """
        Validate user query is not empty and within reasonable length.

        Args:
            query: User's search query

        Returns:
            Cleaned query string

        Raises:
            ValidationError: If query is invalid
        """
        if not query or not query.strip():
            raise ValidationError("Query cannot be empty")

        cleaned = query.strip()

        if len(cleaned) > UserQueryValidator.MAX_QUERY_LENGTH:
            raise ValidationError(
                f"Query too long (max {UserQueryValidator.MAX_QUERY_LENGTH} characters)"
            )

        return cleaned


class ImageBase64Validator:
    """Validates base64 encoded images."""

    MAX_SIZE_MB = 10
    MIN_SIZE_BYTES = 100

    @staticmethod
    def validate(image_base64: str) -> str:
        """
        Validate base64 string is valid and reasonable size.

        Args:
            image_base64: Base64 encoded image string

        Returns:
            Validated base64 string

        Raises:
            ValidationError: If base64 is invalid
        """
        if not image_base64 or not image_base64.strip():
            raise ValidationError("Image base64 string cannot be empty")

        cleaned = image_base64.strip()

        # Check encoded size limit
        max_size = ImageBase64Validator.MAX_SIZE_MB * 1024 * 1024
        if len(cleaned) > max_size:
            raise ValidationError(
                f"Image too large (max {ImageBase64Validator.MAX_SIZE_MB}MB)"
            )

        # Verify valid base64 format
        try:
            decoded = base64.b64decode(cleaned)
        except Exception as e:
            raise ValidationError(f"Invalid base64 format: {e}")

        # Check decoded size makes sense
        if len(decoded) < ImageBase64Validator.MIN_SIZE_BYTES:
            raise ValidationError("Image data too small to be valid")

        return cleaned


class VideoNamesValidator:
    """Validates video names list."""

    MAX_VIDEO_COUNT = 20

    @staticmethod
    def validate(video_names: Optional[List[str]]) -> Optional[List[str]]:
        """
        Validate video names list if provided.

        Args:
            video_names: Optional list of video names

        Returns:
            Validated list or None

        Raises:
            ValidationError: If list is invalid
        """
        if video_names is None:
            return None

        if not isinstance(video_names, list):
            raise ValidationError("video_names must be a list")

        if len(video_names) == 0:
            return None

        if len(video_names) > VideoNamesValidator.MAX_VIDEO_COUNT:
            raise ValidationError(
                f"Too many videos specified (max {VideoNamesValidator.MAX_VIDEO_COUNT})"
            )

        # Clean each name
        cleaned = [name.strip() for name in video_names if name and name.strip()]

        return cleaned if cleaned else None


class VideoIdValidator:
    """Validates video IDs."""

    @staticmethod
    def validate(video_id: str) -> str:
        """
        Validate video ID is not empty.

        Args:
            video_id: Video identifier

        Returns:
            Cleaned video ID

        Raises:
            ValidationError: If ID is invalid
        """
        if not video_id or not video_id.strip():
            raise ValidationError("Video ID cannot be empty")

        cleaned = video_id.strip()

        # Optional: Add format validation if video_id follows specific pattern
        # e.g., UUID format check

        return cleaned
