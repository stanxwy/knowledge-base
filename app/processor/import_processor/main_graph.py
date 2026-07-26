import logging

from langgraph.constants import END
from langgraph.graph import StateGraph
from langgraph.graph.state import CompiledStateGraph

from app.processor.import_processor.nodes.node_bge_embedding import NodeBGEEmbedding
from app.processor.import_processor.nodes.node_document_split import NodeDocumentSplit
from app.processor.import_processor.nodes.node_entry import NodeEntry
from app.processor.import_processor.nodes.node_import_milvus import NodeImportMilvus
from app.processor.import_processor.nodes.node_item_name_recognition import (
    NodeItemNameRecognition,
)
from app.processor.import_processor.nodes.node_md_img import NodeMDImg
from app.processor.import_processor.nodes.node_pdf_to_md import NodePDFToMD
from app.processor.import_processor.state import ImportGraphState
from app.services.embedding_service import get_embedding_service
from app.services.llm_service import get_llm_service
from app.services.mineru_service import get_mineru_service
from app.services.object_store_service import get_object_store_service
from app.services.vectordb_service import get_chunks_vector_db, get_item_name_vector_db

logger = logging.getLogger(__name__)

class KBImportWorkflow:

    def __init__(self):
        self.__graph = StateGraph(ImportGraphState)
        self._register_nodes()
        self._setup_routes()
        self.__compiled_graph: CompiledStateGraph | None = None
        
    def _register_nodes(self):
        mineru_service = get_mineru_service()
        llm_service = get_llm_service()
        object_store = get_object_store_service()
        embedding_service = get_embedding_service()
        item_name_vector_db = get_item_name_vector_db()
        chunks_vector_db = get_chunks_vector_db()

        self.__graph.add_node("node_entry", NodeEntry())
        self.__graph.add_node("node_pdf_to_md", NodePDFToMD(mineru_service))
        self.__graph.add_node("node_md_img", NodeMDImg(llm_service, object_store))
        self.__graph.add_node("node_document_split", NodeDocumentSplit())
        self.__graph.add_node("node_item_name_recognition", NodeItemNameRecognition(llm_service, embedding_service, item_name_vector_db))
        self.__graph.add_node("node_bge_embedding", NodeBGEEmbedding(embedding_service))
        self.__graph.add_node("node_import_milvus", NodeImportMilvus(chunks_vector_db))

    def route_after_entry(self, state: ImportGraphState) -> str:
        if state.get("is_pdf_read_enabled"):
            return "node_pdf_to_md"
        elif state.get("is_md_read_enabled"):
            return "node_md_img"
        else:
            return END
        
    def _setup_routes(self):
        self.__graph.set_entry_point("node_entry")
        self.__graph.add_conditional_edges(
            "node_entry",
            self.route_after_entry,
            {
                "node_md_img": "node_md_img",
                "node_pdf_to_md": "node_pdf_to_md",
                END: END
            }
        )
        self.__graph.add_edge("node_pdf_to_md", "node_md_img")
        self.__graph.add_edge("node_md_img", "node_document_split")
        self.__graph.add_edge("node_document_split", "node_item_name_recognition")
        self.__graph.add_edge("node_item_name_recognition", "node_bge_embedding")
        self.__graph.add_edge("node_bge_embedding", "node_import_milvus")
        self.__graph.add_edge("node_import_milvus", END)

    @property
    def graph(self):
        if self.__compiled_graph is None:
            self.__compiled_graph = self.__graph.compile()
            logger.info(self.__compiled_graph.get_graph().draw_ascii())
        return self.__compiled_graph

    def run(self, state: ImportGraphState, stream: bool = False):
        if stream:
            # return self.graph.stream(state, stream_mode="values")
            return self.graph.stream(state)
        else:
            return self.graph.invoke(state)