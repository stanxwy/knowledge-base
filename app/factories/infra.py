from functools import lru_cache

from app.domain.ports.doc_store import DocumentStore
from app.domain.ports.object_store import ObjectStore
from app.factories.services import get_embedder
from app.infra.config.settings import Settings, get_settings
from app.infra.persistence.mongo import MongoService
from app.infra.persistence.object_store import MinIOService
from app.infra.persistence.vectordb import (
    ChunksVectorDBService,
    ItemNameVectorDBService,
)


@lru_cache(maxsize=1)
def get_object_store(settings: Settings | None = None) -> ObjectStore:
    settings = settings or get_settings()
    return MinIOService(settings)


@lru_cache(maxsize=1)
def get_item_name_vector_db(settings: Settings | None = None) -> ItemNameVectorDBService:
    settings = settings or get_settings()
    return ItemNameVectorDBService(settings, get_embedder())


@lru_cache(maxsize=1)
def get_chunks_vector_db(settings: Settings | None = None) -> ChunksVectorDBService:
    settings = settings or get_settings()
    return ChunksVectorDBService(settings, get_embedder())


@lru_cache(maxsize=1)
def get_doc_store(settings: Settings | None = None) -> DocumentStore:
    settings = settings or get_settings()
    return MongoService(settings)