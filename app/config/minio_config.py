import os
from dataclasses import dataclass

@dataclass(frozen=True)
class MinIOConfig:
    endpoint: str
    secure: bool
    access_key: str
    secret_key: str
    bucket_name: str
    img_dir: str

def load_minio_config() -> MinIOConfig:
    return MinIOConfig(
        endpoint=os.getenv("MINIO_ENDPOINT"),
        secure=os.getenv("SECURE") in ("1", "True", "true", 1),
        access_key=os.getenv("MINIO_ACCESS_KEY"),
        secret_key=os.getenv("MINIO_SECRET_KEY"),
        bucket_name=os.getenv("MINIO_BUCKET_NAME"),
        img_dir=os.getenv("MINIO_IMG_DIR", ""),
    )