import json
import logging
import dashscope

from functools import lru_cache
from app.config.reranker_config import load_reranker_config, RerankerConfig

logger = logging.getLogger(__name__)

class Reranker:

    def __init__(self, reranker_config: RerankerConfig = load_reranker_config()):
        self._reranker_config = reranker_config

    def rerank_documents(self, query: str, documents: list[str]) -> list[float]:
        config = self._reranker_config
        dashscope.api_key = config.text_rerank_api_key
        response = dashscope.TextReRank.call(
            model = config.text_rerank_model,
            query = query,
            documents = documents,
            top_n = len(documents),
            return_documents = False,
            instruct=config.text_rerank_instruct,
        )
        logger.info(f"DashScope rerank response: \n{json.dumps(response, ensure_ascii=False, indent=2)}")

        status_code = response.get("status_code")
        if status_code != 200:
            message = response.get("message")
            raise RuntimeError(f"DashScope rerank failed: {message}")

        results = response.output.get("results",[])
        scores = [0.0] * len(documents)
        for item in results:
            index = item.get("index")
            score = item.get("relevance_score")
            scores[int(index)] = float(score)
        return scores
    
@lru_cache(maxsize=1)
def get_reranker():
    return Reranker()