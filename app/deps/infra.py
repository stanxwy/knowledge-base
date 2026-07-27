from functools import lru_cache

from app.deps.services import get_embedding_service
from app.infra.config.settings import Settings, get_settings
from app.infra.persistence.mongo import MongoService
from app.infra.persistence.object_store import ObjectStoreService
from app.infra.persistence.vectordb import (
    ChunksVectorDBService,
    ItemNameVectorDBService,
)


@lru_cache(maxsize=1)
def get_object_store(settings: Settings | None = None) -> ObjectStoreService:
    settings = settings or get_settings()
    return ObjectStoreService(settings)


@lru_cache(maxsize=1)
def get_item_name_vector_db(settings: Settings | None = None) -> ItemNameVectorDBService:
    settings = settings or get_settings()
    return ItemNameVectorDBService(settings, get_embedding_service())


@lru_cache(maxsize=1)
def get_chunks_vector_db(settings: Settings | None = None) -> ChunksVectorDBService:
    settings = settings or get_settings()
    return ChunksVectorDBService(settings, get_embedding_service())


@lru_cache(maxsize=1)
def get_mongo_service(settings: Settings | None = None) -> MongoService:
    settings = settings or get_settings()
    return MongoService(settings)