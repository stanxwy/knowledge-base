import json

from dotenv import load_dotenv

load_dotenv()

from app.infra.external.reranker.base import get_reranker
from app.utils.logger import setup_logging

if __name__ == "__main__":
    setup_logging("DEBUG")

    query = "1956年发生了哪一事件标志着人工智能这一学科的正式诞生？"
    documents = [
        "1950 年，艾伦·图灵发表了其具有里程碑意义的论文《计算机与智能》，将图灵测试作为衡量智能的标准，这一概念在人工智能的哲学研究和发展中具有基础性意义。",
        "1956 年的达特茅斯会议被认为是人工智能作为一个学科领域的诞生之地；在此会议上，约翰·麦卡锡等人创造了“人工智能”这一术语，并明确了其基本目标.",
        "1951 年，英国数学家兼计算机科学家艾伦·图灵也开发出了首个用于下棋的程序，这展示了人工智能在游戏策略方面的一个早期应用实例.",
        "1955 年，艾伦·纽厄尔、赫伯特·A·西蒙和克利夫·肖共同发明的“逻辑理论家”程序标志着首个真正的人工智能程序的诞生，该程序能够解决逻辑问题，类似于证明数学定理。."
    ]
    reranked = get_reranker().rerank_documents(query, documents)
    print(json.dumps(reranked, ensure_ascii=False, indent=2))

"""
(knowledge-base) D:\knowledge-base>python -m app.test.services.reranker_http
2026-07-24 10:14:44 - root - INFO - logging initialized: ./logs\knowledge_base.log
2026-07-24 10:14:44 - dashscope - DEBUG - Request body: {'model': 'qwen3-rerank', 'parameters': {'return_documents': False, 'top_n': 4, 'instruct': '针对给定的查询，检索能够解答该查询的相关段落'}, 'input': {'query': '1956年发生了哪一事件标志着人工智能这一学科的正式诞生？', 'documents': ['1950 年，艾伦·图灵发表了其具有里程碑意义的论文《计算机与智能》，将图灵测试作为衡量智能的标准，这一概念在人工智能的哲学研究和发展中具有基础性意义。', '1956 年的达特茅斯会议被认为是人工智能作为一个学科领域的诞生之地；在此会议上，约翰·麦卡锡等人创造了“人工智能”这一术语，并明确了其基本目标.', '1951 年，英国数学家兼计算机科学家艾伦·图灵也开发出了首个用于下棋的程序，这展示了人工智能在游戏策略方面的一个早期应用实例.', '1955 年，艾伦·纽厄尔、赫伯特·A·西蒙和克利夫·肖共同发明的“逻辑理论家”程序标志着首个真正的人工智能程序的诞生，该程序能够解决逻辑问题，类似于证明数学定理。.']}}
2026-07-24 10:14:44 - urllib3.connectionpool - DEBUG - Starting new HTTPS connection (1): dashscope.aliyuncs.com:443
2026-07-24 10:14:45 - urllib3.connectionpool - DEBUG - https://dashscope.aliyuncs.com:443 "POST /api/v1/services/rerank/text-rerank/text-rerank HTTP/1.1" 200 None
2026-07-24 10:14:45 - dashscope - DEBUG - Response: {'output': {'results': [{'index': 1, 'relevance_score': 0.9081537463058698}, {'index': 3, 'relevance_score': 0.5149084094896546}, {'index': 0, 'relevance_score': 0.43115310389814865}, {'index': 2, 'relevance_score': 0.3368354789225787}]}, 'usage': {'total_tokens': 333}, 'request_id': '8effa856-a5a7-9cf3-9757-49acfe9b4f82'}
2026-07-24 10:14:45 - app.services.reranker_http - INFO - DashScope rerank response:
{
  "status_code": 200,
  "request_id": "8effa856-a5a7-9cf3-9757-49acfe9b4f82",
  "code": "",
  "message": "",
  "output": {
    "results": [
      {
        "index": 1,
        "relevance_score": 0.9081537463058698,
        "document": null
      },
      {
        "index": 3,
        "relevance_score": 0.5149084094896546,
        "document": null
      },
      {
        "index": 0,
        "relevance_score": 0.43115310389814865,
        "document": null
      },
      {
        "index": 2,
        "relevance_score": 0.3368354789225787,
        "document": null
      }
    ]
  },
  "usage": {
    "total_tokens": 333
  },
  "headers": {
    "vary": "Origin,Access-Control-Request-Method,Access-Control-Request-Headers, Accept-Encoding",
    "content-type": "application/json;charset=utf-8",
    "x-request-id": "8effa856-a5a7-9cf3-9757-49acfe9b4f82",
    "x-dashscope-call-gateway": "true",
    "x-dashscope-finished": "true",
    "x-dashscope-timeout": "3600",
    "req-cost-time": "126",
    "req-arrive-time": "1784859284713",
    "resp-start-time": "1784859284840",
    "x-envoy-upstream-service-time": "114",
    "content-encoding": "gzip",
    "date": "Fri, 24 Jul 2026 02:14:44 GMT",
    "server": "istio-envoy",
    "transfer-encoding": "chunked"
  }
}
[
  0.43115310389814865,
  0.9081537463058698,
  0.3368354789225787,
  0.5149084094896546
]
"""