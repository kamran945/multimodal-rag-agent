from dataclasses import dataclass
from typing import Annotated, Optional, TypedDict, Literal, List
import operator

from langgraph.graph import MessagesState
from langchain_core.messages import AnyMessage
from langchain_mcp_adapters.client import MultiServerMCPClient


# -------------------------------
# Tool result schema
# -------------------------------
class ToolResult(TypedDict):
    """Schema for tool execution results"""

    type: Literal["text", "video"]
    content: str


# -------------------------------
# Graph State Schema
# -------------------------------
class VideoAgentState(MessagesState):
    """Main state schema for the video agent graph"""

    # Input fields
    video_path: Optional[str] = ""
    image_base64: Optional[str] = None
    video_ids: Optional[List[str]] = None  # ✅ NEW: Selected video IDs

    # Routing decisions
    use_tool: bool = False
    is_image_provided: str = ""
    selected_tool: Optional[str] = None

    # Tool execution results
    tool_result: Optional[ToolResult] = None
    output_video_path: Optional[str] = ""

    # Tracking and history
    total_tokens: Annotated[int, operator.add] = 0
    previous_node: str = ""
    summary: str = ""


class VideoAgentInputState(TypedDict):
    """Input schema for agent invocation"""

    messages: List[AnyMessage]
    video_path: Optional[str]
    image_base64: Optional[str]
    video_ids: Optional[List[str]]  # ✅ NEW: Selected video IDs


class VideoAgentOutputState(TypedDict):
    """Output schema returned by the agent"""

    messages: List[AnyMessage]
    output_video_path: Optional[str]


# -------------------------------
# Graph Runtime Context
# -------------------------------
@dataclass
class Context:
    """Runtime context passed to all nodes"""

    mcp_client: MultiServerMCPClient
