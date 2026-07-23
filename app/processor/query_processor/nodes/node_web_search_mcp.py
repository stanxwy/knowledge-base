import asyncio
import json

from app.processor.query_processor.base import NodeBase
from app.processor.query_processor.state import QueryGraphState
from app.services.mcp_search_service import get_mcp_search_service, MCPSearchService
from app.utils.json_format_utils import format_json


class NodeWebSearchMcp(NodeBase):

    name: str = "node_web_search_mcp"

    def __init__(self, mcp_search: MCPSearchService = get_mcp_search_service()):
        super().__init__()
        self._mcp_search = mcp_search
    
    def process(self, state: QueryGraphState) -> QueryGraphState:
        query = state.get("rewritten_query", "")
        docs = []
        if query:
            result = asyncio.run(self._mcp_search.search_web(query))
            if result:
                pages = json.loads(result.content[0].text).get("pages") or []
                for page in pages:
                    snippet = (page.get("snippet") or "").strip()
                    url = (page.get("url") or "").strip()
                    title = (page.get("title") or "").strip()
                    if not snippet:
                        continue
                    docs.append({"title": title, "url": url, "snippet": snippet})
                self.logger.info(f"MCP search result: \n{format_json(docs)}")

        if docs:
            return { "web_search_docs": docs }
        return {}