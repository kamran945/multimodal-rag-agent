"""
Path Validation Utilities - Centralized and secure path validation
"""

from pathlib import Path
from fastapi import HTTPException
from loguru import logger

from multimodal_api.config.config import get_settings
from multimodal_api.config.constants import (
    MSG_INVALID_PATH,
    MSG_FILE_NOT_FOUND,
    MSG_ACCESS_DENIED,
    HTTP_FORBIDDEN,
    HTTP_NOT_FOUND,
)

settings = get_settings()
logger = logger.bind(name="PathValidators")


def validate_media_path(
    file_path: str, base_dir: Path = None, check_exists: bool = True
) -> Path:
    """
    Validate and sanitize media file path with security checks.

    Args:
        file_path: Relative or absolute file path to validate
        base_dir: Base directory to validate against (defaults to SHARED_MEDIA_DIR)
        check_exists: Whether to check if file exists (default: True)

    Returns:
        Validated and resolved Path object

    Raises:
        HTTPException: If path is invalid, outside allowed directory, or doesn't exist

    Examples:
        >>> validate_media_path("images/test.jpg")
        PosixPath('/path/to/shared_media/images/test.jpg')

        >>> validate_media_path("../../../etc/passwd")  # Security check
        HTTPException(403, "Access denied")
    """
    if base_dir is None:
        base_dir = Path(settings.SHARED_MEDIA_DIR)

    try:
        # Normalize path - remove leading slashes and backslashes
        safe_relative_path = file_path.lstrip("/\\")

        # Resolve to absolute path
        resolved_path = (base_dir / safe_relative_path).resolve()

        # Security check: ensure path is within base_dir
        # This prevents directory traversal attacks
        if not str(resolved_path).startswith(str(base_dir.resolve())):
            logger.warning(
                f"Security: Attempted access outside base directory. "
                f"Path: {file_path}, Base: {base_dir}"
            )
            raise HTTPException(status_code=HTTP_FORBIDDEN, detail=MSG_ACCESS_DENIED)

        # Check existence if required
        if check_exists and not resolved_path.exists():
            logger.debug(f"File not found: {resolved_path}")
            raise HTTPException(status_code=HTTP_NOT_FOUND, detail=MSG_FILE_NOT_FOUND)

        return resolved_path

    except HTTPException:
        raise  # Re-raise HTTP exceptions as-is
    except Exception as e:
        logger.error(f"Path validation error for '{file_path}': {e}")
        raise HTTPException(status_code=HTTP_FORBIDDEN, detail=MSG_INVALID_PATH)


def validate_upload_directory(directory_path: str) -> Path:
    """
    Validate and create upload directory if it doesn't exist.

    Args:
        directory_path: Relative path to directory within SHARED_MEDIA_DIR

    Returns:
        Validated Path object

    Raises:
        HTTPException: If directory creation fails or path is invalid

    Examples:
        >>> validate_upload_directory("images")
        PosixPath('/path/to/shared_media/images')
    """
    try:
        base_dir = Path(settings.SHARED_MEDIA_DIR)
        target_dir = base_dir / directory_path.lstrip("/\\")
        target_dir = target_dir.resolve()

        # Security check
        if not str(target_dir).startswith(str(base_dir.resolve())):
            raise HTTPException(status_code=HTTP_FORBIDDEN, detail=MSG_ACCESS_DENIED)

        # Create directory if it doesn't exist
        target_dir.mkdir(parents=True, exist_ok=True)

        return target_dir

    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Failed to validate/create directory '{directory_path}': {e}")
        raise HTTPException(
            status_code=500, detail=f"Directory validation failed: {str(e)}"
        )


def get_relative_media_path(full_path: Path, base_dir: Path = None) -> Path:
    """
    Convert absolute path to relative path from SHARED_MEDIA_DIR.

    Args:
        full_path: Absolute path to convert
        base_dir: Base directory (defaults to SHARED_MEDIA_DIR)

    Returns:
        Relative Path object

    Examples:
        >>> get_relative_media_path(Path("/path/to/shared_media/images/test.jpg"))
        PosixPath('images/test.jpg')
    """
    if base_dir is None:
        base_dir = Path(settings.SHARED_MEDIA_DIR)

    try:
        return full_path.relative_to(base_dir)
    except ValueError as e:
        logger.warning(f"Path not relative to base_dir: {full_path}")
        # Fallback: return the path as-is
        return full_path
