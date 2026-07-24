from dotenv import load_dotenv
load_dotenv()
from app.processor.query_processor.nodes.node_rerank import NodeRerank
from app.utils.logger import setup_logging

if __name__ == "__main__":
    logger = setup_logging()

    mock_state = {
        "rewritten_query": "怎么测这块主板的短路问题？",
        "rrf_chunks": [
            {
                "chunk_id": "local_1",
                "title": "主板维修手册",
                "content": "主板短路通常表现为通电后风扇转一下就停，可以使用万用表的蜂鸣档测量。"
            },
            {
                "chunk_id": "local_2",
                "title": "闲聊",
                "content": "今天中午去吃猪脚饭吧，这块主板外观很漂亮。"
            },
        ],
        "web_search_docs": [
            {
                "url": "https://example.com/repair",
                "title": "短路查修指南",
                "snippet": "主板通电前先打各主供电电感对地阻值，阻值偏低就是短路。"
            },
            {
                "url": "https://example.com/news",
                "title": "科技新闻",
                "snippet": "苹果发布新款手机，A系列芯片性能提升20%。"
            },
        ],
    }
    node_rerank = NodeRerank()
    node_rerank(mock_state)

"""
(knowledge-base) D:\knowledge-base>python -m app.test.processor.query_processor.nodes.node_rerank
2026-07-24 09:17:12 - root - INFO - logging initialized: ./logs\knowledge_base.log
2026-07-24 09:17:12 - import.node_rerank - INFO - --- node_rerank started ---
2026-07-24 09:17:12 - import.node_rerank - INFO - Merged 4 documents:
[
    {
        "content": "主板短路通常表现为通电后风扇转一下就停，可以使用万用表的蜂鸣档测量。",
        "title": "主板维修手册",
        "chunk_id": "local_1",
        "url": null,
        "source": "local"
    },
    {
        "content": "今天中午去吃猪脚饭吧，这块主板外观很漂亮。",
        "title": "闲聊",
        "chunk_id": "local_2",
        "url": null,
        "source": "local"
    },
    {
        "content": "主板通电前先打各主供电电感对地阻值，阻值偏低就是短路。",
        "title": "短路查修指南",
        "chunk_id": null,
        "url": "https://example.com/repair",
        "source": "web"
    },
    {
        "content": "苹果发布新款手机，A系列芯片性能提升20%。",
        "title": "科技新闻",
        "chunk_id": null,
        "url": "https://example.com/news",
        "source": "web"
    }
]
2026-07-24 09:17:12 - app.services.reranker_http - INFO - DashScope rerank response:
{
  "status_code": 200,
  "request_id": "61bb6200-c71f-9508-abdd-a5f7f87942c1",
  "code": "",
  "message": "",
  "output": {
    "results": [
      {
        "index": 0,
        "relevance_score": 0.9244506623675683,
        "document": null
      },
      {
        "index": 2,
        "relevance_score": 0.9008794977295259,
        "document": null
      },
      {
        "index": 1,
        "relevance_score": 0.430502272123862,
        "document": null
      },
      {
        "index": 3,
        "relevance_score": 0.18357113032525535,
        "document": null
      }
    ]
  },
  "usage": {
    "total_tokens": 189
  },
  "headers": {
    "vary": "Origin,Access-Control-Request-Method,Access-Control-Request-Headers, Accept-Encoding",
    "content-type": "application/json;charset=utf-8",
    "x-request-id": "61bb6200-c71f-9508-abdd-a5f7f87942c1",
    "x-dashscope-call-gateway": "true",
    "x-dashscope-finished": "true",
    "x-dashscope-timeout": "3600",
    "req-cost-time": "120",
    "req-arrive-time": "1784855832150",
    "resp-start-time": "1784855832270",
    "x-envoy-upstream-service-time": "109",
    "content-encoding": "gzip",
    "date": "Fri, 24 Jul 2026 01:17:11 GMT",
    "server": "istio-envoy",
    "transfer-encoding": "chunked"
  }
}
2026-07-24 09:17:12 - import.node_rerank - INFO - Re-ranked 4 documents:
[
    {
        "content": "主板短路通常表现为通电后风扇转一下就停，可以使用万用表的蜂鸣档测量。",
        "title": "主板维修手册",
        "chunk_id": "local_1",
        "url": null,
        "source": "local",
        "score": 0.9244506623675683
    },
    {
        "content": "主板通电前先打各主供电电感对地阻值，阻值偏低就是短路。",
        "title": "短路查修指南",
        "chunk_id": null,
        "url": "https://example.com/repair",
        "source": "web",
        "score": 0.9008794977295259
    },
    {
        "content": "今天中午去吃猪脚饭吧，这块主板外观很漂亮。",
        "title": "闲聊",
        "chunk_id": "local_2",
        "url": null,
        "source": "local",
        "score": 0.430502272123862
    },
    {
        "content": "苹果发布新款手机，A系列芯片性能提升20%。",
        "title": "科技新闻",
        "chunk_id": null,
        "url": "https://example.com/news",
        "source": "web",
        "score": 0.18357113032525535
    }
]
2026-07-24 09:17:12 - import.node_rerank - INFO - Cliff detection, curr_idx=2, abs_gap=0.2469, rel_gap=0.5736
2026-07-24 09:17:12 - import.node_rerank - INFO - Cliff detected: 3, abs_gap=0.2469, rel_gap=0.5736
2026-07-24 09:17:12 - import.node_rerank - INFO - Final reranked documents after cliff cutoff:
[
    {
        "content": "主板短路通常表现为通电后风扇转一下就停，可以使用万用表的蜂鸣档测量。",
        "title": "主板维修手册",
        "chunk_id": "local_1",
        "url": null,
        "source": "local",
        "score": 0.9244506623675683
    },
    {
        "content": "主板通电前先打各主供电电感对地阻值，阻值偏低就是短路。",
        "title": "短路查修指南",
        "chunk_id": null,
        "url": "https://example.com/repair",
        "source": "web",
        "score": 0.9008794977295259
    },
    {
        "content": "今天中午去吃猪脚饭吧，这块主板外观很漂亮。",
        "title": "闲聊",
        "chunk_id": "local_2",
        "url": null,
        "source": "local",
        "score": 0.430502272123862
    }
]
2026-07-24 09:17:12 - import.node_rerank - INFO - --- node_rerank done ---
"""