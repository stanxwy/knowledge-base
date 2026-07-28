from functools import lru_cache

from app.factories.infra import get_doc_store, get_object_store
from app.factories.workflows import create_ingest_workflow, create_query_workflow
from app.services.ingestion_service import IngestionService
from app.services.query_service import QueryService


@lru_cache
def create_ingest_service() -> IngestionService:
    return IngestionService(
        workflow=create_ingest_workflow(),
        object_store=get_object_store(),
    )

@lru_cache
def create_query_service() -> QueryService:
    return QueryService(
        workflow=create_query_workflow(),
        doc_store=get_doc_store(),
    )