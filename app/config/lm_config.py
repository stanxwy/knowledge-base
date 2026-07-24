import logging
import os
from dataclasses import dataclass, field
from typing import Optional

from dotenv import load_dotenv

load_dotenv()

@dataclass
class LLMConfig:
    base_url: str = field(
        default_factory=lambda: os.getenv("OPENAI_API_BASE", "")
    )
    api_key: str = field(
        default_factory=lambda: os.getenv("OPENAI_API_KEY", "")
    )
    default_model: str = field(
        default_factory=lambda: os.getenv("LLM_DEFAULT_MODEL", "")
    )
    vl_model: str = field(
        default_factory=lambda: os.getenv("VL_MODEL", "")
    )
    item_model: str = field(
        default_factory=lambda: os.getenv("ITEM_MODEL", "")
    )
    llm_temperature: float = field(
        default_factory=lambda: float(os.getenv("LLM_DEFAULT_TEMPERATURE", "0.8"))
    )

    @classmethod
    def from_env(cls) -> "LLMConfig":
        return cls()

# ==================== Glabal Singleton ====================
_lm_config: Optional[LLMConfig] = None

def get_lm_config() -> LLMConfig:
    global _lm_config
    if _lm_config is None:
        _lm_config = LLMConfig.from_env()
    logging.getLogger().debug(f"lm_config loaded {_lm_config}")
    return _lm_config