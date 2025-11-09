from fastapi import APIRouter, BackgroundTasks, Request
from fastmcp import Client
from pathlib import Path
from loguru import logger

from multimodal_api.config.config import get_settings
from multimodal_api.models import TaskStatus, ProcessVideoRequest, ProcessVideoResponse

settings = get_settings()
logger = logger.bind(name="VideoProcessorAPI")

router_video_processor = APIRouter()


@router_video_processor.post("/process-video", response_model=ProcessVideoResponse)
async def process_video(
    request: ProcessVideoRequest,
    bg_tasks: BackgroundTasks,
    fastapi_request: Request,
):
    """
    Process video using Pixeltable pipeline.
    ✅ Uses media_id from upload as both task_id and video_id
    """
    media_id = request.media_id  # ✅ Single source of truth
    bg_task_states = fastapi_request.app.state.bg_task_states

    logger.info(f"Processing video: {request.video_path} (media_id: {media_id})")
    bg_task_states[media_id] = TaskStatus.PENDING

    video_path = f"{settings.SHARED_MEDIA_DIR}/{request.video_path}"

    async def background_process_video(video_path: str, media_id: str):
        """Background task to process video"""
        try:
            bg_task_states[media_id] = TaskStatus.IN_PROGRESS
            logger.info(f"Starting processing for media_id: {media_id}")

            # Validate file
            if not Path(video_path).exists():
                logger.error(f"Video not found: {video_path}")
                bg_task_states[media_id] = TaskStatus.FAILED
                return

            # Call MCP server with media_id as video_id
            mcp_client = Client(settings.MCP_SERVER)
            async with mcp_client:
                mcp_response = await mcp_client.call_tool(
                    "process_video",
                    {
                        "video_path": video_path,
                        "video_id": media_id,  # ✅ Pass media_id as video_id
                    },
                )

            if mcp_response:
                bg_task_states[media_id] = TaskStatus.COMPLETED
                logger.success(f"Completed processing media_id: {media_id}")
            else:
                bg_task_states[media_id] = TaskStatus.FAILED
                logger.error(f"Failed processing media_id: {media_id}")

        except Exception as e:
            logger.exception(f"Error processing media_id {media_id}: {e}")
            bg_task_states[media_id] = TaskStatus.FAILED

    # Schedule background task
    bg_tasks.add_task(background_process_video, video_path, media_id)

    return ProcessVideoResponse(
        success=True,
        message="Processing started",
        media_id=media_id,
    )
