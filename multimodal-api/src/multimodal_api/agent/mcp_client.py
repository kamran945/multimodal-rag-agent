"""
MCP Client wrapper with retry logic for API calls
"""

from loguru import logger
from langchain_mcp_adapters.client import MultiServerMCPClient

from multimodal_api.config.config import get_settings
from multimodal_api.utils.retry import api_retry

settings = get_settings()
logger = logger.bind(name="MCPClient")


class MCPClientWrapper:
    """
    Wrapper around MultiServerMCPClient with retry logic for API calls
    """

    def __init__(self):
        self._client = None
        self._initialize_client()

    def _initialize_client(self):
        """Initialize the MCP client"""
        try:
            self._client = MultiServerMCPClient(
                {
                    settings.MCP_SERVER_NAME: {
                        "transport": settings.MCP_TRANSPORT_MECHANISM,
                        "url": settings.MCP_SERVER,
                    }
                }
            )
            logger.info(f"MCP Client initialized: {settings.MCP_SERVER}")
        except Exception as e:
            logger.error(f"Failed to initialize MCP client: {e}")
            raise

    @api_retry
    async def get_tools(self):
        """
        Get available tools from MCP server with retry logic.
        Retries on connection/timeout errors.
        """
        if not self._client:
            raise RuntimeError("MCP Client not initialized")

        logger.debug("Fetching tools from MCP server...")
        tools = await self._client.get_tools()
        logger.info(f"Retrieved {len(tools)} tools from MCP server")
        return tools

    @api_retry
    async def get_prompt(self, prompt_name: str, server_name: str):
        """
        Get a prompt from MCP server with retry logic.
        Retries on connection/timeout errors.
        """
        if not self._client:
            raise RuntimeError("MCP Client not initialized")

        logger.debug(f"Fetching prompt '{prompt_name}' from server '{server_name}'...")
        prompt = await self._client.get_prompt(
            prompt_name=prompt_name, server_name=server_name
        )
        logger.debug(f"Retrieved prompt '{prompt_name}'")
        return prompt

    def get_raw_client(self):
        """
        Get the raw MCP client for direct access.
        Use this when you need the client but don't want retry logic.
        """
        return self._client


def get_mcp_client() -> MCPClientWrapper:
    """
    Factory function to get MCP client wrapper.
    This replaces the direct MultiServerMCPClient instantiation.
    """
    return MCPClientWrapper()
