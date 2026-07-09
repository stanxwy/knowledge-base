import json

from langgraph.constants import END
from langgraph.graph import StateGraph

from app.processor.import_processor.base import setup_logging
from app.processor.import_processor.nodes.node_bge_embedding import NodeBGEEmbedding
from app.processor.import_processor.nodes.node_document_split import NodeDocumentSplit
from app.processor.import_processor.nodes.node_entry import NodeEntry
from app.processor.import_processor.nodes.node_import_milvus import NodeImportMilvus
from app.processor.import_processor.nodes.node_item_name_recognition import NodeItemNameRecognition
from app.processor.import_processor.nodes.node_md_img import NodeMDImg
from app.processor.import_processor.nodes.node_pdf_to_md import NodePDFToMD
from app.processor.import_processor.state import ImportGraphState

class KBImportWorkflow:
    """知识库导入工作流"""

    def __init__(self, config=None):
        """
        初始化工作流
        """
        self.__compiled_graph = None

    @property
    def graph(self):
        """
        懒加载：只在第一次使用时编译图
        这个写法是“延迟初始化 + 缓存”的范式，核心目的是把“编译图”这个高成本操作推迟到必须执行时才做。
        这不仅提升了对象实例化的速度，也避免了无效的资源浪费，是 LangGraph 项目中的最佳实践。
        """
        if self.__compiled_graph is None:
            self.__compiled_graph = self.build_graph()
        return self.__compiled_graph

    @staticmethod
    def route_after_entry(state: ImportGraphState) -> str:
        """
        入口节点后的条件路由函数
        :param state: 当前状态
        :return: 下一个节点名称
        """
        if state.get("is_pdf_read_enabled"):
            return "node_pdf_to_md"
        elif state.get("is_md_read_enabled"):
            return "node_md_img"
        else:
            return END

    def build_graph(self):
        """
        创建图结构
        :return: 编译后的图
        """
        # 1. 初始化LangGraph状态图
        graph = StateGraph(ImportGraphState)

        # 2. 注册节点到工作流
        graph.add_node("node_entry", NodeEntry())
        graph.add_node("node_pdf_to_md", NodePDFToMD())
        graph.add_node("node_md_img", NodeMDImg())
        graph.add_node("node_document_split", NodeDocumentSplit())
        graph.add_node("node_item_name_recognition", NodeItemNameRecognition())
        graph.add_node("node_bge_embedding", NodeBGEEmbedding())
        graph.add_node("node_import_milvus", NodeImportMilvus())

        # 3. 设置入口节点
        graph.set_entry_point("node_entry")

        # 4. 注册条件边
        graph.add_conditional_edges(
            "node_entry",
            self.route_after_entry,
            {
                #key：路由函数的返回值，value:节点的名字
                "node_md_img": "node_md_img",
                "node_pdf_to_md": "node_pdf_to_md",
                END: END
            }
        )

        # 5. 注册顺序边
        graph.add_edge("node_pdf_to_md", "node_md_img")
        graph.add_edge("node_md_img", "node_document_split")
        graph.add_edge("node_document_split", "node_item_name_recognition")
        graph.add_edge("node_item_name_recognition", "node_bge_embedding")
        graph.add_edge("node_bge_embedding", "node_import_milvus")
        graph.add_edge("node_import_milvus", END)

        # 6. 编译工作流
        return graph.compile()

    def run(self, state: ImportGraphState, stream: bool = False):
        """
        统一执行入口，支持切换invoke/stream
        :param state: 初始状态
        :param stream: 是否流式输出
        :return: 执行结果
        """
        if stream:
            return self.graph.stream(state, stream_mode="values")
        else:
            return self.graph.invoke(state)


if __name__ == "__main__":
    
    #启用日志
    setup_logging()
    
    # 定义初始状态
    init_state = {"import_file_path": r"../../docs/readme.md"}
    workflow = KBImportWorkflow()
    
    # 方式1：实例化后使用（推荐方式，可复用）
    print("=== 方式1：流式执行 ===")
    for event in workflow.run(init_state, stream=True):
        print(f"state: {event}")

    # 方式2：非流式执行
    print("\n=== 方式2：非流式执行 ===")
    final_state = workflow.run(init_state, stream=False)
    print(json.dumps(final_state, ensure_ascii=False, indent=4))
    
    # 打印编译后的图结构
    # workflow.graph.get_graph().print_ascii()