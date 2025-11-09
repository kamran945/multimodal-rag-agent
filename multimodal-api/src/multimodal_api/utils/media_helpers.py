"""
Media Helpers - Utility functions for media file operations
"""

from pathlib import Path
from typing import Dict, Optional
from loguru import logger

from multimodal_api.config.constants import (
    VIDEO_EXTENSIONS,
    IMAGE_EXTENSIONS,
    MEDIA_DIR_VIDEOS_UPLOADS,
    MEDIA_DIR_VIDEOS_AI,
    MEDIA_DIR_IMAGES,
)

logger = logger.bind(name="MediaHelpers")


def determine_media_type(file_path: Path) -> str:
    """
    Determine if file is video or image based on extension.

    Args:
        file_path: Path to the media file

    Returns:
        Either "video" or "image"

    Examples:
        >>> determine_media_type(Path("test.mp4"))
        "video"
        >>> determine_media_type(Path("photo.jpg"))
        "image"
    """
    file_extension = file_path.suffix.lower()

    if file_extension in VIDEO_EXTENSIONS:
        return "video"
    elif file_extension in IMAGE_EXTENSIONS:
        return "image"
    else:
        # Default to image for unknown types
        logger.warning(
            f"Unknown file extension: {file_extension}, defaulting to 'image'"
        )
        return "image"


def determine_media_source(path_str: str) -> str:
    """
    Determine if media is from user or AI based on path.

    Args:
        path_str: String representation of the file path

    Returns:
        Either "user" or "ai"

    Examples:
        >>> determine_media_source("videos/uploads/video.mp4")
        "user"
        >>> determine_media_source("videos/ai_responses/clip.mp4")
        "ai"
    """
    # Normalize path separators
    normalized_path = path_str.replace("\\", "/")

    if MEDIA_DIR_VIDEOS_UPLOADS in normalized_path:
        return "user"
    elif MEDIA_DIR_VIDEOS_AI in normalized_path:
        return "ai"
    elif MEDIA_DIR_IMAGES in normalized_path:
        return "user"
    else:
        # Default to user for unknown paths
        return "user"


def get_file_metadata(file_path: Path, base_dir: Path) -> Optional[Dict]:
    """
    Extract comprehensive metadata from a media file.

    Args:
        file_path: Path to the media file
        base_dir: Base directory for calculating relative path

    Returns:
        Dictionary with metadata or None if extraction fails

    Metadata includes:
        - media_id: Unique identifier (filename stem)
        - media_url: Relative path as string
        - media_type: "image" or "video"
        - source: "user" or "ai"
        - createdAt: Unix timestamp in milliseconds
        - processed: Boolean (default True)
        - file_size: Size in bytes
    """
    try:
        # Get file stats
        stats = file_path.stat()

        # Calculate relative path
        relative_path = file_path.relative_to(base_dir)
        path_str = str(relative_path.as_posix())

        # Extract media_id from filename stem
        media_id = file_path.stem

        # Determine type and source
        media_type = determine_media_type(file_path)
        source = determine_media_source(path_str)

        return {
            "media_id": media_id,
            "media_url": path_str,
            "media_type": media_type,
            "source": source,
            "createdAt": int(stats.st_mtime * 1000),
            "processed": True,  # Assume processed by default
            "file_size": stats.st_size,
        }

    except Exception as e:
        logger.error(f"Error extracting metadata for {file_path}: {e}")
        return None


def is_valid_media_file(file_path: Path) -> bool:
    """
    Check if file is a valid media file (image or video).

    Args:
        file_path: Path to check

    Returns:
        True if file is a valid media file, False otherwise
    """
    if not file_path.is_file():
        return False

    file_extension = file_path.suffix.lower()
    return file_extension in (IMAGE_EXTENSIONS | VIDEO_EXTENSIONS)


def format_file_size(size_bytes: int) -> str:
    """
    Format file size in human-readable format.

    Args:
        size_bytes: Size in bytes

    Returns:
        Formatted string (e.g., "1.5 MB", "230 KB")

    Examples:
        >>> format_file_size(1536)
        "1.5 KB"
        >>> format_file_size(1048576)
        "1.0 MB"
    """
    for unit in ["B", "KB", "MB", "GB", "TB"]:
        if size_bytes < 1024.0:
            return f"{size_bytes:.1f} {unit}"
        size_bytes /= 1024.0
    return f"{size_bytes:.1f} PB"
