from loguru import logger
from typing import Literal, List

from langchain_core.messages import SystemMessage, AIMessage, HumanMessage
from langchain.chat_models import init_chat_model
from langchain_core.runnables import RunnableConfig
from langgraph.runtime import Runtime
from langgraph.types import Command
from langgraph.graph import END

from multimodal_api.config.config import get_settings
from multimodal_api.agent.state import VideoAgentState, Context
from multimodal_api.agent.callbacks import usage_callback
from multimodal_api.agent.helper import get_total_tokens_from_metadata
from multimodal_api.agent.mcp_client import MCPClientWrapper

logger = logger.bind(name="GeneralResponseNode")
settings = get_settings()


async def general_response_node(
    state: VideoAgentState,
    config: RunnableConfig,
    runtime: Runtime[Context],
) -> Command[Literal["__end__"]]:
    """Generates final response to user, integrating tool results."""

    logger.info("General response node invoked")

    # Fetch response prompt (with automatic retry on network errors)
    mcp_client: MCPClientWrapper = runtime.context["mcp_client"]
    PROMPT: List[HumanMessage] = await mcp_client.get_prompt(
        prompt_name="prompt_general_system", server_name=settings.MCP_SERVER_NAME
    )
    GENERAL_SYSTEM_PROMPT = PROMPT[-1].content

    # Initialize model
    llm = init_chat_model(
        model=settings.GENERAL_RESPONSE_MODEL,
        model_provider=settings.GROQ_MODEL,
        temperature=0.3,
        callbacks=[usage_callback],
    )

    # Add context about video output
    context_note = ""
    if state.get("output_video_path"):
        context_note = f"\n\nIMPORTANT: A video clip has been generated and saved."

    system_msg = SystemMessage(content=GENERAL_SYSTEM_PROMPT + context_note)

    context_messages = [system_msg]

    # Include summary if it exists
    summary = state.get("summary", "")
    if summary:
        context_messages.append(
            SystemMessage(
                content=f"Conversation summary so far:\n{summary}\n\n"
                "Note: Use this summary for context when crafting your response, "
                "but prioritize information from recent messages and tool results."
            )
        )

    messages = [*context_messages, *state["messages"]]

    # Generate response
    result: AIMessage = await llm.ainvoke(messages)

    logger.success("Final response generated")

    # Track tokens
    total_tokens = get_total_tokens_from_metadata(usage_callback.usage_metadata)
    logger.info("Token usage: {}", total_tokens)

    return Command(
        update={
            "messages": [result],
            "total_tokens": total_tokens,
        },
        goto=END,
    )
