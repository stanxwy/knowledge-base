import json
from app.processor.import_processor.nodes.node_item_name_recognition import NodeItemNameRecognition
from app.utils.logger import setup_logging

if __name__ == "__main__":
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