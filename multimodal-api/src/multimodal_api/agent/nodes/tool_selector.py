from loguru import logger
from typing import Literal, List

from langgraph.graph import END
from langchain_core.messages import AnyMessage, SystemMessage, HumanMessage
from langchain.chat_models import init_chat_model
from langchain_core.runnables import RunnableConfig
from langgraph.runtime import Runtime
from langgraph.types import Command

from multimodal_api.config.config import get_settings
from multimodal_api.agent.state import VideoAgentState, Context
from multimodal_api.agent.helper import discover_tools, get_total_tokens_from_metadata
from multimodal_api.agent.callbacks import usage_callback
from multimodal_api.agent.mcp_client import MCPClientWrapper

logger = logger.bind(name="ToolSelectorNode")
settings = get_settings()


async def tool_selector_node(
    state: VideoAgentState,
    config: RunnableConfig,
    runtime: Runtime[Context],
) -> Command[Literal["tool_executor_node"]]:
    """Node responsible for selecting which tool to use."""

    last_msg = state["messages"][-1]
    logger.info("Tool selector invoked. Message: {}", last_msg.content[:50])

    # Fetch tool selection prompt (with automatic retry on network errors)
    mcp_client: MCPClientWrapper = runtime.context["mcp_client"]
    PROMPT: List[HumanMessage] = await mcp_client.get_prompt(
        prompt_name="prompt_tool_use_system", server_name=settings.MCP_SERVER_NAME
    )
    TOOL_SELECTOR_PROMPT = PROMPT[-1].content

    # Get available tools (with automatic retry on network errors)
    tools = await mcp_client.get_tools()
    tool_list_str = "\n".join(f"{t.name}: {t.description}" for t in tools)

    # Initialize chat model with tools
    llm = init_chat_model(
        model=settings.TOOL_SELECTOR_MODEL,
        model_provider=settings.GROQ_MODEL,
        temperature=0.0,
        callbacks=[usage_callback],
    ).bind_tools(tools)

    # Prepare system message
    is_image_provided = "YES" if state.get("image_base64") else "NO"
    system_msg = SystemMessage(
        content=(
            TOOL_SELECTOR_PROMPT.format(is_image_provided=is_image_provided)
            + f"\n\n# Available Tools:\n{tool_list_str}"
        )
    )

    # Prepare user content (with image if available)
    if state.get("image_base64"):
        user_content = [
            HumanMessage(
                content=[
                    {"type": "text", "text": last_msg.content},
                    {
                        "type": "image_url",
                        "image_url": {
                            "url": f"data:image/jpeg;base64,{state['image_base64']}"
                        },
                    },
                ],
            )
        ]
    else:
        user_content = [last_msg]

    # Call LLM for tool selection
    messages = [system_msg, *state["messages"][:-1], *user_content]
    result: AnyMessage = await llm.ainvoke(messages)

    # Extract tool information
    tool_calls = result.additional_kwargs.get("tool_calls")
    tool_name = ""
    if tool_calls:
        tool_name = tool_calls[0]["function"]["name"]
        logger.success("Tool selected: {}", tool_name)
    else:
        logger.warning("No tool call in model response")

    # Track tokens
    total_tokens = get_total_tokens_from_metadata(usage_callback.usage_metadata)
    logger.info("Token usage: {}", total_tokens)

    return Command(
        update={
            "messages": user_content + [result],
            "selected_tool": tool_name,
            "total_tokens": total_tokens,
        },
        goto="tool_executor_node",
    )
