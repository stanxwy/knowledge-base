from fastapi import Depends

from app.domain.ports.doc_store import DocumentStore
from app.domain.ports.object_store import ObjectStore
from app.infra.config.settings import Settings, get_settings
from app.infra.persistence.mongo import MongoService
from app.infra.persistence.object_store import MinIOService


def get_settings_dep() -> Settings:
    return get_settings()


def get_doc_store(
    settings: Settings = Depends(get_settings_dep),
) -> DocumentStore:
    return MongoService(settings)


def get_object_store(
    settings: Settings = Depends(get_settings_dep),
) -> ObjectStore:
    return MinIOService(settings)
