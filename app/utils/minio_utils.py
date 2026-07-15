import logging
import json
import os

from minio import Minio
from minio.deleteobjects import DeleteObject
from rich import print as rprint
from app.config.minio_config import minio_config

try:
    # 1) 初始化MinIO客户端
    logging.getLogger().debug("开始初始化MinIO客户端")
    minio_client = Minio(
        endpoint=minio_config.endpoint,
        access_key=minio_config.access_key,
        secret_key=minio_config.secret_key,
        # secure=False 是否启用HTTPS加密连接；False=用HTTP，True=用HTTPS；本地/内网部署一律写False
        secure=False)

    # 2) 创建存储桶
    if not minio_client.bucket_exists(minio_config.bucket_name):
        minio_client.make_bucket(minio_config.bucket_name)
    
    # 3) 设置存储桶策略
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
    logging.getLogger().debug("MinIO客户端初始化完成")
except Exception as e:
    logging.getLogger().error(f"Minio init failed:{e}")
    minio_client = None

def get_minio_client():
    return minio_client

def clean_dir(dir_path: str) -> None:
    """
    :param prefix: MinIO目录前缀（要清理的目录路径）
    """
    try:
        objects_to_delete = minio_client.list_objects(minio_config.bucket_name, prefix=dir_path, recursive=True)
        # 构造删除列表
        delete_list = [DeleteObject(obj.object_name) for obj in objects_to_delete]
        if delete_list:
            errors = minio_client.remove_objects(minio_config.bucket_name, delete_list)
            for error in errors:
                logging.getLogger().error(f"删除失败：{error}")
    except Exception as e:
        logging.getLogger().error(f"清理minio目录失败：{e}")

def upload(local_path: str, object_name: str) -> str | None:
    """
    将单张本地图片上传至MinIO对象存储，并返回公网可访问URL
    :param local_path: 图片本地完整路径
    :param object_name: MinIO中要存储的对象名称
    :return: 图片MinIO访问URL（上传失败返回None）
    """
    try:
        # 上传本地文件至MinIO（fput_object：文件流上传，适合大文件）
        minio_client.fput_object(
            bucket_name=minio_config.bucket_name,  # MinIO存储桶名（从配置读取）
            object_name=object_name,  # MinIO对象名称
            file_path=local_path,  # 本地文件路径
            # 关键规则：多后缀文件仅拆分最后一个，如test.tar.gz拆分为("test.tar", ".gz")。
            content_type=f"image/{os.path.splitext(local_path)[1][1:]}"
        )

        # 构造MinIO基础访问URL
        base_url = f"http://{minio_config.endpoint}/{minio_config.bucket_name}"
        return f"{base_url}/{object_name}"

    except Exception as e:
        logging.getLogger().error(f"图片上传MinIO失败：{local_path}，错误信息：{str(e)}")

if __name__ == "__main__":
    minio_client = get_minio_client()
    print(f"bucket {minio_config.bucket_name}", minio_client.bucket_exists(minio_config.bucket_name))

    local_path = "./docs/images/Docker访问原理图.png"
    result =minio_client.fput_object(
        bucket_name=minio_config.bucket_name,  # MinIO存储桶名（从配置读取）
        object_name=f"{minio_config.img_dir}/{os.path.basename(local_path)}",  # MinIO对象名称
        file_path=local_path,  # 本地文件路径
        # 关键规则：多后缀文件仅拆分最后一个，如test.tar.gz拆分为("test.tar", ".gz")。
        content_type=f"image/{os.path.splitext(local_path)[1][1:]}"
    )
    rprint(result)

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