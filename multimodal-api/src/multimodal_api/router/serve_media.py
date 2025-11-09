"""
Serve Media API - Refactored with centralized utilities
"""

from fastapi import APIRouter
from fastapi.responses import FileResponse
from loguru import logger

# ✅ New centralized utilities
from multimodal_api.utils.path_validators import validate_media_path
from multimodal_api.utils.error_handlers import handle_api_errors, log_endpoint_call

logger = logger.bind(name="ServeMediaAPI")
router_serve_media = APIRouter()


@router_serve_media.get("/media/{file_path:path}")
@log_endpoint_call("serve_media")  # ✅ Automatic logging
@handle_api_errors("media serving")  # ✅ Centralized error handling
async def serve_media(file_path: str):
    """
    Serve media files safely from the shared_media directory.

    This endpoint:
    - Validates the file path for security
    - Checks file exists
    - Returns the file as a response

    Args:
        file_path: Relative path to media file within shared_media directory

    Returns:
        FileResponse with the requested media file

    Raises:
        HTTPException: 403 if path is invalid, 404 if file not found
    """
    # ✅ Centralized validation with security checks
    media_file = validate_media_path(file_path, check_exists=True)

    # Return file response
    return FileResponse(str(media_file))
