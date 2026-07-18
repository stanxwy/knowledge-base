from typing import List, Dict, Any, Tuple

from app.processor.query_processor.base import NodeBase
from app.processor.query_processor.state import QueryGraphState
from app.utils.json_format_utils import format_json


class NodeRrf(NodeBase):
    """
    节点功能：Reciprocal Rank Fusion
    将多路召回的结果（向量、HyDE、Web）进行加权融合排序。
    """
    name: str = "node_rrf"

    def _rrf_merge(self, rrf_inputs, k: int = 60, max_results: int = None) -> List[Tuple[Dict[str, Any], float]]:
        """
        利用 RRF 公式计算每一个文档的总得分
        :param rrf_inputs:  列表，每个元素是(各路的搜索结果列表, 权重)的元组
        :param k:           平滑参数(RFF常数)，通常取 60
        :param max_results: 合并完之后返回的文档数，None 表示全部
        :return:            合并以及排序后的文档列表，[(元素, RRF 得分), ...] 按得分降序
        """
        chunk_scores = {}  # 存放所有 chunk 的 RRF 计算后的分数值
        chunk_data = {}  # 存放所有 chunk 的文档数据

        for rrf_input, weight in rrf_inputs:
            for rank, doc in enumerate(rrf_input, start=1):
                chunk_id = doc.get('chunk_id')
                # RRF 公式: score += weight / (k + rank)
                chunk_scores[chunk_id] = chunk_scores.get(chunk_id, 0.0) + weight / (k + rank)

                # 使用 setdefault 保留首次遇到的文档版本(只记录第一次)
                chunk_data.setdefault(chunk_id, doc)
        self.logger.info(f"chunk_scores: \n{format_json(chunk_scores)}")
        self.logger.info(f"chunk_data: \n{format_json(chunk_data)}")

        # 按得分降序排序
        unsorted_results = [(chunk_data[chunk_id], score) for chunk_id, score in chunk_scores.items()]
        self.logger.info(f"unsorted_results: \n{format_json(unsorted_results)}")

        sorted_results = sorted(
            unsorted_results,
            # 排序时看每个元素的第 2 个值（也就是分数）
            key=lambda result_entry: result_entry[1],
            reverse=True
        )
        self.logger.info(f"sorted_results: \n{format_json(sorted_results)}")
        # 等价写法
        # def get_score(item):
        #     return item[1]  # 返回分数
        # sorted_results = sorted(unsorted_results, key=get_score, reverse=True)

        # 动态截取前 max_results 条
        return sorted_results[:max_results] if max_results else sorted_results

    def process(self, state: QueryGraphState) -> QueryGraphState:
        # 1. 获取各路搜索的结果（排除网络搜索: reranK节点做）
        embedding_search_list = [
            doc.get('entity') for doc in (state.get('embedding_chunks') or []) if isinstance(doc, dict)
        ]
        hyde_embedding_search_list = [
            doc.get('entity') for doc in (state.get('hyde_embedding_chunks') or []) if isinstance(doc, dict)
        ]

        # 2. 为不同路的搜索结果设置不同的权重
        rrf_inputs = [
            (embedding_search_list, 1.0),
            (hyde_embedding_search_list, 1.0)
        ]
        self.logger.info(f"rrf_inputs: \n{format_json(rrf_inputs)}")

        # 3. 利用RRF的计算公式去获取到所有路查询到的所有chunk对应的score
        rrf_merge_results = self._rrf_merge(rrf_inputs)

        # 4. 获取rrf_chunks（只取文档，不要分数）
        rrf_chunks = [doc for doc, _ in rrf_merge_results]
        self.logger.info(f"rrf_chunks: \n{format_json(rrf_chunks)}")

        # 6. 返回state
        return {
            'rrf_chunks': rrf_chunks
        }
    
if __name__ == '__main__':
    from app.utils.logger import setup_logging
    logger = setup_logging()
    # 模拟两路检索结果
    mock_state = {
        "embedding_chunks": [
            {"entity": {"chunk_id": "chunk_1", "content": "向量搜索结果#1"}},
            {"entity": {"chunk_id": "chunk_2", "content": "向量搜索结果#2"}},
            {"entity": {"chunk_id": "chunk_3", "content": "向量搜索结果#3"}},
        ],
        "hyde_embedding_chunks": [
            {"entity": {"chunk_id": "chunk_1", "content": "HyDE搜索结果#1"}},
            {"entity": {"chunk_id": "chunk_4", "content": "HyDE搜索结果#2"}},
            {"entity": {"chunk_id": "chunk_2", "content": "HyDE搜索结果#3"}},
        ]
    }
    node_rrf = NodeRrf()
    result = node_rrf(mock_state)

"""
(knowledge-base) PS D:\code\atguigu\knowledge-base> python -m app.processor.query_processor.nodes.node_rrf
2026-07-18 21:14:57 - root - INFO - 日志系统初始化完成，日志文件: ./logs\knowledge_base.log
2026-07-18 21:14:57 - import.node_rrf - INFO - --- node_rrf 开始啦 ---
2026-07-18 21:14:57 - import.node_rrf - INFO - rrf_inputs:
[
    [
        [
            {
                "chunk_id": "chunk_1",
                "content": "向量搜索结果#1"
            },
            {
                "chunk_id": "chunk_2",
                "content": "向量搜索结果#2"
            },
            {
                "chunk_id": "chunk_3",
                "content": "向量搜索结果#3"
            }
        ],
        1.0
    ],
    [
        [
            {
                "chunk_id": "chunk_1",
                "content": "HyDE搜索结果#1"
            },
            {
                "chunk_id": "chunk_4",
                "content": "HyDE搜索结果#2"
            },
            {
                "chunk_id": "chunk_2",
                "content": "HyDE搜索结果#3"
            }
        ],
        1.0
    ]
]
2026-07-18 21:14:57 - import.node_rrf - INFO - chunk_scores:
{
    "chunk_1": 0.03278688524590164,
    "chunk_2": 0.03200204813108039,
    "chunk_3": 0.015873015873015872,
    "chunk_4": 0.016129032258064516
}
2026-07-18 21:14:57 - import.node_rrf - INFO - chunk_data:
{
    "chunk_1": {
        "chunk_id": "chunk_1",
        "content": "向量搜索结果#1"
    },
    "chunk_2": {
        "chunk_id": "chunk_2",
        "content": "向量搜索结果#2"
    },
    "chunk_3": {
        "chunk_id": "chunk_3",
        "content": "向量搜索结果#3"
    },
    "chunk_4": {
        "chunk_id": "chunk_4",
        "content": "HyDE搜索结果#2"
    }
}
2026-07-18 21:14:57 - import.node_rrf - INFO - unsorted_results:
[
    [
        {
            "chunk_id": "chunk_1",
            "content": "向量搜索结果#1"
        },
        0.03278688524590164
    ],
    [
        {
            "chunk_id": "chunk_2",
            "content": "向量搜索结果#2"
        },
        0.03200204813108039
    ],
    [
        {
            "chunk_id": "chunk_3",
            "content": "向量搜索结果#3"
        },
        0.015873015873015872
    ],
    [
        {
            "chunk_id": "chunk_4",
            "content": "HyDE搜索结果#2"
        },
        0.016129032258064516
    ]
]
2026-07-18 21:14:57 - import.node_rrf - INFO - sorted_results:
[
    [
        {
            "chunk_id": "chunk_1",
            "content": "向量搜索结果#1"
        },
        0.03278688524590164
    ],
    [
        {
            "chunk_id": "chunk_2",
            "content": "向量搜索结果#2"
        },
        0.03200204813108039
    ],
    [
        {
            "chunk_id": "chunk_4",
            "content": "HyDE搜索结果#2"
        },
        0.016129032258064516
    ],
    [
        {
            "chunk_id": "chunk_3",
            "content": "向量搜索结果#3"
        },
        0.015873015873015872
    ]
]
2026-07-18 21:14:57 - import.node_rrf - INFO - rrf_chunks:
[
    {
        "chunk_id": "chunk_1",
        "content": "向量搜索结果#1"
    },
    {
        "chunk_id": "chunk_2",
        "content": "向量搜索结果#2"
    },
    {
        "chunk_id": "chunk_4",
        "content": "HyDE搜索结果#2"
    },
    {
        "chunk_id": "chunk_3",
        "content": "向量搜索结果#3"
    }
]
2026-07-18 21:14:57 - import.node_rrf - INFO - --- node_rrf 完成啦 ---
"""