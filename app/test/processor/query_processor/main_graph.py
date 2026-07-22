from app.processor.query_processor.main_graph import KBQueryWorkflow
from app.utils.logger import setup_logging

# ===================== 用法示例 =====================
if __name__ == "__main__":
    logger = setup_logging()
    init_state = { "original_query": "如何使用万用表测量电压？"}
    workflow = KBQueryWorkflow()
    for chunk in workflow.run(init_state, stream=True):
        logger.warning(chunk)
        
    workflow.graph.get_graph().print_ascii()

"""
(knowledge-base) PS D:\knowledge-base> python -m app.test.processor.query_processor.main_graph
                                                             +-----------+
                                                             | __start__ |
                                                             +-----------+
                                                                   *
                                                                   *
                                                                   *
                                                      +------------------------+
                                                      | node_item_name_confirm |.
                                             .........+------------------------+ .........
                                    .........              ..                ...          ..........
                           .........                    ...                     ....                .........
                      .....                           ..                            ..                       .........
+-----------------------+           +----------------------------+           +---------------------+                  .....
| node_search_embedding |           | node_search_embedding_hyde |           | node_web_search_mcp |                      .
+-----------------------+****       +----------------------------+       ****+---------------------+                      .
                             ******                *              *******                                                 .
                                   ******          *        ******                                                        .
                                         ****      *    ****                                                              .
                                            +----------+                                                                  .
                                            | node_rrf |                                                                  .
                                            +----------+                                                                  .
                                                  *                                                                       .
                                                  *                                                                       .
                                                  *                                                                       .
                                           +-------------+                                                            .....
                                           | node_rerank |                                                   .........
                                           +-------------+                                          .........
                                                          **                              ..........
                                                            ***                  .........
                                                               **           .....
                                                        +--------------------+
                                                        | node_answer_output |
                                                        +--------------------+
                                                                   *
                                                                   *
                                                                   *
                                                              +---------+
                                                              | __end__ |
                                                              +---------+
2026-07-16 08:40:08 - base.py:32 - INFO - --- node_item_name_confirm 开始啦 ---
2026-07-16 08:40:08 - node_item_name_confirm.py:23 - INFO - 【node_item_name_confirm】节点逻辑
2026-07-16 08:40:08 - base.py:38 - INFO - --- node_item_name_confirm 完成啦 ---
2026-07-16 08:40:08 - main_graph.py:143 - WARNING - {'node_item_name_confirm': {'original_query': '如何使用万用表测量电压？'}}
2026-07-16 08:40:08 - base.py:32 - INFO - --- node_search_embedding 开始啦 ---
2026-07-16 08:40:08 - node_search_embedding.py:22 - INFO - 【node_search_embedding】节点逻辑
2026-07-16 08:40:08 - base.py:32 - INFO - --- node_search_embedding_hyde 开始啦 ---
2026-07-16 08:40:08 - base.py:38 - INFO - --- node_search_embedding 完成啦 ---
2026-07-16 08:40:08 - base.py:32 - INFO - --- node_web_search_mcp 开始啦 ---
2026-07-16 08:40:08 - node_search_embedding_hyde.py:23 - INFO - 【node_search_embedding_hyde】节点逻辑
2026-07-16 08:40:08 - main_graph.py:143 - WARNING - {'node_search_embedding': {'embedding_chunks': []}}
2026-07-16 08:40:08 - node_web_search_mcp.py:22 - INFO - 【node_web_search_mcp】节点逻辑
2026-07-16 08:40:08 - base.py:38 - INFO - --- node_search_embedding_hyde 完成啦 ---
2026-07-16 08:40:08 - base.py:38 - INFO - --- node_web_search_mcp 完成啦 ---
2026-07-16 08:40:08 - main_graph.py:143 - WARNING - {'node_search_embedding_hyde': {'hyde_embedding_chunks': []}}
2026-07-16 08:40:08 - main_graph.py:143 - WARNING - {'node_web_search_mcp': {'web_search_docs': []}}
2026-07-16 08:40:08 - base.py:32 - INFO - --- node_rrf 开始啦 ---
2026-07-16 08:40:08 - node_rrf.py:23 - INFO - 【node_rrf】节点逻辑
2026-07-16 08:40:08 - base.py:38 - INFO - --- node_rrf 完成啦 ---
2026-07-16 08:40:08 - main_graph.py:143 - WARNING - {'node_rrf': {'original_query': '如何使用万用表测量电压？', 'embedding_chunks': [], 'hyde_embedding_chunks': [], 'web_search_docs': []}}
2026-07-16 08:40:08 - base.py:32 - INFO - --- node_rerank 开始啦 ---
2026-07-16 08:40:08 - node_rerank.py:22 - INFO - 【node_rerank】节点逻辑
2026-07-16 08:40:08 - base.py:38 - INFO - --- node_rerank 完成啦 ---
2026-07-16 08:40:08 - main_graph.py:143 - WARNING - {'node_rerank': {'original_query': '如何使用万用表测量电压？', 'embedding_chunks': [], 'hyde_embedding_chunks': [], 'web_search_docs': []}}
2026-07-16 08:40:08 - base.py:32 - INFO - --- node_answer_output 开始啦 ---
2026-07-16 08:40:08 - node_answer_output.py:22 - INFO - 【node_answer_output】节点逻辑
2026-07-16 08:40:08 - base.py:38 - INFO - --- node_answer_output 完成啦 ---
2026-07-16 08:40:08 - main_graph.py:143 - WARNING - {'node_answer_output': {'original_query': '如何使用万用表测量电压？', 'embedding_chunks': [], 'hyde_embedding_chunks': [], 'web_search_docs': []}}
"""