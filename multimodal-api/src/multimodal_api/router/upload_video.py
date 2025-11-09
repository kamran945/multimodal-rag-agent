"""
Upload Video API - Refactored with centralized utilities
"""

import shutil
import uuid
from pathlib import Path

from fastapi import APIRouter, File, HTTPException, UploadFile
from loguru import logger

from multimodal_api.config.config import get_settings
from multimodal_api.models import VideoUploadResponse

# ✅ New centralized utilities
from multimodal_api.config.constants import (
    MEDIA_DIR_VIDEOS_UPLOADS,
    MSG_NO_FILE_UPLOADED,
    MSG_UPLOAD_SUCCESS,
    HTTP_BAD_REQUEST,
)
from multimodal_api.utils.path_validators import (
    validate_upload_directory,
    get_relative_media_path,
)
from multimodal_api.utils.error_handlers import handle_api_errors, log_endpoint_call

settings = get_settings()
logger = logger.bind(name="UploadVideoAPI")
router_upload_video = APIRouter()


@router_upload_video.post("/upload-video", response_model=VideoUploadResponse)
@log_endpoint_call("upload_video")  # ✅ Automatic logging
@handle_api_errors("video upload")  # ✅ Centralized error handling
async def upload_video(file: UploadFile = File(...)):
    """
    Upload a video and return path + media_id.

    Process:
    1. Generate unique media_id (UUID)
    2. Save file with media_id as filename stem
    3. Return relative path and media_id

    Args:
        file: Uploaded video file

    Returns:
        VideoUploadResponse with success status, message, path, and media_id

    Raises:
        HTTPException: 400 if no file uploaded, 500 if save fails
    """
    # Validate file was provided
    if not file.filename:
        raise HTTPException(status_code=HTTP_BAD_REQUEST, detail=MSG_NO_FILE_UPLOADED)

    # ✅ Generate UUID that becomes both media_id and filename stem
    media_id = str(uuid.uuid4())
    file_ext = Path(file.filename).suffix or ".mp4"
    unique_filename = f"{media_id}{file_ext}"

    # ✅ Validate and create upload directory
    videos_upload_dir = validate_upload_directory(MEDIA_DIR_VIDEOS_UPLOADS)
    video_path = videos_upload_dir / unique_filename

    # Save file
    with open(video_path, "wb") as f:
        shutil.copyfileobj(file.file, f)

    # ✅ Get relative path using utility
    shared_media_dir = Path(settings.SHARED_MEDIA_DIR)
    relative_path = get_relative_media_path(video_path, shared_media_dir)

    logger.info(f"Uploaded video: {relative_path} (media_id: {media_id})")

    return VideoUploadResponse(
        success=True,
        message=MSG_UPLOAD_SUCCESS,
        video_path=str(relative_path.as_posix()),
        media_id=media_id,
    )
