from dotenv import load_dotenv
from app.utils.logger import setup_logging
from app.workflows.ingestion.nodes.node_pdf_to_md import NodePDFToMD

if __name__ == "__main__":
    load_dotenv(override=True)
    setup_logging("DEBUG")
    
    init_state = {
        "pdf_path": "./test_data/kb/B3-211H.pdf",
        "output_file_dir": "./test_data/output"
    }
    node_pdf_to_md = NodePDFToMD()
    node_pdf_to_md(init_state)

"""
(knowledge-base) PS D:\knowledge-base> python -m app.test.workflows.ingestion.nodes.node_pdf_to_md
2026-07-22 11:40:40 - root - INFO - logging initialized: ./logs\knowledge_base.log
2026-07-22 11:40:40 - root - DEBUG - ImportConfig instance not found...
2026-07-22 11:40:40 - root - DEBUG - creating ImportConfig instance...
2026-07-22 11:40:40 - root - DEBUG - ImportConfig instance loaded ImportConfig(max_content_length=2000, img_content_length=200, min_content_length=500, overlap_sentences=1, item_name_chunk_k=3, item_name_chunk_size=2500, image_extensions={'.jpeg', '.bmp', '.png', '.jpg', '.gif', '.webp'}, milvus_url='http://192.168.222.8:19530', chunks_collection='kb_chunks', item_name_collection='kb_item_names', entity_name_collection='', minio_endpoint='192.168.222.8:9000', minio_access_key='minioadmin', minio_secret_key='minioadmin', minio_bucket='knowledge-base', minio_secure=False, embedding_dim=1536, embedding_batch_size=8, requests_per_minute=15)
2026-07-22 11:40:40 - import.node_pdf_to_md - INFO - --- node_pdf_to_md started ---
2026-07-22 11:40:40 - app.services.mineru_service - INFO - get_upload_url start: https://mineru.net/api/v4/file-urls/batch, data: {'files': [{'name': 'B3-211H.pdf'}], 'model_version': 'vlm'}
2026-07-22 11:40:40 - urllib3.connectionpool - DEBUG - Starting new HTTPS connection (1): mineru.net:443
2026-07-22 11:40:41 - urllib3.connectionpool - DEBUG - https://mineru.net:443 "POST /api/v4/file-urls/batch HTTP/1.1" 200 404
2026-07-22 11:40:41 - app.services.mineru_service - INFO - get_upload_url response: {'code': 0, 'msg': 'ok', 'trace_id': 'cbd90f789afe2b6389945cef4f3d9538', 'data': {'batch_id': 'fe9eaabb-6364-4bc1-b2b0-ed138167d816', 'file_urls': ['https://mineru.oss-cn-shanghai.aliyuncs.com/api-upload/extract/2026-07-22/fe9eaabb-6364-4bc1-b2b0-ed138167d816/66393fba-a320-4778-8e72-d88104a2f5f3.pdf?Expires=1784778039&OSSAccessKeyId=LTAI5t8fSGMgiRhQn4mpp926&Signature=UI3TbCNM1Zk52xDrKKRhjbA0rlk%3D']}}
2026-07-22 11:40:41 - app.services.mineru_service - INFO - get_upload_url success, batch_id: fe9eaabb-6364-4bc1-b2b0-ed138167d816, signed_url: https://mineru.oss-cn-shanghai.aliyuncs.com/api-upload/extract/2026-07-22/fe9eaabb-6364-4bc1-b2b0-ed138167d816/66393fba-a320-4778-8e72-d88104a2f5f3.pdf?Expires=1784778039&OSSAccessKeyId=LTAI5t8fSGMgiRhQn4mpp926&Signature=UI3TbCNM1Zk52xDrKKRhjbA0rlk%3D
2026-07-22 11:40:41 - app.services.mineru_service - INFO - start to upload file, signed_url: https://mineru.oss-cn-shanghai.aliyuncs.com/api-upload/extract/2026-07-22/fe9eaabb-6364-4bc1-b2b0-ed138167d816/66393fba-a320-4778-8e72-d88104a2f5f3.pdf?Expires=1784778039&OSSAccessKeyId=LTAI5t8fSGMgiRhQn4mpp926&Signature=UI3TbCNM1Zk52xDrKKRhjbA0rlk%3D
2026-07-22 11:40:41 - urllib3.connectionpool - DEBUG - Starting new HTTPS connection (1): mineru.oss-cn-shanghai.aliyuncs.com:443
2026-07-22 11:40:41 - urllib3.connectionpool - DEBUG - https://mineru.oss-cn-shanghai.aliyuncs.com:443 "PUT /api-upload/extract/2026-07-22/fe9eaabb-6364-4bc1-b2b0-ed138167d816/66393fba-a320-4778-8e72-d88104a2f5f3.pdf?Expires=1784778039&OSSAccessKeyId=LTAI5t8fSGMgiRhQn4mpp926&Signature=UI3TbCNM1Zk52xDrKKRhjbA0rlk%3D HTTP/1.1" 200 0
2026-07-22 11:40:41 - app.services.mineru_service - INFO - upload_doc success
2026-07-22 11:40:41 - app.services.mineru_service - INFO - start to poll task status, max timeout: 60s, poll_url: https://mineru.net/api/v4/extract-results/batch/fe9eaabb-6364-4bc1-b2b0-ed138167d816
2026-07-22 11:40:41 - app.services.mineru_service - INFO - start to poll, url: https://mineru.net/api/v4/extract-results/batch/fe9eaabb-6364-4bc1-b2b0-ed138167d816
2026-07-22 11:40:41 - urllib3.connectionpool - DEBUG - Starting new HTTPS connection (1): mineru.net:443
2026-07-22 11:40:42 - urllib3.connectionpool - DEBUG - https://mineru.net:443 "GET /api/v4/extract-results/batch/fe9eaabb-6364-4bc1-b2b0-ed138167d816 HTTP/1.1" 200 209
2026-07-22 11:40:42 - app.services.mineru_service - INFO - poll_task_status success: {'code': 0, 'msg': 'ok', 'trace_id': '6da7b27968bd97917b3cd1252053d036', 'data': {'batch_id': 'fe9eaabb-6364-4bc1-b2b0-ed138167d816', 'extract_result': [{'file_name': 'B3-211H.pdf', 'state': 'waiting-file', 'err_msg': ''}]}}
2026-07-22 11:40:42 - app.services.mineru_service - INFO - fe9eaabb-6364-4bc1-b2b0-ed138167d816 task status: waiting-file, total time: 0s
2026-07-22 11:40:45 - app.services.mineru_service - INFO - start to poll, url: https://mineru.net/api/v4/extract-results/batch/fe9eaabb-6364-4bc1-b2b0-ed138167d816
2026-07-22 11:40:45 - urllib3.connectionpool - DEBUG - Starting new HTTPS connection (1): mineru.net:443
2026-07-22 11:40:45 - urllib3.connectionpool - DEBUG - https://mineru.net:443 "GET /api/v4/extract-results/batch/fe9eaabb-6364-4bc1-b2b0-ed138167d816 HTTP/1.1" 200 209
2026-07-22 11:40:45 - app.services.mineru_service - INFO - poll_task_status success: {'code': 0, 'msg': 'ok', 'trace_id': '156dd97ca135e72d6f595b590241d316', 'data': {'batch_id': 'fe9eaabb-6364-4bc1-b2b0-ed138167d816', 'extract_result': [{'file_name': 'B3-211H.pdf', 'state': 'waiting-file', 'err_msg': ''}]}}
2026-07-22 11:40:45 - app.services.mineru_service - INFO - fe9eaabb-6364-4bc1-b2b0-ed138167d816 task status: waiting-file, total time: 3s
2026-07-22 11:40:48 - app.services.mineru_service - INFO - start to poll, url: https://mineru.net/api/v4/extract-results/batch/fe9eaabb-6364-4bc1-b2b0-ed138167d816
2026-07-22 11:40:48 - urllib3.connectionpool - DEBUG - Starting new HTTPS connection (1): mineru.net:443
2026-07-22 11:40:49 - urllib3.connectionpool - DEBUG - https://mineru.net:443 "GET /api/v4/extract-results/batch/fe9eaabb-6364-4bc1-b2b0-ed138167d816 HTTP/1.1" 200 309
2026-07-22 11:40:49 - app.services.mineru_service - INFO - poll_task_status success: {'code': 0, 'msg': 'ok', 'trace_id': 'c6fdce666c8dda03ba1212d55c818fe3', 'data': {'batch_id': 'fe9eaabb-6364-4bc1-b2b0-ed138167d816', 'extract_result': [{'file_name': 'B3-211H.pdf', 'state': 'done', 'err_msg': '', 'full_zip_url': 'https://cdn-mineru.openxlab.org.cn/pdf/2026-06-23/1259ea5b-fc6f-456b-ab1d-b118d652f186.zip'}]}}
2026-07-22 11:40:49 - app.services.mineru_service - INFO - fe9eaabb-6364-4bc1-b2b0-ed138167d816 task done, total time: 6s
2026-07-22 11:40:49 - app.services.mineru_service - INFO - fe9eaabb-6364-4bc1-b2b0-ed138167d816 full_zip_url: https://cdn-mineru.openxlab.org.cn/pdf/2026-06-23/1259ea5b-fc6f-456b-ab1d-b118d652f186.zip
2026-07-22 11:40:49 - app.services.mineru_service - INFO - start to download zip, url: https://cdn-mineru.openxlab.org.cn/pdf/2026-06-23/1259ea5b-fc6f-456b-ab1d-b118d652f186.zip
2026-07-22 11:40:49 - urllib3.connectionpool - DEBUG - Starting new HTTPS connection (1): cdn-mineru.openxlab.org.cn:443
2026-07-22 11:40:49 - urllib3.connectionpool - DEBUG - https://cdn-mineru.openxlab.org.cn:443 "GET /pdf/2026-06-23/1259ea5b-fc6f-456b-ab1d-b118d652f186.zip HTTP/1.1" 200 1854621
2026-07-22 11:40:49 - app.services.mineru_service - INFO - download_zip success, save path: test_data\output\B3-211H_result.zip
2026-07-22 11:40:49 - app.services.mineru_service - INFO - removed existing extract dir: test_data\output\B3-211H
2026-07-22 11:40:49 - app.services.mineru_service - INFO - start to unzip test_data\output\B3-211H_result.zip
2026-07-22 11:40:49 - app.services.mineru_service - INFO - unzip success, target dir: test_data\output\B3-211H
2026-07-22 11:40:49 - app.services.mineru_service - INFO - start to rename test_data\output\B3-211H\full.md to B3-211H.md
2026-07-22 11:40:49 - app.services.mineru_service - INFO - rename success B3-211H.md
2026-07-22 11:40:49 - import.node_pdf_to_md - INFO - --- node_pdf_to_md done ---
"""