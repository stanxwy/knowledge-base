import os
from dotenv import load_dotenv
from app.utils.logger import setup_logging

load_dotenv(override=True)
if __name__ == "__main__":
    from app.services.object_store_service import get_object_store_service
    logger = setup_logging("DEBUG")

    local_path = "./docs/images/Docker访问原理图.png"
    object_store = get_object_store_service()
    result = object_store.upload(local_path, f"upload/{os.path.basename(local_path)}")
    logger.info(result)

"""
(knowledge-base) PS D:\knowledge-base> python -m app.test.services.object_store_service
bucket knowledge-base True
ObjectWriteResult(
    bucket_name='knowledge-base',
    object_name='upload-images/Docker访问原理图.png',
    version_id=None,
    etag='84207f3dc24963953bc1ffbdff8ef97b',
    http_headers=HTTPHeaderDict({'Accept-Ranges': 'bytes', 'Content-Length': '0', 'ETag': '"84207f3dc24963953bc1ffbdff8ef97b"', 'Server': 'MinIO', 
'Strict-Transport-Security': 'max-age=31536000; includeSubDomains', 'Vary': 'Origin, Accept-Encoding', 'X-Amz-Id-2': 
'dd9025bab4ad464b049177c95eb6ebf374d3b3fd1af9251148b658df7ac2e3e8', 'X-Amz-Request-Id': '18C1C84009B51AF0', 'X-Content-Type-Options': 'nosniff', 
'X-Ratelimit-Limit': '893', 'X-Ratelimit-Remaining': '893', 'X-Xss-Protection': '1; mode=block', 'Date': 'Mon, 13 Jul 2026 07:18:24 GMT'}),
    last_modified=None,
    location=None
)

(knowledge-base) PS D:\knowledge-base> python -m app.test.services.object_store_service
2026-07-23 10:45:26 - root - INFO - logging initialized: ./logs\knowledge_base.log
2026-07-23 10:45:26 - app.services.object_store_service - DEBUG - Minio client initializing...
2026-07-23 10:45:26 - urllib3.connectionpool - DEBUG - Starting new HTTP connection (1): 192.168.222.8:9000
2026-07-23 10:45:26 - urllib3.connectionpool - DEBUG - http://192.168.222.8:9000 "GET /knowledge-base?location= HTTP/1.1" 200 0
2026-07-23 10:45:26 - urllib3.connectionpool - DEBUG - http://192.168.222.8:9000 "HEAD /knowledge-base HTTP/1.1" 200 0
2026-07-23 10:45:26 - urllib3.connectionpool - DEBUG - http://192.168.222.8:9000 "PUT /knowledge-base?policy= HTTP/1.1" 204 0
2026-07-23 10:45:26 - app.services.object_store_service - DEBUG - MinIO client initialized
2026-07-23 10:45:26 - urllib3.connectionpool - DEBUG - http://192.168.222.8:9000 "PUT /knowledge-base/upload/Docker%E8%AE%BF%E9%97%AE%E5%8E%9F%E7%90%86%E5%9B%BE.png HTTP/1.1" 200 0
2026-07-23 10:45:26 - root - INFO - "http://192.168.222.8:9000/knowledge-base/upload/Docker访问原理图.png"
"""