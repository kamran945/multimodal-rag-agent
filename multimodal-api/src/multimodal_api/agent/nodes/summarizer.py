from typing import Literal
from loguru import logger

from langchain.messages import RemoveMessage
from langgraph.types import Command
from langchain_core.messages import AIMessage, HumanMessage
from langchain.chat_models import init_chat_model
from langchain_core.runnables import RunnableConfig
from langgraph.runtime import Runtime

from multimodal_api.config.config import get_settings
from multimodal_api.agent.state import VideoAgentState, Context

logger = logger.bind(name="SummarizerNode")
settings = get_settings()


# =====================================================
# SUMMARIZATION PROMPT
# =====================================================
SUMMARIZER_PROMPT_TEMPLATE = """
You are a conversation summarizer. Create a concise summary of the conversation history.

{instruction}

Focus on:
- Key topics discussed
- User requests and outcomes
- Video-related queries and results
- Important context for future interactions

Keep it under 300 words.
"""

EXTEND_INSTRUCTION = "This is a summary of the conversation to date: {summary}\n\nExtend the summary by taking into account the new messages above:"
CREATE_INSTRUCTION = "Create a summary of the conversation above:"


# =====================================================
# SUMMARIZER NODE
# =====================================================
async def summarization_node(
    state: VideoAgentState,
    config: RunnableConfig,
    runtime: Runtime[Context],
) -> Command[Literal["routing_node"]]:
    """
    Node responsible for summarization of state messages.

    Includes error handling and safe token counting.
    """

    logger.info("Summarization node invoked. Message count: {}", len(state["messages"]))

    summary = state.get("summary", "")
    total_tokens = state.get("total_tokens", 0)

    # -------------------------------------------------------------------------
    # Early exit if token threshold not reached
    # -------------------------------------------------------------------------
    if total_tokens <= settings.MAX_TOKENS_BEFORE_SUMMARY:
        logger.info(
            "Token threshold not reached ({}/{}). Skipping summarization.",
            total_tokens,
            settings.MAX_TOKENS_BEFORE_SUMMARY,
        )
        return Command(goto="routing_node")

    logger.info("Token threshold exceeded. Initiating summarization...")

    # -------------------------------------------------------------------------
    # Prepare summarization prompt
    # -------------------------------------------------------------------------
    try:
        instruction = (
            EXTEND_INSTRUCTION.format(summary=summary)
            if summary
            else CREATE_INSTRUCTION
        )

        summary_prompt = SUMMARIZER_PROMPT_TEMPLATE.format(instruction=instruction)
        summary_message = HumanMessage(content=summary_prompt)

    except Exception as e:
        logger.error(f"Failed to prepare summarization prompt: {e}")
        # Continue without summarization
        return Command(goto="routing_node")

    # -------------------------------------------------------------------------
    # Initialize LLM with error handling
    # -------------------------------------------------------------------------
    try:
        llm = init_chat_model(
            model=settings.SUMMARIZER_MODEL,
            model_provider=settings.GROQ_MODEL,
            temperature=0.0,
        )
    except Exception as e:
        logger.error(f"Failed to initialize LLM for summarization: {e}")
        return Command(goto="routing_node")

    # -------------------------------------------------------------------------
    # Generate summary with retry logic
    # -------------------------------------------------------------------------
    messages = state["messages"] + [summary_message]
    response = await llm.ainvoke(messages)
    logger.success("Summarization complete.")

    # -------------------------------------------------------------------------
    # Remove old messages if needed
    # -------------------------------------------------------------------------
    remaining_messages = []

    try:
        if len(state["messages"]) > settings.MESSAGES_TO_KEEP:
            num_to_remove = len(state["messages"]) - settings.MESSAGES_TO_KEEP
            logger.info(f"Removing {num_to_remove} old messages")

            remaining_messages = [
                RemoveMessage(id=m.id)
                for m in state["messages"][:num_to_remove]
                if hasattr(m, "id") and m.id  # Safety check
            ]
    except Exception as e:
        logger.warning(f"Failed to prepare message removal: {e}")
        # Continue anyway, just don't remove messages

    # -------------------------------------------------------------------------
    # Return update with new summary
    # -------------------------------------------------------------------------
    update_dict = {"messages": remaining_messages}

    # Only update summary if we got a response
    if response and hasattr(response, "content"):
        update_dict["summary"] = response.content
        logger.info(f"New summary length: {len(response.content)} chars")
    else:
        logger.warning("No valid response from LLM, keeping old summary")

    return Command(
        update=update_dict,
        goto="routing_node",
    )
