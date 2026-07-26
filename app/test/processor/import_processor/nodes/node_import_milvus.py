import json
from app.workflows.ingestion.nodes.node_import_milvus import NodeImportMilvus
from app.utils.logger import setup_logging

if __name__ == "__main__":
    setup_logging("DEBUG")

    json_path = "./test_data/output/B530/chunks_with_embeddings.json"
    with open(json_path, "r", encoding="utf-8") as f:
        state_json = f.read()
    chunks = json.loads(state_json)

    init_state = {
        "file_title": "B530",
        "output_file_dir": "./test_data/output",
        "chunks": chunks
    }
    node_import_milvus = NodeImportMilvus()
    node_import_milvus(init_state)

"""
(knowledge-base) D:\knowledge-base>python -m app.test.workflows.ingestion.nodes.node_import_milvus
2026-07-22 20:07:48 - root - INFO - logging initialized: ./logs\knowledge_base.log
2026-07-22 20:07:48 - root - DEBUG - ImportConfig instance not found...
2026-07-22 20:07:48 - root - DEBUG - creating ImportConfig instance...
2026-07-22 20:07:48 - root - DEBUG - ImportConfig instance loaded ImportConfig(max_content_length=2000, img_content_length=200, min_content_length=500, overlap_sentences=1, item_name_chunk_k=3, item_name_chunk_size=2500, image_extensions={'.webp', '.jpeg', '.gif', '.jpg', '.bmp', '.png'}, milvus_url='http://192.168.222.8:19530', chunks_collection='kb_chunks', item_name_collection='kb_item_names', entity_name_collection='', minio_endpoint='192.168.222.8:9000', minio_access_key='minioadmin', minio_secret_key='minioadmin', minio_bucket='knowledge-base', minio_secure=False, embedding_dim=1536, embedding_batch_size=8, requests_per_minute=15)
2026-07-22 20:07:48 - import.node_import_milvus - INFO - --- node_import_milvus started ---
2026-07-22 20:07:49 - app.services.vectordb_service - WARNING - Collection kb_chunks already exists, skip creating...
2026-07-22 20:07:49 - app.services.vectordb_service - DEBUG - Deleted count 14
2026-07-22 20:07:49 - app.services.vectordb_service - INFO - Inserted count 14
2026-07-22 20:07:49 - app.utils.backup_utils - DEBUG - Successfully backed up json: test_data\output\B530\chunks_with_id.json
2026-07-22 20:07:49 - import.node_import_milvus - INFO - --- node_import_milvus done ---
"""