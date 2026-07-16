import json
from typing import List, Dict

from app.processor.import_processor.base import BaseNode
from app.processor.import_processor.exceptions import StateFieldError
from app.processor.import_processor.state import ImportGraphState
from app.utils.embedding_utils import generate_embeddings

class NodeBGEEmbedding(BaseNode):
    """
    混合向量化节点：使用 BGE-M3 模型将文本转换为向量
    """
    name: str = "node_bge_embedding"

    def _step_1_validate_input(self, state: ImportGraphState) -> List[Dict]:
        """
        步骤 1：输入数据有效性校验
        核心作用：
            1. 从全局状态提取待向量化的chunks切片列表
            2. 严格校验chunks类型和非空性，无有效数据则终止向量化
        参数：
            state: ImportGraphState - 流程全局状态对象
        返回：
            List[Dict] - 校验通过的文本切片列表
        异常：
            若chunks非列表/为空，抛出ValueError，终止当前向量化流程
        """

        chunks = state.get("chunks")

        if not chunks:
            raise StateFieldError(field_name="chunks", message="chunks不能为空", expected_type=list)

        if not isinstance(chunks, list):
            raise StateFieldError(field_name="chunks", message="chunks数据类型不正确", expected_type=list)

        return chunks

    def _step_2_generate_embeddings(self, chunks: List[Dict[str, str]]) -> List[Dict[str, str]]:
        """
        步骤 2: 批量生成向量（核心业务逻辑）
        核心逻辑：
            1. 分批处理：避免一次性处理过多数据导致显存溢出（OOM）。
            2. 文本构造：将 item_name 和 content 拼接，增强语义（商品名作为核心特征前置）。
            3. 向量生成：调用模型批量生成 Dense（稠密）和 Sparse（稀疏）向量。
        参数：
            chunks: List[Dict] 待向量化的文本切片列表
        返回：
            List[Dict]: 包含向量字段（dense_vector/sparse_vector）的文本切片列表
        """

        # 初始化空列表，存储最终带向量的文本切片
        output_data = []
        # 设置批次大小（每批处理5条，可根据显存/性能调整：显存大则调大，反之调小）
        batch_size = 5  # 设置批次大小，可以根据显存大小进行调整！

        # 按批次遍历文本切片：range(起始, 终止, 步长) → 0,5,10... 分批处理
        for i in range(0, len(chunks), batch_size):
            batch_texts = chunks[i:i + batch_size]
            input_texts = []
            for doc in batch_texts:
                item_name = doc["item_name"]
                content = doc["content"]
                input_texts.append(f"{item_name}\n{content}" if item_name else content)

            docs_embeddings = generate_embeddings(input_texts)
            for j, doc in enumerate(batch_texts):
                item = doc.copy() # 防御式编程：函数不修改入参，是最优默认策略
                item["dense_vector"] = docs_embeddings["dense"][j]
                item["sparse_vector"] = docs_embeddings["sparse"][j]
                output_data.append(item)

            self.logger.info(f"成功获取第 {i + 1}-{min(i + len(batch_texts), len(chunks))} 项的嵌入。")

        # 返回带向量的文本切片列表（供后续存入Milvus）
        return output_data

    def process(self, state: ImportGraphState) -> ImportGraphState:
        """
        LangGraph核心节点：BGE-M3文本向量化处理
        流程总览：
            1. 输入校验：验证chunks有效性，核心数据缺失则终止当前节点
            2. 批量向量化：分批拼接文本、生成双向量，为切片绑定向量字段
            3. 状态更新：将带向量的chunks更新回全局状态，供下游Milvus入库节点使用

        必要参数：chunks
        更新参数：chunks字段新增dense_vector/sparse_vector

        :param state: 工作流状态对象
        :return: 更新后的状态对象
        """

        # 步骤1：输入数据校验
        chunks = self._step_1_validate_input(state)

        # 步骤2：批量生成双向量，为切片绑定向量字段
        output_data = self._step_2_generate_embeddings(chunks)

        # 步骤3：更新全局状态，将带向量的chunks回传下游
        self.backup_json(state, output_data, "chunks_with_embeddings.json")
        return {
            "chunks": output_data
        }

if __name__ == "__main__":
    from app.utils.logger import setup_logging
    setup_logging()

    json_path = "./test_data/output/B530/chunks.json"
    with open(json_path, "r", encoding="utf-8") as f:
        chunks_json = f.read()

    init_state = {
        "chunks": json.loads(chunks_json),
        "file_title": "B530",
        "output_file_dir": "./test_data/output"
    }
    node_bge_embedding = NodeBGEEmbedding()
    result = node_bge_embedding(init_state)

"""
(knowledge-base) PS D:\knowledge-base> python -m app.processor.import_processor.nodes.node_bge_embedding
config loaded True...
ImportConfig instance not found...
creating ImportConfig instance...
2026-07-14 14:54:54 - import.node_bge_embedding - INFO - --- node_bge_embedding 开始 ---
2026-07-14 14:54:55,527 [WARNING][__init__]: Using fp16 with CPU can lead to runtime errors such as 'LayerNormKernelImpl', It's recommended to set 'use_fp16 = False' when using cpu.  (bge_m3.py:50)
Loading weights: 100%|█████████████████████████████████████████████████████████████████████████████████████████████████████████████████████████████████| 391/391 [00:00<00:00, 1921.33it/s]
2026-07-14 14:54:59 - FlagEmbedding.finetune.embedder.encoder_only.m3.runner - INFO - loading existing colbert_linear and sparse_linear---------
2026-07-14 14:55:27 - import.node_bge_embedding - INFO - 成功获取第 1-5 项的嵌入。
2026-07-14 14:55:38 - import.node_bge_embedding - INFO - 成功获取第 6-6 项的嵌入。
2026-07-14 14:55:38.270 | INFO     | app.utils.backup_utils:backup_json:25 - 步骤6：json结果备份成功，备份文件路径：test_data\output\hak180\chunks_with_embeddings.json
2026-07-14 14:55:38 - import.node_bge_embedding - INFO - --- node_bge_embedding 完成 ---
2026-07-14 14:55:38 - root - INFO - {
    "chunks": [
        {
            "title": "",
            "content": "![](images/677a08ee041965bbbdb6b483d6c17d5aaa36a26b6dc96870a2019f0307b8616f.jpg)  \nD01WD7001-00\n\nSCHN\n\n\n## HAK 180 烫金机\n\n产品安全手册（简体中文）\n\n感谢您购买 HAK 180 烫金机。\n\n在使用本设备之前，请先阅读本手册，包括所有预防措施。阅读本手册后，请妥善保管。\n\n有关使用本设备的更多信息，请参阅使用说明书，其可在兄弟 (中国)商业有限公司技术服务支持网站 http://www.95105369.com/Web/Manuals.aspx 上找到。建议您先通读使用说明书，再使用本设备。\n\n如需获得常见问题解答、故障排除和说明书，请访问\n\nhttp://www.95105369.com。\n\n对于本设备所有者不遵守本指南中规定的说明操作而导致的损害，Brother 不承担任何责任。\n\n•\t对于保养、调整或维修事宜，请联系 Brother 呼叫中心或您当地的Brother 经销商。\n\n•\t如果本设备工作不正常或发生任何错误，请关闭本设备，拔下所有电缆，然后联系 Brother 呼叫中心或您当地的 Brother 经销商。\n\n•\t本文档中提供的信息可能会随时更改，恕不另行通知。\n\n•\t严禁未经授权擅自复制或重制本文档的任何部分或全部内容。\n\n•\t请注意，对于使用通过本设备制作的产品造成的任何损坏或利润损失，或者故障、维修导致的数据消失或更改，或者第三方提出的任何索赔，我们不承担任何责任。\n",
            "file_title": "hak180",
            "parent_title": "",
            "item_name": "HAK180烫金机",
            "dense_vector": [
                -0.003924362827092409,
                -0.0020521613769233227,
                -0.10509362816810608,
                ...
"""