from app.processor.query_processor.nodes.node_rrf import NodeRrf
from app.utils.logger import setup_logging

if __name__ == '__main__':
    logger = setup_logging()

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
(knowledge-base) PS D:\knowledge-base> python -m app.processor.query_processor.nodes.node_rrf
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