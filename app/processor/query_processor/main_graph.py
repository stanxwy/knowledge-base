import logging

from langgraph.constants import END
from langgraph.graph import StateGraph
from langgraph.graph.state import CompiledStateGraph

from app.processor.query_processor.nodes.node_answer_output import NodeAnswerOutput
from app.processor.query_processor.nodes.node_item_name_confirm import (
    NodeItemNameConfirm,
)
from app.processor.query_processor.nodes.node_rerank import NodeRerank
from app.processor.query_processor.nodes.node_rrf import NodeRrf
from app.processor.query_processor.nodes.node_search_embedding import (
    NodeSearchEmbedding,
)
from app.processor.query_processor.nodes.node_search_embedding_hyde import (
    NodeSearchEmbeddingHyde,
)
from app.processor.query_processor.nodes.node_web_search_mcp import NodeWebSearchMcp
from app.processor.query_processor.state import QueryGraphState
from app.services.llm_service import get_llm_service
from app.services.mcp_search_service import get_mcp_search_service
from app.services.mongo_service import get_mongo_service
from app.services.reranker_http import get_reranker
from app.services.vectordb_service import get_chunks_vector_db, get_item_name_vector_db

logger = logging.getLogger(__name__)

class KBQueryWorkflow:
    
    def __init__(self):
        self.__graph = StateGraph(QueryGraphState)
        self._init_nodes()
        self._register_nodes()
        self._setup_routes()
        self.__compiled_graph: CompiledStateGraph | None = None

    def _init_nodes(self):
        llm_service = get_llm_service()
        mongo_service = get_mongo_service()
        item_name_vector_db = get_item_name_vector_db()
        chunks_vector_db = get_chunks_vector_db()
        mcp_service = get_mcp_search_service()
        reranker_service = get_reranker()

        self.node_item_name_confirm = NodeItemNameConfirm(mongo_service, llm_service, item_name_vector_db)
        self.node_search_embedding = NodeSearchEmbedding(chunks_vector_db)
        self.node_search_embedding_hyde = NodeSearchEmbeddingHyde(llm_service, chunks_vector_db)
        self.node_web_search_mcp = NodeWebSearchMcp(mcp_service)
        self.node_rrf = NodeRrf()
        self.node_rerank = NodeRerank(reranker_service)
        self.node_answer_output = NodeAnswerOutput(mongo_service, llm_service)

    def _register_nodes(self):
        self.__graph.add_node("node_item_name_confirm", self.node_item_name_confirm)
        self.__graph.add_node("node_search_embedding", self.node_search_embedding)
        self.__graph.add_node("node_search_embedding_hyde", self.node_search_embedding_hyde) 
        self.__graph.add_node("node_web_search_mcp", self.node_web_search_mcp)
        self.__graph.add_node("node_rrf", self.node_rrf)
        self.__graph.add_node("node_rerank", self.node_rerank)
        self.__graph.add_node("node_answer_output", self.node_answer_output)

    def _route_after_item_name_confirm(self, state: QueryGraphState) -> str | list[str]:
        if state.get("answer"):
            return "node_answer_output"
        return ["node_search_embedding", "node_search_embedding_hyde", "node_web_search_mcp"]

    def _setup_routes(self):
        self.__graph.set_entry_point("node_item_name_confirm")
        self.__graph.add_conditional_edges(
            "node_item_name_confirm",
            self._route_after_item_name_confirm,
            {
                "node_answer_output": "node_answer_output",
                "node_search_embedding": "node_search_embedding",
                "node_search_embedding_hyde": "node_search_embedding_hyde",
                "node_web_search_mcp": "node_web_search_mcp"
            }
        )

        self.__graph.add_edge("node_search_embedding", "node_rrf")
        self.__graph.add_edge("node_search_embedding_hyde", "node_rrf")
        self.__graph.add_edge("node_web_search_mcp", "node_rrf")

        self.__graph.add_edge("node_rrf", "node_rerank")
        self.__graph.add_edge("node_rerank", "node_answer_output")
        self.__graph.add_edge("node_answer_output", END)

    @property
    def graph(self):
        if not self.__compiled_graph:
            self.__compiled_graph = self.__graph.compile()
            logger.info(self.__compiled_graph.get_graph().draw_ascii())
        return self.__compiled_graph

    def run(self, initial_state: QueryGraphState, stream: bool = False) -> QueryGraphState:
        if stream:
            return self.graph.stream(initial_state)
        else:
            return self.graph.invoke(initial_state)