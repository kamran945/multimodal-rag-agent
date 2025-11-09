"""
Media Files API - Enhanced with task-tracked deletion
"""

from pathlib import Path

from fastapi import APIRouter, Request, BackgroundTasks
from fastmcp import Client
from loguru import logger

from multimodal_api.config.config import get_settings
from multimodal_api.models import (
    MediaFilesListResponse,
    MediaFileResponse,
    DeleteMediaRequest,
    DeleteMediaResponse,
    TaskStatus,
)

# centralized utilities
from multimodal_api.config.constants import (
    ALL_MEDIA_EXTENSIONS,
    MSG_INVALID_PATH,
    MSG_FILE_NOT_FOUND,
    MSG_DELETE_SUCCESS,
    HTTP_FORBIDDEN,
    HTTP_NOT_FOUND,
)
from multimodal_api.utils.path_validators import validate_media_path
from multimodal_api.utils.error_handlers import handle_api_errors, log_endpoint_call
from multimodal_api.utils.media_helpers import get_file_metadata, is_valid_media_file

settings = get_settings()
logger = logger.bind(name="MediaFilesAPI")
router_media_files = APIRouter()


@router_media_files.get("/media-files", response_model=MediaFilesListResponse)
@log_endpoint_call("list_media_files")
@handle_api_errors("media files listing")
async def list_media_files():
    """
    List all media files with metadata.

    Scans the shared_media directory recursively for all image and video files,
    extracts metadata for each file, and returns a sorted list.

    Returns:
        MediaFilesListResponse with list of files and total count
    """
    shared_media_dir = Path(settings.SHARED_MEDIA_DIR)

    # If directory doesn't exist, return empty list
    if not shared_media_dir.exists():
        return MediaFilesListResponse(success=True, files=[], total_count=0)

    files = []

    # ✅ Find all media files using utility function
    for file_path in shared_media_dir.rglob("*"):
        if is_valid_media_file(file_path):
            # ✅ Use centralized metadata extraction
            metadata = get_file_metadata(file_path, shared_media_dir)
            if metadata:
                files.append(MediaFileResponse(**metadata))

    # Sort by creation time (newest first)
    files.sort(key=lambda x: x.createdAt, reverse=True)

    logger.info(f"Found {len(files)} media files")

    return MediaFilesListResponse(success=True, files=files, total_count=len(files))


@router_media_files.delete("/media-file", response_model=DeleteMediaResponse)
@log_endpoint_call("delete_media_file")
@handle_api_errors("media file deletion")
async def delete_media_file(
    request: DeleteMediaRequest,
    bg_tasks: BackgroundTasks,
    fastapi_request: Request,
):
    """
    Delete media file with task tracking (two-phase: Pixeltable + Disk).

    This endpoint returns immediately with a task_id, then performs deletion in background:
    Phase 1: Delete from Pixeltable database (if video was processed)
    Phase 2: Delete file from disk

    Args:
        request: DeleteMediaRequest with media_id and file_path
        bg_tasks: FastAPI background tasks
        fastapi_request: FastAPI request object

    Returns:
        DeleteMediaResponse with success status, message, and task_id

    Raises:
        HTTPException: 403 if invalid path, 404 if file not found
    """
    # ✅ Validate path with security checks
    shared_media_dir = Path(settings.SHARED_MEDIA_DIR)
    file_path = validate_media_path(
        request.file_path, base_dir=shared_media_dir, check_exists=True
    )

    # ✅ Generate task_id for tracking (same as media_id for consistency)
    task_id = request.media_id
    bg_task_states = fastapi_request.app.state.bg_task_states

    # ✅ Initialize task as pending
    bg_task_states[task_id] = TaskStatus.PENDING

    # Check if this is an uploaded video needing Pixeltable cleanup
    videos_upload_dir = shared_media_dir / "videos" / "uploads"
    needs_pixeltable_cleanup = str(file_path.parent).startswith(
        str(videos_upload_dir.resolve())
    )

    async def background_delete_with_phases(
        media_id: str, file_path: Path, cleanup_db: bool
    ):
        """
        Background deletion task with two phases:
        1. Delete from Pixeltable (if needed)
        2. Delete from disk

        Updates task status throughout the process.
        """
        try:
            # ✅ Phase 1: Mark as in progress
            bg_task_states[media_id] = TaskStatus.IN_PROGRESS
            logger.info(f"Starting deletion for media_id: {media_id}")

            # ✅ Phase 2: Delete from Pixeltable if needed
            if cleanup_db:
                try:
                    logger.info(f"Phase 1: Pixeltable cleanup for media_id: {media_id}")
                    mcp_client = Client(settings.MCP_SERVER)
                    async with mcp_client:
                        await mcp_client.call_tool(
                            "delete_video",
                            {"video_id": media_id},
                        )
                    logger.success(
                        f"Phase 1 complete: Pixeltable cleanup for {media_id}"
                    )
                except Exception as db_error:
                    # Log but continue - file might not be in DB yet
                    logger.warning(
                        f"Phase 1 warning: Pixeltable cleanup failed for {media_id}: {db_error}"
                    )

            # ✅ Phase 3: Delete file from disk
            try:
                logger.info(f"Phase 2: Disk deletion for media_id: {media_id}")
                if file_path.exists():
                    file_path.unlink()
                    logger.success(f"Phase 2 complete: Deleted file {file_path}")
                else:
                    logger.warning(
                        f"Phase 2 warning: File already deleted: {file_path}"
                    )
            except Exception as disk_error:
                logger.error(
                    f"Phase 2 error: Disk deletion failed for {media_id}: {disk_error}"
                )
                raise  # This is critical, so we fail the task

            # ✅ Mark as completed - both phases successful
            bg_task_states[media_id] = TaskStatus.COMPLETED
            logger.success(f"Deletion completed for media_id: {media_id}")

        except Exception as e:
            # ✅ Mark as failed if any critical error
            logger.exception(f"Deletion failed for {media_id}: {e}")
            bg_task_states[media_id] = TaskStatus.FAILED

    # ✅ Schedule background deletion
    bg_tasks.add_task(
        background_delete_with_phases,
        request.media_id,
        file_path,
        needs_pixeltable_cleanup,
    )

    logger.info(f"Delete task scheduled: {task_id}")

    # ✅ Return immediately with task_id
    return DeleteMediaResponse(
        success=True,
        message=MSG_DELETE_SUCCESS,
        task_id=task_id,  # ✅ Frontend can track this
    )


@router_media_files.get("/media-files/stats")
@log_endpoint_call("get_media_stats")
@handle_api_errors("media stats retrieval")
async def get_media_stats():
    """
    Get media file statistics.

    Returns aggregate statistics about media files:
    - Total file count
    - Total size in bytes and MB
    - Count by type (images vs videos)

    Returns:
        Dictionary with statistics
    """
    shared_media_dir = Path(settings.SHARED_MEDIA_DIR)

    # If directory doesn't exist, return zeros
    if not shared_media_dir.exists():
        return {
            "success": True,
            "total_files": 0,
            "total_size_bytes": 0,
            "total_size_mb": 0,
            "images": 0,
            "videos": 0,
        }

    total_size = 0
    image_count = 0
    video_count = 0

    # ✅ Count files using utility
    for file_path in shared_media_dir.rglob("*"):
        if is_valid_media_file(file_path):
            total_size += file_path.stat().st_size

            # Determine type using helper
            from multimodal_api.utils.media_helpers import determine_media_type

            if determine_media_type(file_path) == "image":
                image_count += 1
            else:
                video_count += 1

    return {
        "success": True,
        "total_files": image_count + video_count,
        "total_size_bytes": total_size,
        "total_size_mb": round(total_size / (1024 * 1024), 2),
        "images": image_count,
        "videos": video_count,
    }
