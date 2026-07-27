
from app.infra.persistence.milvus import ChunksVectorDBService
from app.workflows.query.base import NodeBase
from app.workflows.query.state import QueryGraphState


class NodeSearchEmbedding(NodeBase):

    name: str = "node_search_embedding"

    def __init__(self, chunks_vector_db: ChunksVectorDBService):
        super().__init__()
        self._chunks_vector_db = chunks_vector_db

    def process(self, state: QueryGraphState) -> QueryGraphState:

        query = state.get("rewritten_query")
        item_names = state.get("item_names")

        search_results = self._chunks_vector_db.hybrid_search_chunks(query, item_names)

        return {
            "embedding_chunks": search_results
        }