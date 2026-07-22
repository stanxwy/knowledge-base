from langgraph.constants import END
from langgraph.graph import StateGraph
from langgraph.graph.state import CompiledStateGraph
from typing import Optional

from app.processor.import_processor.nodes.node_bge_embedding import NodeBGEEmbedding
from app.processor.import_processor.nodes.node_document_split import NodeDocumentSplit
from app.processor.import_processor.nodes.node_entry import NodeEntry
from app.processor.import_processor.nodes.node_import_milvus import NodeImportMilvus
from app.processor.import_processor.nodes.node_item_name_recognition import NodeItemNameRecognition
from app.processor.import_processor.nodes.node_md_img import NodeMDImg
from app.processor.import_processor.nodes.node_pdf_to_md import NodePDFToMD
from app.processor.import_processor.state import ImportGraphState


class KBImportWorkflow:

    def __init__(self):
        self.__graph = StateGraph(ImportGraphState)
        self._register_nodes()
        self._setup_routes()
        self.__compiled_graph: Optional[CompiledStateGraph] = None
        
    def _register_nodes(self):
        self.__graph.add_node("node_entry", NodeEntry())
        self.__graph.add_node("node_pdf_to_md", NodePDFToMD())
        self.__graph.add_node("node_md_img", NodeMDImg())
        self.__graph.add_node("node_document_split", NodeDocumentSplit())
        self.__graph.add_node("node_item_name_recognition", NodeItemNameRecognition())
        self.__graph.add_node("node_bge_embedding", NodeBGEEmbedding())
        self.__graph.add_node("node_import_milvus", NodeImportMilvus())

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
        return self.__compiled_graph

    def run(self, state: ImportGraphState, stream: bool = False):
        if stream:
            # return self.graph.stream(state, stream_mode="values")
            return self.graph.stream(state)
        else:
            return self.graph.invoke(state)