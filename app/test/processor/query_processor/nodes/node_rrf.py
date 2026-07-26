from app.workflows.query.nodes.node_rrf import NodeRrf
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
(knowledge-base) D:\knowledge-base>python -m app.test.workflows.query.nodes.node_rrf
2026-07-23 22:21:24 - root - INFO - logging initialized: ./logs\knowledge_base.log
2026-07-23 22:21:24 - import.node_rrf - INFO - --- node_rrf started ---
2026-07-23 22:21:24 - import.node_rrf - INFO - rrf_inputs:
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
2026-07-23 22:21:24 - import.node_rrf - INFO - dict_score:
{
    "chunk_1": 0.03278688524590164,
    "chunk_2": 0.03200204813108039,
    "chunk_3": 0.015873015873015872,
    "chunk_4": 0.016129032258064516
}
2026-07-23 22:21:24 - import.node_rrf - INFO - dict_doc:
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
2026-07-23 22:21:24 - import.node_rrf - INFO - unsorted_results:
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
2026-07-23 22:21:24 - import.node_rrf - INFO - sorted_results:
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
2026-07-23 22:21:24 - import.node_rrf - INFO - rrf_chunks:
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
2026-07-23 22:21:24 - import.node_rrf - INFO - --- node_rrf done ---
"""