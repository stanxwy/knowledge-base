import os
from dataclasses import dataclass, field

@dataclass
class EmbeddingConfig:
    bge_m3_path: str = field(
        default_factory=lambda: os.getenv("BGE_M3_PATH")
    )
    bge_m3: str = field(
        default_factory=lambda: os.getenv("BGE_M3")
    ) 
    bge_device: str = field(
        default_factory=lambda: os.getenv("BGE_DEVICE")
    )
    bge_fp16: bool = field(
        # 特殊处理：将.env中的1/0转为布尔值，兼容常见的数字/字符串格式
        default_factory=lambda: os.getenv("BGE_FP16") in ("1", "True", "true", 1)
    )

    @classmethod
    def from_env(cls) -> "EmbeddingConfig":
        return cls()

__config = None
def config() -> EmbeddingConfig:
    global __config
    if __config is None:
        __config = EmbeddingConfig.from_env()
    return __config