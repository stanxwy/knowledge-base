from typing import Dict, Any, List, Tuple

from app.processor.query_processor.base import NodeBase
from app.processor.query_processor.state import QueryGraphState
from app.utils.json_format_utils import format_json
from app.services.reranker_http import Reranker, get_reranker

# -----------------------------
# Rerank / TopK 全局常量
# -----------------------------
# 动态 TopK 硬上限：最多取前 N 条（<=10）
RERANK_MAX_TOPK: int = 10
# 最小 TopK：至少保留前 N 条（>=1，且 <= RERANK_MAX_TOPK）
RERANK_MIN_TOPK: int = 3 #总数最少条数

# 断崖阈值（绝对，判断高分文档）
RERANK_GAP_ABS: float = 0.5
# 断崖阈值（相对，判断低分文档）
RERANK_GAP_RATIO: float = 0.25

class NodeRerank(NodeBase):
    """
    节点功能：使用 Cross-Encoder 模型对 RRF 后的结果进行精确打分重排。
    """
    name: str = "node_rerank"

    def __init__(self, reranker: Reranker = get_reranker()):
        self._reranker = reranker

    def _validate_input_state(self, state: QueryGraphState) -> Tuple[str, List[Dict[str, Any]], List[Dict[str, Any]]]:
        return state.get('rewritten_query'), state.get('rrf_chunks'), state.get('web_search_docs')

    def _step_1_merge_multi_source_docs(self, rrf_chunk, web_search_docs) -> List[Dict[str, Any]]:
        """合并本地 RRF 结果和网络搜索结果为统一格式"""
        final_docs = []
        # 1. 获取本地 RRF 的文档
        for rrf_doc in rrf_chunk:
            format_rrf_doc = {
                "content": rrf_doc.get('content'),
                "title": rrf_doc.get('title'),
                "chunk_id": rrf_doc.get('chunk_id'),
                "url": None,
                "source": "local"
            }
            final_docs.append(format_rrf_doc)

        # 2. 获取 web 远程的文档
        for web_doc in web_search_docs:
            format_web_doc = {
                "content": web_doc.get('snippet'),
                "title": web_doc.get('title'),
                "chunk_id": None,
                "url": web_doc.get('url'),
                "source": "web"
            }
            final_docs.append(format_web_doc)
        return final_docs

    def _step_2_rerank_merged_docs(self, rewritten_query: str, merged_multi_docs: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
        """使用 Reranker 模型对文档进行精排"""
        try:
            user_query = rewritten_query
            # 获取文档列表的conten字段组成列表
            contents = [doc.get("content") for doc in merged_multi_docs]
            # 调用Rerank模型：交叉编码器（精排阶段）
            # Query 和 Document 联合编码，精度更高
            rerank_scores = self._reranker.rerank_documents(user_query, contents)

            scored_docs = [{**doc, "score": score} for doc, score in zip(merged_multi_docs, rerank_scores)]
            # 等同如下写法
            # scored_docs = []
            # for doc, score in zip(merged_multi_docs, rerank_scores):
            #     scored_docs.append({
            #         "content": doc.get("content"),
            #         "title": doc.get("title"),
            #         "chunk_id": doc.get("chunk_id"),
            #         "url": doc.get("url"),
            #         "source": doc.get("source"),
            #         "score": float(score),
            #     })
            sorted_score_docs = sorted(
                scored_docs,
                key=lambda doc: doc["score"],
                reverse=True
            )
            return sorted_score_docs
        except Exception as e:
            self.logger.error(f"Rerank 重排序失败: {str(e)}")
            return [{**merged_multi_docs, "score": None}]
        
    def _step_3_cliff_cutoff(self, ranked_docs: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
        """断崖检测截断：相邻得分差距超过阈值时截断。"""
        if not ranked_docs:
            return []
        upper_bound = min(RERANK_MAX_TOPK, len(ranked_docs))
        lower_bound = min(RERANK_MIN_TOPK, upper_bound)

        # 默认值：取满硬上限（最多10条）
        cutoff_pos = upper_bound

        # 遍历范围：从min_topk-1到max_topk-2（索引从0开始），检测相邻两个文档的分数差
        # 例：min_topk=3，max_topk=10 → 遍历i=2,3,4,5,6,7,8（对应第3~9条文档，检测与下一条的差距）
        for idx in range(lower_bound - 1, upper_bound - 1):
            current_score = ranked_docs[idx].get("score")
            next_score = ranked_docs[idx + 1].get("score")

            if current_score is None or next_score is None:
                continue
            # 计算相邻文档的分数绝对差距（因已降序，gap≥0）
            abs_gap = current_score - next_score
            # 计算相对差距：绝对差距 / 当前文档分数（+1e-6避免除数为0/极小值，防止程序报错）
            # 1e-6 是 Python 中科学计数法的写法，等价于 0.000001（10 的负 6 次方，也就是百万分之一）。
            rel_gap = abs_gap / (abs(current_score) + 1e-6)

            # 触发断崖截断条件：绝对差距≥绝对阈值 OR 相对差距≥相对阈值
            # 满足任一条件，说明下一条文档相关性骤降，截断在当前位置
            self.logger.info(f"断崖检测: 当前位置 {idx}, abs_gap={abs_gap:.4f}, rel_gap={rel_gap:.4f}")
            if abs_gap >= RERANK_GAP_ABS or rel_gap >= RERANK_GAP_RATIO:
                # 最终取前i+1条（索引转实际数量，如i=2 → 取前3条）
                cutoff_pos = idx + 1
                self.logger.info(f"断崖判定: 位置 {idx + 1}, abs_gap={abs_gap:.4f}, rel_gap={rel_gap:.4f}")
                break
        return ranked_docs[:cutoff_pos]

    def process(self, state: QueryGraphState) -> QueryGraphState:
        """
        执行重排序
        流程: 合并多源文档 → Reranker 计算相关性 → 断崖检测动态截断
        :param state: 需包含 rrf_chunks、web_search_docs、rewritten_query
        :return: 更新后的 state，包含 reranked_docs
        """
        rewritten_query, rrf_chunks, web_search_docs = self._validate_input_state(state)

        # 1. 合并多源文档
        merged_multi_docs: List[Dict[str, Any]] = self._step_1_merge_multi_source_docs(rrf_chunks, web_search_docs)
        self.logger.info(f"merged_multi_docs: \n{format_json(merged_multi_docs)}")

        # 2. Rerank 精排(精排打分)
        reranked_docs: List[Dict[str, Any]] = self._step_2_rerank_merged_docs(rewritten_query, merged_multi_docs)
        self.logger.info(f"reranked_docs: \n{format_json(reranked_docs)}")

        # 3. 动态 Top_K 截取(断崖检测)
        cutoff_docs = self._step_3_cliff_cutoff(reranked_docs)
        self.logger.info(f"cutoff_docs: \n{format_json(cutoff_docs)}")

        # 4. 更新state
        return {
            "reranked_docs": cutoff_docs
        }

if __name__ == "__main__":
    from app.utils.logger import setup_logging
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
    result = node_rerank(mock_state)

"""
(knowledge-base) PS D:\knowledge-base> python -m app.processor.query_processor.nodes.node_rerank
2026-07-19 09:25:34 - root - INFO - 日志系统初始化完成，日志文件: ./logs\knowledge_base.log
2026-07-19 09:25:34 - import.node_rerank - INFO - --- node_rerank 开始啦 ---
2026-07-19 09:25:34 - import.node_rerank - INFO - merged_multi_docs:
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
2026-07-19 09:25:35 - root - INFO - DashScope rerank response:
{
  "status_code": 200,
  "request_id": "a398c4c1-b581-9ff6-bc6c-b98cbd2cd2b0",
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
    "x-request-id": "a398c4c1-b581-9ff6-bc6c-b98cbd2cd2b0",
    "x-dashscope-call-gateway": "true",
    "x-dashscope-finished": "true",
    "x-dashscope-timeout": "3600",
    "req-cost-time": "150",
    "req-arrive-time": "1784424333760",
    "resp-start-time": "1784424333910",
    "x-envoy-upstream-service-time": "138",
    "content-encoding": "gzip",
    "date": "Sun, 19 Jul 2026 01:25:33 GMT",
    "server": "istio-envoy",
    "transfer-encoding": "chunked"
  }
}
2026-07-19 09:25:35 - import.node_rerank - INFO - reranked_docs:
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
2026-07-19 09:25:35 - import.node_rerank - INFO - 断崖检测: 当前位置 2, abs_gap=0.2469, rel_gap=0.5736
2026-07-19 09:25:35 - import.node_rerank - INFO - 断崖判定: 位置 3, abs_gap=0.2469, rel_gap=0.5736
2026-07-19 09:25:35 - import.node_rerank - INFO - cutoff_docs:
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
2026-07-19 09:25:35 - import.node_rerank - INFO - --- node_rerank 完成啦 ---
"""