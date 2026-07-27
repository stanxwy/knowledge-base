import logging

from langgraph.constants import END
from langgraph.graph import StateGraph
from langgraph.graph.state import CompiledStateGraph

from app.factories.infra import (
    get_chunks_vector_db,
    get_item_name_vector_db,
    get_object_store,
)
from app.factories.services import get_embedder, get_llm_service, get_pdf_parser
from app.workflows.ingestion.nodes.node_bge_embedding import NodeBGEEmbedding
from app.workflows.ingestion.nodes.node_document_split import NodeDocumentSplit
from app.workflows.ingestion.nodes.node_entry import NodeEntry
from app.workflows.ingestion.nodes.node_import_milvus import NodeImportMilvus
from app.workflows.ingestion.nodes.node_item_name_recognition import (
    NodeItemNameRecognition,
)
from app.workflows.ingestion.nodes.node_md_img import NodeMDImg
from app.workflows.ingestion.nodes.node_pdf_to_md import NodePDFToMD
from app.workflows.ingestion.state import ImportGraphState

logger = logging.getLogger(__name__)

class KBImportWorkflow:

    def __init__(self):
        self._graph = StateGraph(ImportGraphState)
        self._register_nodes()
        self._setup_routes()
        self._compiled_graph: CompiledStateGraph | None = None
        
    def _register_nodes(self):
        pdf_parser = get_pdf_parser()
        llm_service = get_llm_service()
        object_store = get_object_store()
        embedding_service = get_embedder()
        item_name_vector_db = get_item_name_vector_db()
        chunks_vector_db = get_chunks_vector_db()

        self._graph.add_node("node_entry", NodeEntry())
        self._graph.add_node("node_pdf_to_md", NodePDFToMD(pdf_parser))
        self._graph.add_node("node_md_img", NodeMDImg(llm_service, object_store))
        self._graph.add_node("node_document_split", NodeDocumentSplit())
        self._graph.add_node("node_item_name_recognition", NodeItemNameRecognition(llm_service, embedding_service, item_name_vector_db))
        self._graph.add_node("node_bge_embedding", NodeBGEEmbedding(embedding_service))
        self._graph.add_node("node_import_milvus", NodeImportMilvus(chunks_vector_db))

    def route_after_entry(self, state: ImportGraphState) -> str:
        if state.get("is_pdf_read_enabled"):
            return "node_pdf_to_md"
        elif state.get("is_md_read_enabled"):
            return "node_md_img"
        else:
            return END
        
    def _setup_routes(self):
        self._graph.set_entry_point("node_entry")
        self._graph.add_conditional_edges(
            "node_entry",
            self.route_after_entry,
            {
                "node_md_img": "node_md_img",
                "node_pdf_to_md": "node_pdf_to_md",
                END: END
            }
        )
        self._graph.add_edge("node_pdf_to_md", "node_md_img")
        self._graph.add_edge("node_md_img", "node_document_split")
        self._graph.add_edge("node_document_split", "node_item_name_recognition")
        self._graph.add_edge("node_item_name_recognition", "node_bge_embedding")
        self._graph.add_edge("node_bge_embedding", "node_import_milvus")
        self._graph.add_edge("node_import_milvus", END)

    @property
    def graph(self):
        if self._compiled_graph is None:
            self._compiled_graph = self._graph.compile()
            logger.info(f"\n{self._compiled_graph.get_graph().draw_ascii()}")
        return self._compiled_graph

    def run(self, state: ImportGraphState, stream: bool = False):
        if stream:
            # return self.graph.stream(state, stream_mode="values")
            return self.graph.stream(state)
        else:
            return self.graph.invoke(state)