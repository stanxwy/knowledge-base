from pymilvus.model.hybrid import BGEM3EmbeddingFunction

from app.config.embedding_config import embedding_config
from app.processor.import_processor.base import setup_logging

setup_logging()
_bge_m3_ef = None

def get_bge_m3_ef():
    """
    单例对象
    :return:
    """
    global _bge_m3_ef
    if _bge_m3_ef is not None:
        return _bge_m3_ef

    _bge_m3_ef = BGEM3EmbeddingFunction(
        model_name=embedding_config.bge_m3_path,
        device=embedding_config.bge_device,
        use_fp16=embedding_config.bge_fp16
    )
    return _bge_m3_ef

def generate_embeddings(texts: list[str]):
    """
    生成向量
    :param texts:
    :return:
    """
    model = get_bge_m3_ef()
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