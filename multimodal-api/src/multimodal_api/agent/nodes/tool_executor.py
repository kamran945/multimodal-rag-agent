from typing import Literal
import json
from loguru import logger

from langchain_core.messages import AIMessage, ToolMessage
from langgraph.types import Command
from langgraph.runtime import Runtime
from langchain_core.runnables import RunnableConfig
from multimodal_api.agent.mcp_client import MCPClientWrapper

from multimodal_api.agent.state import VideoAgentState, Context, ToolResult

logger = logger.bind(name="ToolExecutorNode")


# =====================================================
# FALLBACK: Generate fallback response
# =====================================================
def generate_fallback_response(
    tool_name: str, error: Exception, tool_id: str
) -> Command[Literal["general_response_node"]]:
    """Generate a helpful fallback response when tool execution fails"""

    fallback_messages = {
        "search_video_captions": (
            "I apologize, but I'm having trouble searching the video captions right now. "
            "This could be due to processing issues or the video hasn't been fully indexed yet. "
            "Please try rephrasing your query or check back in a moment."
        ),
        "get_video_clip_from_text": (
            "I couldn't generate the video clip at this moment. "
            "This might be due to:\n"
            "- The video file being corrupted or in an unsupported format\n"
            "- The timestamp not being available in the video\n"
            "- Temporary processing issues\n\n"
            "Please try with a different query or video."
        ),
        "get_video_clip_from_image": (
            "I'm unable to find matching scenes in the video right now. "
            "This could be because:\n"
            "- The scene doesn't exist in the uploaded video\n"
            "- The image quality is too low for matching\n"
            "- The video hasn't been fully processed yet\n\n"
            "Please try uploading a clearer frame or a different video."
        ),
    }

    fallback_message = fallback_messages.get(
        tool_name,
        f"I encountered an error while processing your request. Please try again or rephrase your query.",
    )

    logger.error(f"Tool '{tool_name}' failed with error: {error}")
    logger.warning(f"Using fallback response for {tool_name}")

    return Command(
        update={
            "tool_result": {
                "type": "text",
                "content": fallback_message,
            },
            "messages": [
                ToolMessage(
                    content=fallback_message,
                    tool_call_id=tool_id,
                )
            ],
        },
        goto="general_response_node",
    )


# =====================================================
# TOOL EXECUTOR NODE - Fail Fast with Fallback
# =====================================================
async def tool_executor_node(
    state: VideoAgentState,
    config: RunnableConfig,
    runtime: Runtime[Context],
) -> Command[Literal["general_response_node"]]:
    """
    Executes the selected MCP tool with immediate fallback on failure.
    NO RETRY - fails fast and returns user-friendly error messages.

    ✅ NEW: Passes video_ids to tools for targeted search
    """

    last_msg = state["messages"][-1]
    logger.info("Tool executor invoked")

    # Validate tool call structure
    tool_calls = last_msg.additional_kwargs.get("tool_calls")
    if not tool_calls:
        logger.warning("No tool calls in last message")
        return Command(
            update={
                "messages": [AIMessage(content="No tool was selected for execution.")]
            },
            goto="general_response_node",
        )

    # Extract tool info
    first_call = tool_calls[0]
    tool_name = first_call["function"]["name"]
    tool_args = first_call["function"]["arguments"]
    tool_id = first_call.get("id", "unknown")

    logger.info(
        "Executing tool: {} with args: {}",
        tool_name,
        tool_args[:100] if len(tool_args) > 100 else tool_args,
    )

    # Fetch tools from MCP client
    mcp_client: MCPClientWrapper = runtime.context["mcp_client"]

    try:
        tools = await mcp_client.get_tools()
    except Exception as e:
        logger.error("Failed to fetch tools from MCP client: {}", e)
        return generate_fallback_response(tool_name, e, tool_id)

    available_tools = {t.name: t for t in tools}

    # Check if tool exists
    if tool_name not in available_tools:
        logger.error("Tool '{}' not found in available tools", tool_name)
        error = ValueError(f"Tool '{tool_name}' not available")
        return generate_fallback_response(tool_name, error, tool_id)

    tool = available_tools[tool_name]

    # Execute tool with fail-fast approach
    try:
        # Parse arguments
        try:
            tool_args = (
                json.loads(tool_args) if isinstance(tool_args, str) else tool_args
            )
        except json.JSONDecodeError as e:
            logger.error("Invalid JSON in tool arguments: {}", e)
            return generate_fallback_response(tool_name, e, tool_id)

        # Add image base64 if needed for image-based search
        if tool_name == "get_video_clip_from_image" and state.get("image_base64"):
            tool_args["image_base64"] = state["image_base64"]

        # ✅ NEW: Add video_ids if provided for targeted search
        if state.get("video_ids") and len(state["video_ids"]) > 0:
            tool_args["video_ids"] = state["video_ids"]
            logger.info(f"Searching in specific videos: {state['video_ids']}")
        else:
            logger.info("No video selection - searching all videos")

        # Execute tool (NO RETRY - fail fast)
        result = await tool.ainvoke(tool_args)

        # Parse result
        result: ToolResult = json.loads(result) if isinstance(result, str) else result

        logger.success("Tool '{}' executed successfully", tool_name)

        # Build update based on result type
        update = {
            "tool_result": result,
            "messages": [
                ToolMessage(
                    content=result["content"],
                    tool_call_id=tool_id,
                )
            ],
        }

        # Add video path if video type
        if result["type"] == "video":
            update["output_video_path"] = result["content"]
            logger.info("Video generated at: {}", result["content"])

        return Command(update=update, goto="general_response_node")

    except json.JSONDecodeError as e:
        logger.error("JSON parsing error in tool result: {}", e)
        return generate_fallback_response(tool_name, e, tool_id)

    except Exception as e:
        # Any error - fail fast with fallback
        logger.error("Tool '{}' execution failed: {}", tool_name, str(e))
        return generate_fallback_response(tool_name, e, tool_id)
