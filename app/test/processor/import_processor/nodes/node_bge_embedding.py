import json
from app.workflows.ingestion.nodes.node_bge_embedding import NodeBGEEmbedding
from app.services.embedding import get_embedding_service
from app.utils.logger import setup_logging

if __name__ == "__main__":
    logger = setup_logging()
    
    json_path = "./test_data/output/B530/chunks.json"
    with open(json_path, "r", encoding="utf-8") as f:
        chunks_json = f.read()

    init_state = {
        "chunks": json.loads(chunks_json),
        "file_title": "B530",
        "output_file_dir": "./test_data/output"
    }
    
    node_bge_embedding = NodeBGEEmbedding(get_embedding_service())
    result = node_bge_embedding(init_state)
    logger.info(result)

"""
(knowledge-base) PS D:\knowledge-base> python -m app.workflows.ingestion.nodes.node_bge_embedding
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