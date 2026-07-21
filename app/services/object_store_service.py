import logging
import json
import os

from functools import lru_cache
from minio import Minio
from minio.deleteobjects import DeleteObject

from app.config.minio_config import load_minio_config, MinIOConfig

logger = logging.getLogger(__name__)

class ObjectStoreService:

    def __init__(self, minio_config: MinIOConfig = load_minio_config()):
        self._minio_config = minio_config
        logger.debug(f"MinIO config: {minio_config}")
        self._minio_client = None
        self._base_url = f"http://{minio_config.endpoint}/{minio_config.bucket_name}"
        self._bucket_name = minio_config.bucket_name

    def _get_minio_client(self):
        minio_config = self._minio_config
        if self._minio_client is None:
            try:
                logger.debug("Minio client initializing...")
                minio_client = Minio(
                    endpoint=minio_config.endpoint,
                    access_key=minio_config.access_key,
                    secret_key=minio_config.secret_key,
                    # secure=False 是否启用HTTPS加密连接；False=用HTTP，True=用HTTPS；本地/内网部署一律写False
                    secure=False)

                if not minio_client.bucket_exists(minio_config.bucket_name):
                    minio_client.make_bucket(minio_config.bucket_name)
                
                # 设置存储桶策略为 Public Read (只读权限开放给匿名用户)
                # 这样前端可以直接通过 URL 访问图片，而不需要预签名 URL
                policy = {
                    "Version": "2012-10-17",
                    "Statement": [
                        {
                            "Effect": "Allow",
                            "Principal": {"AWS": ["*"]},
                            "Action": ["s3:GetObject"],
                            "Resource": [f"arn:aws:s3:::{minio_config.bucket_name}/*"]
                        }
                    ]
                }
                minio_client.set_bucket_policy(minio_config.bucket_name, json.dumps(policy))
                logger.debug("MinIO client initialized")
                self._minio_client = minio_client
                return self._minio_client
            except Exception as e:
                logger.error(f"Minio init failed:{e}")
        return None

    def clean_dir(self, dir_path: str) -> None:
        try:
            minio_client = self._get_minio_client()
            objects_to_delete = minio_client.list_objects(
                self._minio_config.bucket_name, 
                prefix=dir_path, 
                recursive=True)
            
            delete_list = [DeleteObject(obj.object_name) for obj in objects_to_delete]
            if delete_list:
                errors = minio_client.remove_objects(self._bucket_name, delete_list)
                for error in errors:
                    logger.error(f"删除失败：{error}")
        except Exception as e:
            logger.error(f"清理minio目录失败：{e}")

    def upload(self, local_path: str, object_name: str, content_type: str = None) -> str | None:
        try:
            # 上传本地文件至MinIO（fput_object：文件流上传，适合大文件）
            self._get_minio_client().fput_object(
                bucket_name=self._bucket_name,
                object_name=object_name,
                file_path=local_path,
                # 关键规则：多后缀文件仅拆分最后一个，如test.tar.gz拆分为("test.tar", ".gz")。
                content_type=content_type or f"image/{os.path.splitext(local_path)[1][1:]}"
            )
            return f"{self._base_url}/{object_name}"
        except Exception as e:
            logger.error(f"图片上传MinIO失败：{local_path}，错误信息：{str(e)}")

    def clean_img_dir(self, doc_stem: str) -> None:
        img_dir = f"{self._minio_config.img_dir}/{doc_stem}"
        self.clean_dir(img_dir)

    def upload_img(self, local_path: str, object_name: str, content_type: str = None) -> str | None:
        self.upload(local_path, f"{self._minio_config.img_dir}/{object_name}", content_type)

@lru_cache(maxsize=1)
def get_object_store_service() -> ObjectStoreService:
    return ObjectStoreService()

if __name__ == "__main__":
    from dotenv import load_dotenv
    from app.utils.logger import setup_logging
    logger = setup_logging("DEBUG")
    load_dotenv()

    local_path = "./docs/images/Docker访问原理图.png"
    object_store = get_object_store_service()
    result = object_store.upload(local_path, f"upload/{os.path.basename(local_path)}")
    logger.info(json.dumps(result, ensure_ascii=False, indent=4))

"""
(knowledge-base) PS D:\knowledge-base> python -m app.utils.minio_utils
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
"""