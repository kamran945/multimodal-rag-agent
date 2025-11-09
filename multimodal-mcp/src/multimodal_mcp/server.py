from typing import Dict, List, Optional
import click
from fastmcp import FastMCP

from multimodal_mcp.tools import (
    ask_question_about_video,
    get_video_clip_from_image,
    get_video_clip_from_user_query,
    process_video,
    delete_video,
)
from multimodal_mcp.models import ToolResult

from multimodal_mcp.prompts import (
    ROUTING_SYSTEM_PROMPT,
    TOOL_USE_SYSTEM_PROMPT,
    GENERAL_SYSTEM_PROMPT,
)

import multimodal_mcp.video.ingestion.registry as registry


def add_mcp_tools(mcp: FastMCP):
    @mcp.tool(
        name="process_video",
        description=(
            "Use this tool to ingest and preprocess a video before any analysis, "
            "search, or question answering. It prepares frames, audio, and embeddings "
            "so other tools can work on the video efficiently."
        ),
        tags={"video", "prepare", "ingest", "preprocess"},
    )
    def tool_process_video(video_path: str, video_id: str) -> bool:
        return process_video(video_path=video_path, video_id=video_id)

    @mcp.tool(
        name="delete_video",
        description=(
            "Use this tool to delete a video and all its associated data (frames, audio, embeddings, etc.) "
            "from the system. Use this when a video is outdated or needs to be removed from search and analysis."
        ),
        tags={"video", "delete", "cleanup", "remove"},
    )
    def tool_delete_video(video_id: str) -> bool:
        return delete_video(video_id=video_id)

    @mcp.tool(
        name="get_video_clip_from_user_query",
        description=(
            "Use this tool to extract the most relevant video clip based on a natural-language "
            "query or question. Ideal when the user asks to 'find where...' or 'show the part where...'."
        ),
        tags={"video", "clip", "query", "search"},
    )
    def tool_get_video_clip_from_user_query(
        user_query: str, video_ids: Optional[List[str]] = None
    ) -> ToolResult:
        return get_video_clip_from_user_query(
            user_query=user_query, video_ids=video_ids
        )

    @mcp.tool(
        name="get_video_clip_from_image",
        description=(
            "Use this tool when the user provides an image or visual reference and wants "
            "to find matching or similar scenes within a video."
        ),
        tags={"video", "clip", "image", "visual-match"},
    )
    def tool_get_video_clip_from_image(
        image_base64: str, video_ids: Optional[List[str]] = None
    ) -> ToolResult:
        return get_video_clip_from_image(image_base64=image_base64, video_ids=video_ids)

    @mcp.tool(
        name="ask_question_about_video",
        description=(
            "Use this tool when the user asks a factual or descriptive question about "
            "a video's content — for example, 'What happens after...', 'Who is speaking...', "
            "or 'Describe this scene'."
        ),
        tags={"video", "question", "qa", "understanding"},
    )
    def tool_ask_question_about_video(
        user_query: str, video_ids: Optional[List[str]] = None
    ) -> ToolResult:
        return ask_question_about_video(user_query=user_query, video_ids=video_ids)


def add_mcp_prompts(mcp: FastMCP):
    @mcp.prompt
    def prompt_routing_system() -> str:
        return ROUTING_SYSTEM_PROMPT

    @mcp.prompt
    def prompt_tool_use_system() -> str:
        return TOOL_USE_SYSTEM_PROMPT

    @mcp.prompt
    def prompt_general_system() -> str:
        return GENERAL_SYSTEM_PROMPT


def add_mcp_resources(mcp: FastMCP):
    @mcp.resource("data://registry")
    def resource_list_registry_entries() -> List[Dict]:
        return registry.list_registry_entries()

    @mcp.resource("data://table_{video_name}")
    def resource_get_video_details_by_name(video_name: str) -> Dict:
        return registry.get_video_details_by_name(video_name=video_name)


mcp = FastMCP("VideoProcessor")

add_mcp_tools(mcp)
add_mcp_prompts(mcp)
add_mcp_resources(mcp)


@click.command()
@click.option("--port", default=9090, help="FastMCP server port")
@click.option("--host", default="0.0.0.0", help="FastMCP server host")
@click.option(
    "--transport", default="streamable-http", help="MCP Transport protocol type"
)
def run_mcp_server(port, host, transport):
    """
    Run the FastMCP server with the specified port, host, and transport protocol.
    """
    mcp.run(host=host, port=port, transport=transport)


if __name__ == "__main__":
    run_mcp_server()
