import asyncio
import json

from app.infra.external.mcp_search import MCPSearchService
from app.utils.json_format_utils import format_json
from app.workflows.query.base import NodeBase
from app.workflows.query.state import QueryGraphState


class NodeWebSearchMcp(NodeBase):

    name: str = "node_web_search_mcp"

    def __init__(self, mcp: MCPSearchService):
        super().__init__()
        self._mcp = mcp
    
    def process(self, state: QueryGraphState) -> QueryGraphState:
        query = state.get("rewritten_query", "")
        docs = []
        if query:
            result = asyncio.run(self._mcp.search_web(query))
            if result:
                pages = json.loads(result.content[0].text).get("pages") or []
                docs = [{
                    "snippet": (page.get("snippet") or "").strip(),
                    "url": (page.get("url") or "").strip(),
                    "title": (page.get("title") or "").strip()
                } for page in pages if page.get("snippet")]
                self.logger.info(f"MCP search result: \n{format_json(docs)}")

        return { "web_search_docs": docs }