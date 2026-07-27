from app.services.llm import LLMService
from app.services.vectordb_service import ChunksVectorDBService
from app.workflows.query.base import NodeBase
from app.workflows.query.state import QueryGraphState


class NodeSearchEmbeddingHyde(NodeBase):

    name: str = "node_search_embedding_hyde"

    def __init__(self, 
                 llm_service: LLMService,
                 chunks_vector_db: ChunksVectorDBService):
        super().__init__()
        self._llm_service = llm_service
        self._chunks_vector_db = chunks_vector_db

    def process(self, state: QueryGraphState) -> QueryGraphState:

        rewritten_query = state.get("rewritten_query")
        item_names = state.get("item_names")

        try:
            hyde_doc = self._llm_service.generate_hyde_doc(rewritten_query)

            combined_text = rewritten_query + " " + hyde_doc
            search_results = self._chunks_vector_db.hybrid_search_chunks(combined_text, item_names)

            return {
                "hyde_embedding_chunks": search_results,
                "hyde_doc": hyde_doc,
            }
        except Exception as e:
            self.logger.exception(f"Error in HyDE node: {e}")
            return {}