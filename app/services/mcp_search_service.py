import logging
from functools import lru_cache

from agents.mcp import MCPServerStreamableHttp

from app.config.mcp_config import DashScopeMcpConfig, load_dashscope_mcp_config

_MCP_TIME_OUT = 10
_MCP_MAX_RETRY_ATTEMPTS = 3
_MCP_QUERY_RESULT_COUNT = 5

logger = logging.getLogger(__name__)

class MCPSearchService:
    def __init__(self, mcp_config: DashScopeMcpConfig = load_dashscope_mcp_config()):
        self._mcp_config = mcp_config
        self._mcp_client = None

    def get_mcp_client(self):
        if not self._mcp_client:
            self._mcp_client = MCPServerStreamableHttp(
                name="search_mcp",
                params={
                    "url": self._mcp_config.mcp_base_url,
                    "headers": {"Authorization": f"Bearer {self._mcp_config.api_key}"},
                    "timeout": _MCP_TIME_OUT,
                },
                cache_tools_list=True,
                max_retry_attempts=_MCP_MAX_RETRY_ATTEMPTS,
            )
        return self._mcp_client

    async def search_web(self, query):
        client = self.get_mcp_client()
        try:
            await client.connect()
            result = await client.call_tool(
                tool_name="bailian_web_search",
                arguments={"query": query, "count": _MCP_QUERY_RESULT_COUNT},
            )
            logger.info(f"MCP web search result: \n{result}")
            return result
        finally:
            await client.cleanup()

@lru_cache(maxsize=1)
def get_mcp_search_service() -> MCPSearchService:
    return MCPSearchService()