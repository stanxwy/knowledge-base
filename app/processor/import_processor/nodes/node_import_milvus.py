import json
from typing import Dict, Any, List

from app.processor.import_processor.base import BaseNode
from app.processor.import_processor.exceptions import StateFieldError
from app.processor.import_processor.state import ImportGraphState
from app.services.milvus_service import ChunksVectorDBService, get_chunks_vector_db

class NodeImportMilvus(BaseNode):
    """
    导入向量库节点：数据持久化
    """
    name: str = "node_import_milvus"
    def __init__(self, chunks_vector_db: ChunksVectorDBService = get_chunks_vector_db()):
        super().__init__()
        self._chunks_vector_db = chunks_vector_db

    def _step_1_validate_input_state(self, state: ImportGraphState) -> tuple[List[Dict[str, Any]], int]:

        chunks = state.get("chunks")

        if not chunks:
            raise StateFieldError(field_name="chunks", message="chunks不能为空", expected_type=list)

        if not isinstance(chunks, list):
            raise StateFieldError(field_name="chunks", message="chunks数据类型不正确", expected_type=list)

        first_chunk = chunks[0]
        if 'dense_vector' not in first_chunk:
            raise StateFieldError(field_name="chunks", message="错误: 数据中缺失dense_vector字段")

        if 'sparse_vector' not in first_chunk:
            raise StateFieldError(field_name="chunks", message="错误: 数据中缺失sparse_vector字段")

        vector_dimension = len(first_chunk['dense_vector'])
        return chunks, vector_dimension
    

    def _step_4_insert_data(self, chunks_json_data: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
        """
        步骤4：批量插入切片数据到Milvus+主键回填
        核心逻辑：
            1. 批量插入数据：提升入库效率，减少Milvus连接次数
            2. 回填chunk_id：将Milvus生成的自增主键回填到切片，供下游业务使用
        """
        # 1. 预处理数据：移除手动chunk_id，避免与Milvus自增主键冲突
        data_to_insert = []
        for chunk in chunks_json_data:
            chunk_copy = chunk.copy()
            if "part" not in chunk_copy:
                chunk_copy["part"] = 0
            data_to_insert.append(chunk_copy)

        # 2. 执行批量插入
        insert_result = self._chunks_vector_db.insert_into_chunks_collection(data_to_insert)
     
        # 3. 主键回填：将Milvus生成的chunk_id回填到原始切片
        inserted_ids = insert_result.get('ids', [])
        if inserted_ids:
            for idx, chunk in enumerate(chunks_json_data):
                chunk['chunk_id'] = str(inserted_ids[idx])

        return chunks_json_data

    def process(self, state: ImportGraphState) -> ImportGraphState:
        """
        LangGraph核心节点：Milvus切片数据入库主流程
        执行流程（串行执行，一步一校验，保证数据一致性）：
            1. 输入校验：验证切片有效性、向量字段完整性，提取向量维度
            2. 环境准备：连接Milvus，集合不存在则自动创建Schema+索引
            3. 幂等清理：删除同file_title旧数据，避免重复存储
            4. 批量插入：预处理数据后批量入库，回填Milvus自增chunk_id
            5. 状态更新：将回填了chunk_id的切片更新回全局状态，供下游使用

        异常处理：
            任一步骤失败抛出异常，终止节点执行，保证数据不脏写

        必要参数：chunks
        更新参数：chunks字段回填chunk_id
        """
        # 步骤1：输入数据有效性校验
        chunks_json_data, vector_dimension = self._step_1_validate_input_state(state)

        # 步骤2：Milvus客户端连接+集合准备（自动建表）
        self._chunks_vector_db.create_chunks_collection(vector_dimension)

        # 步骤3：幂等性处理 - 清理同file_title旧数据
        file_title = chunks_json_data[0].get("file_title")
        self._chunks_vector_db.delete_from_chunks_collection(file_title)

        # 步骤4：批量插入数据+主键chunk_id回填
        updated_chunks = self._step_4_insert_data(chunks_json_data)
        self.backup_json(state, updated_chunks, "chunks_with_id.json")

        # 步骤5：更新全局状态，将回填后的切片回传下游
        return {
            "chunks": updated_chunks
        }
    
if __name__ == "__main__":
    json_path = "./test_data/output/B530/chunks_with_embeddings.json"
    with open(json_path, "r", encoding="utf-8") as f:
        state_json = f.read()
    chunks = json.loads(state_json)

    init_state = {
        "chunks": chunks
    }
    node_import_milvus = NodeImportMilvus()
    result = node_import_milvus(init_state)
    print(result)