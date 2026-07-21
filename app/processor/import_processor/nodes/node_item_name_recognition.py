import json
from typing import Tuple, Dict, List

from app.processor.import_processor.base import BaseNode
from app.processor.import_processor.exceptions import StateFieldError
from app.processor.import_processor.state import ImportGraphState
from app.services.embedding_service import EmbeddingService, get_embedding_service
from app.utils.llm_utils import identify_main_product
from app.services.milvus_service import ItemNameVectorDBService, get_item_name_vector_db


class NodeItemNameRecognition(BaseNode):
    """
    主体识别节点：主体识别与标签提取
    """
    name: str = "node_item_name_recognition"

    def __init__(self, 
                 embedding_service: EmbeddingService = get_embedding_service(), 
                 item_name_vector_db: ItemNameVectorDBService = get_item_name_vector_db()):
        super().__init__()
        self._embedding_service = embedding_service
        self._item_name_vector_db = item_name_vector_db

    def _step_1_validate_input_state(self, state: ImportGraphState) -> Tuple[str, List[Dict]]:
        """
        步骤 1: 接收并校验流程输入
        核心作用：
            1. 从流程状态中提取文件标题、文本切片核心数据
            2. 基础数据类型校验，保证下游流程输入有效性
        依赖的状态数据（上游节点产出）：
            - state["file_title"]: 上游提取的文件标题
            - state["chunks"]: 文本切片列表
        返回值：
            Tuple[str, List[Dict]]: (处理后的文件标题, 校验后的文本切片列表)
        """
        # 1、参数校验
        file_title = state.get("file_title")
        if not file_title:
            raise StateFieldError(field_name="file_title", message="文件标题不能为空", expected_type=str)

        chunks = state.get("chunks")
        if not chunks:
            raise StateFieldError(field_name="chunks", message="chunks不能为空", expected_type=list)

        if not isinstance(chunks, list):
            raise StateFieldError(field_name="chunks", message="chunks数据类型不正确", expected_type=list)

        return file_title, chunks

    def _step_2_build_context(self, chunks: List[Dict]) -> str:
        """
        步骤 2: 构造大模型商品名称识别的标准化上下文
        核心作用：
            1. 限制切片数量：仅取前k个切片，避免上下文过长
            2. 限制字符长度：总上下文字符限制，适配大模型输入上限
            3. 格式化内容：带序号的结构化格式，提升大模型识别精度
        参数说明：
            chunks: 文本切片列表
        返回值：
            str: 格式化后的上下文字符串
        """
        chunk_size = self.config.item_name_chunk_size
        parts: List[str] = []
        total_chars = 0
        for idx, chunk in enumerate(chunks[:self.config.item_name_chunk_k], start = 1):

            # 1. 提取前k的切片，避免上下文过长
            chunk_title = chunk.get("title").strip()
            chunk_content = chunk.get("content").strip()

            # 2. 格式化切片
            part = f"【切片{idx}】\n标题{chunk_title}\n内容：{chunk_content}"
            parts.append(part)

            # 3. 计算累计的字符数
            total_chars += len(part)

            # 4. 判断是否需要继续切分
            if total_chars > chunk_size:
                self.logger.warning(f"累计字符数{total_chars}已超过限制{chunk_size}，停止切分")
                break

        # 5. 使用换行符对切分后的片段进行连接
        context = "\n\n".join(parts).strip()

        # 6. 对返回结果进行二次截断
        final_context = context[:chunk_size]
        self.logger.info(f"构造的上下文长度：{len(final_context)}")
        self.logger.info(f"构造的上下文内容：{final_context}")
        return final_context

    def _step_4_update_chunks(self, chunks: List[Dict[str, str]], item_name: str):
        """
        步骤 4: 回填商品名称到流程状态和所有文本切片
        核心作用：
            1. 全局状态更新：将item_name存入state，供下游所有节点直接使用
            2. 切片数据补全：为每个切片添加item_name字段，保证数据一致性
            3. 状态同步：更新state中的chunks，确保切片修改全局生效
        设计思路：
            所有切片关联同一商品名称，保证后续向量入库、检索时的维度一致性
        参数：
            state: 流程状态对象
            chunks: 校验后的文本切片列表
            item_name: 步骤3识别并清洗后的商品名称
        """
        # 1. 遍历所有切片，为每个切片添加商品名字段，保证数据全链路一致
        for chunk in chunks:
            chunk["item_name"] = item_name
        return chunks

    def _step_5_generate_vectors(self, item_name: str) -> Tuple[List, Dict]:
        """
        步骤 5: 为商品名称生成 BGE-M3 稠密 + 稀疏双向量（Milvus 向量检索核心）
        核心说明：
            - 稠密向量（dense_vector）：BGE-M3 固定 1024 维，记录文本深层语义信息
            - 稀疏向量（sparse_vector）：变长键值对，记录文本关键词/特征位置信息
        依赖工具：
            generate_embeddings：封装 BGE-M3 模型，批量生成双向量，兼容单条/批量输入
        参数：
            item_name: 步骤 3 识别的商品名称（非空，空值时直接返回空向量）
        返回值：
            Tuple[List, Dict]: (稠密向量列表，稀疏向量字典)
        """
        # 1. 商品名称为空 → 直接返回空向量
        if not item_name:
            return None, None

        # 2、调用向量生成工具：传入列表支持批量生成，单条数据仍用列表保证格式统一
        vectors = self._embedding_service.generate_embeddings([item_name])
        return vectors["dense"][0], vectors["sparse"][0]

    def _step_6_save_to_vector_db(self, file_title: str, item_name: str, dense_vector, sparse_vector):
        """
        步骤 6: 将商品名称、文件标题、双向量持久化到 Milvus 向量数据库
        核心逻辑：
            1. 客户端获取：获取单例 Milvus 客户端，连接失败则跳过
            2. 集合初始化：无集合则创建（定义 Schema+索引），有集合则直接使用
            3. 幂等性处理：删除同名商品数据，避免重复存储
            4. 数据插入：构造符合 Schema 的数据，非空向量才添加
            5. 集合加载：插入后强制加载集合，确保数据立即可查/Attu 可见
        参数：
            state: 流程状态对象，用于最终状态同步
            file_title: 处理后的文件标题
            item_name: 识别后的商品名称（主键去重依据）
            dense_vector: 步骤 5 生成的稠密向量（1024 维列表）
            sparse_vector: 步骤 5 生成的稀疏向量（字典格式）
        """
        try:
            # 1. 创建集合（如果不存在）
            self._item_name_vector_db.create_item_name_collection()

            # 删除符合条件的数据
            self._item_name_vector_db.delete_from_item_name_collection(file_title)

            # 3. 准备插入Milvus的数据
            data = {
                "file_title": file_title,  # 文件标题
                "item_name": item_name  # 商品名称
            }
            # 稠密向量非空则添加
            if dense_vector is not None:
                data["dense_vector"] = dense_vector
            # 稀疏向量非空则添加
            if sparse_vector is not None:
                data["sparse_vector"] = sparse_vector

            # 4. 插入数据（传入列表支持批量插入，这里仅1条）
            self._item_name_vector_db.insert_into_item_name_collection(data)

        # 捕获所有Milvus操作异常：连接中断、入库失败、索引错误等，不中断主流程
        except Exception as e:
            self.logger.warning(f"数据存入Milvus失败，原因：{str(e)}", exc_info=True)

    def process(self, state: ImportGraphState) -> ImportGraphState:
        """
        LangGraph 核心节点：商品主体名称识别
        流程总览：
            1. 提取输入
            2. 构建大模型上下文
            3. 调用大模型识别商品名称
            4. 回填商品名称到状态和切片
            5. 生成商品名称的稠密/稀疏向量
            6. 将数据存入Milvus向量数据库

        必要参数：task_id、file_title, chunks
        更新参数：item_name

        :param state: 工作流状态对象
        :return: 更新后的状态对象
        """

        # 步骤1：提取并校验输入
        filename, chunks = self._step_1_validate_input_state(state)

        # 步骤2：构建大模型识别的上下文
        context = self._step_2_build_context(chunks)

        # 步骤3：调用大模型识别商品名称
        item_name = identify_main_product(filename, context)

        # 步骤4：回填商品名称到状态和切片
        chunks = self._step_4_update_chunks(chunks, item_name)

        # 步骤5：为商品名称生成稠密/稀疏向量
        dense_vector, sparse_vector = self._step_5_generate_vectors(item_name)

        # 步骤6：将数据存入Milvus向量数据库
        self._step_6_save_to_vector_db(filename, item_name, dense_vector, sparse_vector)

        # 打印识别结果
        self.logger.info(f"--- 识别完成: {item_name} ---")

        self.backup_json(state, chunks, "chunks.json")
        return {
            "chunks": chunks,       # 同步更新state中的切片列表，确保修改全局生效
            "item_name": item_name  # 将商品名称存入全局状态，供下游节点调用
        }


if __name__ == "__main__":
    from app.utils.logger import setup_logging
    logger = setup_logging()

    md_path = r"./test_data/output/B530/chunks.json"
    with open(md_path, "r", encoding="utf-8") as f:
        chunks_json = f.read()
    chunks = json.loads(chunks_json)
    init_state = {
        "chunks": chunks,
        "file_title": "B530",
        "output_file_dir": "./test_data/output"
    }

    node_item_name_recognition = NodeItemNameRecognition()
    result = node_item_name_recognition(init_state)

    logger.info(json.dumps(result, ensure_ascii=False, indent=4))

"""
(knowledge-base) PS D:\knowledge-base> python -m app.processor.import_processor.nodes.node_item_name_recognition
config loaded True...
ImportConfig instance not found...
creating ImportConfig instance...
2026-07-14 13:24:45 - import.node_item_name_recognition - INFO - --- node_item_name_recognition 开始 ---
2026-07-14 13:24:45 - import.node_item_name_recognition - WARNING - 累计字符数2961已超过限制2500，停止切分
2026-07-14 13:24:45 - import.node_item_name_recognition - INFO - 构造的上下文长度：2500
2026-07-14 13:24:46 - httpx - INFO - HTTP Request: POST https://ws-xfsvflr5yndg90oh.cn-beijing.maas.aliyuncs.com/compatible-mode/v1/chat/completions "HTTP/1.1 200 OK"
2026-07-14 13:24:46.422 | INFO     | app.utils.llm_utils:identify_main_product:105 - 商品名称识别结果：HAK 180 烫金机
2026-07-14 13:24:46.423 | INFO     | app.utils.backup_utils:backup_json:25 - 步骤6：json结果备份成功，备份文件路径：test_data\output\hak180\chunks.json
2026-07-14 13:24:47,310 [WARNING][__init__]: Using fp16 with CPU can lead to runtime errors such as 'LayerNormKernelImpl', It's recommended to set 'use_fp16 = False' when using cpu.  (bge_m3.py:50)
Loading weights: 100%|█████████████████████████████████████████████████████████████████████████████████████████████████████████████████████████████████| 391/391 [00:00<00:00, 2222.89it/s]
2026-07-14 13:24:50 - FlagEmbedding.finetune.embedder.encoder_only.m3.runner - INFO - loading existing colbert_linear and sparse_linear---------
2026-07-14 13:24:51.423 | WARNING  | app.utils.milvus_utils:create_item_name_collection:34 - Milvus 集合 kb_item_names 已存在，跳过创建
2026-07-14 13:24:51.777 | DEBUG    | app.utils.milvus_utils:delete_from_item_name_collection:112 - 删除结果
2026-07-14 13:24:51.787 | DEBUG    | app.utils.milvus_utils:insert_into_item_name_collection:107 - 插入结果
2026-07-14 13:24:51 - import.node_item_name_recognition - INFO - --- 识别完成: HAK180烫金机 ---
2026-07-14 13:24:51 - import.node_item_name_recognition - INFO - --- node_item_name_recognition 完成 ---
"""