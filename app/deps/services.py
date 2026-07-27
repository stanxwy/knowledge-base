from functools import lru_cache

from app.infra.config.settings import Settings, get_settings
from app.services.embedding import EmbeddingService
from app.services.llm import LLMService
from app.services.mcp_search import MCPSearchService
from app.services.mineru import MineruService
from app.services.reranker_http import Reranker


@lru_cache(maxsize=1)
def get_reranker(settings: Settings | None = None) -> Reranker:
    settings = settings or get_settings()
    return Reranker(settings)


@lru_cache(maxsize=1)
def get_llm_service(settings: Settings | None = None) -> LLMService:
    settings = settings or get_settings()
    return LLMService(settings)


@lru_cache(maxsize=1)
def get_mineru_service(settings: Settings | None = None) -> MineruService:
    settings = settings or get_settings()
    return MineruService(settings)


@lru_cache(maxsize=1)
def get_embedding_service(settings: Settings | None = None) -> EmbeddingService:
    settings = settings or get_settings()
    return EmbeddingService(settings)


@lru_cache(maxsize=1)
def get_mcp_search_service(settings: Settings | None = None) -> MCPSearchService:
    settings = settings or get_settings()
    return MCPSearchService(settings)