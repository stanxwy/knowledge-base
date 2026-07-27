from abc import abstractmethod

from FlagEmbedding.inference import FlagReranker


class Reranker:

    @abstractmethod
    def _get_reranker_model(self) -> FlagReranker: ...

    @abstractmethod
    def rerank_documents(self, query: str, documents: list[str]) -> list[float]: ...