
from app.processor.query_processor.base import NodeBase
from app.processor.query_processor.state import QueryGraphState

from app.services.vectordb_service import ChunksVectorDBService, get_chunks_vector_db

class NodeSearchEmbedding(NodeBase):

    name: str = "node_search_embedding"

    def __init__(self, chunks_vector_db: ChunksVectorDBService = get_chunks_vector_db()):
        super().__init__()
        self._chunks_vector_db = chunks_vector_db

    def process(self, state: QueryGraphState) -> QueryGraphState:

        query = state.get("rewritten_query")
        item_names = state.get("item_names")

        search_results = self._chunks_vector_db.hybrid_search_chunks(query, item_names)

        return {
            "embedding_chunks": search_results
        }