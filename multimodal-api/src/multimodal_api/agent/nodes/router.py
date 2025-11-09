from typing import Literal, List
from loguru import logger

from langgraph.graph import END
from langgraph.types import Command
from langchain_core.messages import AnyMessage, SystemMessage, HumanMessage
from langchain.chat_models import init_chat_model
from langchain_core.runnables import RunnableConfig
from langgraph.runtime import Runtime

from multimodal_api.config.config import get_settings
from multimodal_api.agent.state import VideoAgentState, Context
from multimodal_api.agent.models import RoutingDecision
from multimodal_api.agent.callbacks import usage_callback
from multimodal_api.agent.helper import get_total_tokens_from_metadata
from multimodal_api.agent.mcp_client import MCPClientWrapper


logger = logger.bind(name="RouterNode")

settings = get_settings()


async def routing_node(
    state: VideoAgentState,
    config: RunnableConfig,
    runtime: Runtime[Context],
) -> Command[Literal["tool_selector_node", "general_response_node"]]:
    """Node responsible for routing to tool selection or direct response."""

    last_msg = state["messages"][-1]
    logger.info("Routing node invoked. Last message: {}", last_msg.content[:50])

    # Fetch routing prompt (with automatic retry on network errors)
    mcp_client: MCPClientWrapper = runtime.context["mcp_client"]
    PROMPT: List[HumanMessage] = await mcp_client.get_prompt(
        prompt_name="prompt_routing_system", server_name=settings.MCP_SERVER_NAME
    )
    ROUTING_SYSTEM_PROMPT = PROMPT[-1].content

    # Initialize model with structured output
    llm = init_chat_model(
        model=settings.ROUTING_MODEL,
        model_provider=settings.GROQ_MODEL,
        temperature=0.0,
        callbacks=[usage_callback],
    ).with_structured_output(RoutingDecision)

    # Build messages with memory and summary context
    system_msg = SystemMessage(content=ROUTING_SYSTEM_PROMPT)

    context_messages = [system_msg]

    # Include summary if it exists
    summary = state.get("summary", "")
    if summary:
        context_messages.append(
            SystemMessage(
                content=f"Conversation summary so far:\n{summary}\n\n"
                "Note: Use this summary for context, but focus on the recent messages below."
            )
        )

    messages = [*context_messages, *state["messages"]]

    # Query the model
    result: RoutingDecision = await llm.ainvoke(messages)

    logger.debug("Routing decision: {}", result.model_dump_json())

    # Track tokens
    total_tokens = get_total_tokens_from_metadata(usage_callback.usage_metadata)
    logger.info("Token usage: {}", total_tokens)

    # Determine next node
    next_node = "tool_selector_node" if result.use_tool else "general_response_node"

    logger.success("Routing to: {}", next_node)

    return Command(
        update={
            "use_tool": result.use_tool,
            "total_tokens": total_tokens,
        },
        goto=next_node,
    )
