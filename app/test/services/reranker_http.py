import json
from app.services.reranker_http import get_reranker

if __name__ == "__main__":
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
(knowledge-base) PS D:\knowledge-base> python -m app.utils.reranker_http_utils
[
  0.43115306465142617,
  0.9081537463058698,
  0.3368354789225787,
  0.5149084094896546
]
"""