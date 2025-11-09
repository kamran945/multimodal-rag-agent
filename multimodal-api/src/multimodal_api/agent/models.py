from pydantic import BaseModel, Field
from typing import TypedDict, Dict


# -------------------------------
# Structured Output Schema
# -------------------------------
class RoutingDecision(BaseModel):
    """Structured decision on whether a video tool is needed."""

    use_tool: str = Field(
        ..., description="True if a video-related tool should be used"
    )


class ToolSelection(BaseModel):
    """Structured schema for selecting the appropriate tool."""

    tool_name: str = Field(..., description="The exact name of the tool to use.")


# -------------------------------
# UsageMetadataCallbackHandler output
# -------------------------------
class ModelUsage(TypedDict, total=False):
    input_tokens: int
    output_tokens: int
    total_tokens: int


# metadata returned by UsageMetadataCallbackHandler
UsageMetadata = Dict[str, ModelUsage]
