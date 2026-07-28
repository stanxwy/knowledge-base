from functools import lru_cache

from app.domain.ports.doc_store import DocumentStore
from app.domain.ports.object_store import ObjectStore
from app.domain.ports.vector_db import ChunksVectorDB, ItemNameVectorDB
from app.factories.services import get_embedder
from app.infra.config.settings import Settings, get_settings
from app.infra.persistence.milvus import (
    ChunksMilvusService,
    ItemNameMilvusService,
)
from app.infra.persistence.minio import MinIOService
from app.infra.persistence.mongo import MongoService


@lru_cache(maxsize=1)
def get_object_store(settings: Settings | None = None) -> ObjectStore:
    settings = settings or get_settings()
    return MinIOService(settings)


@lru_cache(maxsize=1)
def get_item_name_vector_db(settings: Settings | None = None) -> ItemNameVectorDB:
    settings = settings or get_settings()
    return ItemNameMilvusService(settings, get_embedder())


@lru_cache(maxsize=1)
def get_chunks_vector_db(settings: Settings | None = None) -> ChunksVectorDB:
    settings = settings or get_settings()
    return ChunksMilvusService(settings, get_embedder())


@lru_cache(maxsize=1)
def get_doc_store(settings: Settings | None = None) -> DocumentStore:
    settings = settings or get_settings()
    return MongoService(settings)