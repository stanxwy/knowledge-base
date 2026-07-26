from typing import Any

from app.processor.query_processor.base import NodeBase
from app.processor.query_processor.state import QueryGraphState
from app.utils.json_format_utils import format_json

_WEIGHT_SEARCH_EMBEDDING = 1.0
_WEIGHT_HYDE = 1.0
_CONSTANT_K = 60

class NodeRrf(NodeBase):

    name: str = "node_rrf"

    def _rrf_merge(self, rrf_inputs, k: int = _CONSTANT_K, max_results: int | None = None) -> list[tuple[dict[str, Any], float]]:
        dict_score = {}
        dict_doc = {}

        for rrf_input, weight in rrf_inputs:
            for rank, doc in enumerate(rrf_input, start=1):
                chunk_id = doc.get('chunk_id')
                # RRF formula: score += weight / (k + rank)
                dict_score[chunk_id] = dict_score.get(chunk_id, 0.0) + weight / (k + rank)
                dict_doc.setdefault(chunk_id, doc)
        self.logger.info(f"dict_score: \n{format_json(dict_score)}")
        self.logger.info(f"dict_doc: \n{format_json(dict_doc)}")

        unsorted_results = [(dict_doc[chunk_id], score) for chunk_id, score in dict_score.items()]
        self.logger.info(f"unsorted_results: \n{format_json(unsorted_results)}")

        sorted_results = sorted(
            unsorted_results,
            # sort by 2nd element of tuple i.e. score
            key=lambda result_entry: result_entry[1],
            reverse=True
        )
        self.logger.info(f"sorted_results: \n{format_json(sorted_results)}")
        
        return sorted_results[:max_results] if max_results else sorted_results

    def process(self, state: QueryGraphState) -> QueryGraphState:
        
        embedding_search_list = [
            doc.get('entity') for doc in (state.get('embedding_chunks') or []) if isinstance(doc, dict)
        ]
        hyde_embedding_search_list = [
            doc.get('entity') for doc in (state.get('hyde_embedding_chunks') or []) if isinstance(doc, dict)
        ]

        # set weight for each result set from multi-query retrieval
        rrf_inputs = [
            (embedding_search_list, _WEIGHT_SEARCH_EMBEDDING),
            (hyde_embedding_search_list, _WEIGHT_HYDE)
        ]
        self.logger.info(f"rrf_inputs: \n{format_json(rrf_inputs)}")

        rrf_merge_results = self._rrf_merge(rrf_inputs)

        # discard score
        rrf_chunks = [doc for doc, _ in rrf_merge_results]
        self.logger.info(f"rrf_chunks: \n{format_json(rrf_chunks)}")

        return {
            'rrf_chunks': rrf_chunks
        }