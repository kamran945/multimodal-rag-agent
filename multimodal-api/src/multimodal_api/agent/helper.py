from loguru import logger
from fastmcp import Client

from multimodal_api.config.config import get_settings
from multimodal_api.agent.models import UsageMetadata


logger = logger.bind(name="DiscoverTools")

settings = get_settings()


async def discover_tools(mcp_client: Client) -> list:
    """
    Discover and register available tools from the MCP server.

    This method connects to the MCP server and retrieves the list of available tools.
    Each tool contains metadata like name, description, and parameters.

    Returns:
        list: A list of Tool objects containing the discovered tools and their metadata

    Raises:
        ConnectionError: If unable to connect to the MCP server
        Exception: If tool discovery fails for any other reason
    """
    try:
        # async with mcp_client as client:
        tools = await mcp_client.list_tools()
        if not tools:
            logger.info("No tools were discovered from the MCP server")
            return []

        logger.info(f"Discovered {len(tools)} tools:")
        for tool in tools:
            logger.info(f"- {tool.name}: {tool.description}")

        return tools

    except ConnectionError as e:
        logger.error(f"Failed to connect to MCP server: {e}")
        raise
    except Exception as e:
        logger.error(f"Tool discovery failed: {e}")
        raise


def get_total_tokens_from_metadata(metadata: UsageMetadata) -> int:
    """
    Safely sum total token usage from UsageMetadataCallbackHandler metadata.
    """
    if not metadata:
        return 0

    total_tokens = 0
    for model_name, usage in metadata.items():
        if not isinstance(usage, dict):
            continue
        total_tokens += usage.get("total_tokens") or (
            usage.get("input_tokens", 0) + usage.get("output_tokens", 0)
        )

    return total_tokens
