from typing_extensions import Literal, TypedDict


class ToolResult(TypedDict):
    type: Literal["text", "video"]
    content: str
