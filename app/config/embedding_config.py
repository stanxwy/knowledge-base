import os
from dataclasses import dataclass


@dataclass(frozen=True) # make it immutable
class EmbeddingConfig:
    bge_m3_path: str
    bge_m3: str
    bge_device: str
    bge_fp16: bool

def load_embedding_config() -> EmbeddingConfig:
    return EmbeddingConfig(
        bge_m3_path=os.getenv("BGE_M3_PATH"),
        bge_m3=os.getenv("BGE_M3", "BAAI/bge-m3"),
        bge_device=os.getenv("BGE_DEVICE", "cuda:0"),
        bge_fp16=os.getenv("BGE_FP16") in ("1", "True", "true", 1)
    )