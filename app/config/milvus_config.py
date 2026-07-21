import os
from dataclasses import dataclass

@dataclass(frozen=True)
class MilvusConfig:
    milvus_url: str
    chunks_collection: str
    item_name_collection: str

def load_milvus_config() -> MilvusConfig:
    return MilvusConfig(
        milvus_url=os.getenv("MILVUS_URL"),
        chunks_collection=os.getenv("CHUNKS_COLLECTION"),
        item_name_collection=os.getenv("ITEM_NAME_COLLECTION")
    )