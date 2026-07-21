from functools import lru_cache
from pymilvus.model.hybrid import BGEM3EmbeddingFunction
from typing import Dict, List

from app.config.embedding_config import EmbeddingConfig, load_embedding_config

class EmbeddingService:
    def __init__(self, config: EmbeddingConfig = load_embedding_config()):
        self._config = config
        self._model = None

    def _get_model(self):
        if self._model is None:
            self._model = BGEM3EmbeddingFunction(
                model_name=self._config.bge_m3_path,
                device=self._config.bge_device,
                use_fp16=self._config.bge_fp16
            )
        return self._model

    def generate_embeddings(self, texts: list[str]) -> Dict[str, List]:
        model = self._get_model()
        embeddings = model.encode_documents(texts)
        processed_sparse = []
        for i in range(len(texts)):
            start = embeddings["sparse"].indptr[i]
            end = embeddings["sparse"].indptr[i + 1]
            sparse_indices = embeddings["sparse"].indices[start:end].tolist()
            sparse_data = embeddings["sparse"].data[start:end].tolist()
            sparse_dict = {k: v for k, v in zip(sparse_indices, sparse_data)}
            processed_sparse.append(sparse_dict)
        return {
            "sparse": processed_sparse,
            "dense": [emb.tolist() for emb in embeddings["dense"]]
        }

@lru_cache(maxsize=1)
def get_embedding_service() -> EmbeddingService:
    return EmbeddingService()

if __name__ == '__main__':
    embeddings = get_embedding_service().generate_embeddings(["hello","world"])
    print(embeddings)