import uuid
import asyncio

from fastapi import APIRouter, HTTPException, Request
from loguru import logger

from multimodal_api.config.config import get_settings
from multimodal_api.models import UserMessageRequest, AIAgentResponse
from multimodal_api.agent.service import ainvoke_agent


settings = get_settings()

logger = logger.bind(name="ChatAPI")

router_chat = APIRouter()


# -----------------------------------------------------
# Non-Streaming Endpoint
# -----------------------------------------------------
@router_chat.post(
    "/chat",
    response_model=AIAgentResponse,
)
async def chat(request: UserMessageRequest, fastapi_request: Request):
    """
    Non-streaming chat endpoint with optional video selection.

    If video_ids are provided, AI will search only in those videos.
    If not provided (or empty), AI searches all videos in Pixeltable.
    """
    agent = fastapi_request.app.state.agent
    mcp_client = fastapi_request.app.state.mcp_client
    thread_id = uuid.uuid4()

    logger.info(f"Chat request - video_ids: {request.video_ids}")

    try:
        if not request.video_path:
            agent_response = await ainvoke_agent(
                agent=agent,
                input={
                    "messages": request.message,
                    "video_path": request.video_path,
                    "image_base64": request.image_base64,
                    "video_ids": request.video_ids,  # Pass video IDs to agent
                },
                context={"mcp_client": mcp_client},
                config={"configurable": {"thread_id": thread_id}},
            )

            return AIAgentResponse(
                success=True,
                message=agent_response.message,
                output_video_path=getattr(agent_response, "output_video_path", "")
                or "",
                media_id=str(
                    uuid.uuid4()
                    if not getattr(agent_response, "output_video_path", "")
                    else ""
                ),
            )

        return AIAgentResponse(
            success=True,
            message="You need to upload the video using the side panel for the processing to start...",
            video_clip_path="",
        )
    except Exception as e:
        logger.exception("Chat invocation failed")
        raise HTTPException(status_code=500, detail=str(e))
