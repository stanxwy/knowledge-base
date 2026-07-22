import os
from dataclasses import dataclass

@dataclass(frozen=True)
class MineruConfig:
    base_url: str
    api_token: str

def load_mineru_config() -> MineruConfig:
    return MineruConfig(
        base_url=os.getenv("MINERU_BASE_URL"),
        api_token=os.getenv("MINERU_API_TOKEN")
    )