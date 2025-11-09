"""
Upload Image API - Refactored with centralized utilities
"""

import shutil
import uuid
from pathlib import Path

from fastapi import APIRouter, File, HTTPException, UploadFile
from loguru import logger

from multimodal_api.config.config import get_settings
from multimodal_api.models import ImageUploadResponse

# ✅ New centralized utilities
from multimodal_api.config.constants import (
    MEDIA_DIR_IMAGES,
    MSG_NO_FILE_UPLOADED,
    MSG_IMAGE_UPLOADED,
    HTTP_BAD_REQUEST,
)
from multimodal_api.utils.path_validators import (
    validate_upload_directory,
    get_relative_media_path,
)
from multimodal_api.utils.error_handlers import handle_api_errors, log_endpoint_call

settings = get_settings()
logger = logger.bind(name="UploadImageAPI")
router_upload_image = APIRouter()


@router_upload_image.post("/upload-image", response_model=ImageUploadResponse)
@log_endpoint_call("upload_image")  # ✅ Automatic logging
@handle_api_errors("image upload")  # ✅ Centralized error handling
async def upload_image(file: UploadFile = File(...)):
    """
    Upload an image and return path + media_id.

    Process:
    1. Generate unique media_id (UUID)
    2. Save file with media_id as filename stem
    3. Return relative path and media_id

    Args:
        file: Uploaded image file

    Returns:
        ImageUploadResponse with success status, message, path, and media_id

    Raises:
        HTTPException: 400 if no file uploaded, 500 if save fails
    """
    # Validate file was provided
    if not file.filename:
        raise HTTPException(status_code=HTTP_BAD_REQUEST, detail=MSG_NO_FILE_UPLOADED)

    # ✅ Generate UUID that becomes both media_id and filename stem
    media_id = str(uuid.uuid4())
    file_ext = Path(file.filename).suffix or ".jpg"
    unique_filename = f"{media_id}{file_ext}"

    # ✅ Validate and create upload directory
    images_dir = validate_upload_directory(MEDIA_DIR_IMAGES)
    image_path = images_dir / unique_filename

    # Save file
    with open(image_path, "wb") as f:
        shutil.copyfileobj(file.file, f)

    # ✅ Get relative path using utility
    shared_media_dir = Path(settings.SHARED_MEDIA_DIR)
    relative_path = get_relative_media_path(image_path, shared_media_dir)

    logger.info(f"Uploaded image: {relative_path} (media_id: {media_id})")

    return ImageUploadResponse(
        success=True,
        message=MSG_IMAGE_UPLOADED,
        image_path=str(relative_path.as_posix()),
        media_id=media_id,
    )
