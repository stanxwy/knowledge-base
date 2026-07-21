import os
from dataclasses import dataclass

@dataclass(frozen=True)
class RerankerConfig:
    text_rerank_api_key: str    
    text_rerank_model: str      
    text_rerank_instruct: str

    bge_rerank_model: str
    bge_rerank_device: str
    bge_rerank_fp16: bool

def load_reranker_config() -> RerankerConfig:
    return RerankerConfig(
        text_rerank_api_key=os.getenv("OPENAI_API_KEY"),
        text_rerank_model=os.getenv("TEXT_RERANK_MODEL"),
        text_rerank_instruct=os.getenv("TEXT_RERANK_INSTRUCT"),

        bge_rerank_model=os.getenv("BGE_RERANKER_LARGE"),
        bge_rerank_device=os.getenv("BGE_RERANKER_DEVICE"),
        bge_rerank_fp16=os.getenv("BGE_RERANKER_FP16") in ("1", "True", "true", 1)
    )