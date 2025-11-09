from typing import Optional, Dict, List
from pydantic import BaseModel
from loguru import logger

from langchain_core.messages import AnyMessage, AIMessage
from fastapi import WebSocket

from multimodal_api.agent.graph import AIAgent
from multimodal_api.agent.state import (
    VideoAgentInputState,
    VideoAgentOutputState,
    Context,
)


logger = logger.bind(name="AgentService")


class AIAgentServiceResponse(BaseModel):
    message: str
    output_video_path: Optional[str] = ""


async def ainvoke_agent(
    agent: AIAgent,
    input: VideoAgentInputState,
    context: Context,
    config: Optional[Dict],
) -> VideoAgentOutputState:
    """Handles a single non-streaming call."""
    try:
        logger.info("Invoking agent...")
        response: VideoAgentOutputState = await agent.ainvoke(
            input=input, config=config, context=context
        )

        message_text = ""

        # Extract the last message (AI Response)
        messages: List[AnyMessage] = response.get("messages")
        last_msg: AnyMessage = messages[-1]
        if isinstance(last_msg, AIMessage):
            message_text = getattr(last_msg, "content", str(last_msg))

        return AIAgentServiceResponse(
            message=message_text,
            output_video_path=response.get("output_video_path", ""),
        )
    except Exception as e:
        logger.exception("Agent invocation failed")
        raise
