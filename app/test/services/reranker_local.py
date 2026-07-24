import json
from dotenv import load_dotenv
load_dotenv()

from app.services.reranker_local import get_reranker
from app.utils.logger import setup_logging

if __name__ == '__main__':
    setup_logging("DEBUG")
    
    query = "1956年发生了哪一事件标志着人工智能这一学科的正式诞生？"
    documents = [
        "1950 年，艾伦·图灵发表了其具有里程碑意义的论文《计算机与智能》，将图灵测试作为衡量智能的标准，这一概念在人工智能的哲学研究和发展中具有基础性意义。",
        "1956 年的达特茅斯会议被认为是人工智能作为一个学科领域的诞生之地；在此会议上，约翰·麦卡锡等人创造了“人工智能”这一术语，并明确了其基本目标.",
        "1951 年，英国数学家兼计算机科学家艾伦·图灵也开发出了首个用于下棋的程序，这展示了人工智能在游戏策略方面的一个早期应用实例.",
        "1955 年，艾伦·纽厄尔、赫伯特·A·西蒙和克利夫·肖共同发明的“逻辑理论家”程序标志着首个真正的人工智能程序的诞生，该程序能够解决逻辑问题，类似于证明数学定理。."
    ]
    scores = get_reranker().rerank_documents(query, documents)
    print(json.dumps(scores, indent=4))

"""
#⚠️：安装FlagEmbedding的时候会自动安装一个cpu版本的torch替换掉之前的gpu版本的torch，
# 要解决这个问题需要将以下内容配置在pyproject.toml中锁定这三个依赖的版本为cuda版
# 另外 transformers 和 FlagEmbedding  也有版本兼容问题，这里也锁定 transformers 的版本
"flagembedding>=1.3.5",
"transformers>=4.45.0,<5.0.0",

(knowledge-base) PS D:\knowledge-base> uv sync
Resolved 164 packages in 21.35s
Prepared 2 packages in 3.50s
Uninstalled 3 packages in 449ms
░░░░░░░░░░░░░░░░░░░░ [0/2] Installing wheels...                                                                                                                                             warning: Failed to hardlink files; falling back to full copy. This may lead to degraded performance.
         If the cache and target directories are on different filesystems, hardlinking may not be supported.
         If this is intentional, set `export UV_LINK_MODE=copy` or use `--link-mode=copy` to suppress this warning.
Installed 2 packages in 1.39s
 - hf-xet==1.5.1
 - huggingface-hub==1.23.0
 + huggingface-hub==0.36.2
 - transformers==5.13.1
 + transformers==4.57.6

(knowledge-base) PS D:\knowledge-base> python -m app.utils.bge_rerank_utils
<class 'transformers.models.xlm_roberta.tokenization_xlm_roberta_fast.XLMRobertaTokenizerFast'>
You're using a XLMRobertaTokenizerFast tokenizer. Please note that with a fast tokenizer, using the `__call__` method is faster than using a method to encode the text followed by a call to the `pad` method to get a padded encoding.
[0.0277058673878419, 0.9980846725164658, 0.041886650306271686, 0.50644986966622]

# with query_instruction_for_rerank
(knowledge-base) D:\knowledge-base>python -m app.test.services.reranker_local
2026-07-24 10:11:25 - root - INFO - logging initialized: ./logs\knowledge_base.log
2026-07-24 10:11:25 - app.services.reranker_local - INFO - Initializing Reranker...
RerankerConfig(text_rerank_api_key='sk-ws-H.EMRLMMH.b5oG.MEUCIEUTDFBGW2yxwBPgwwFev5thtDIbXTtyUJEdmj3X3uNDAiEAqUguWZEovOVdVtkQN7WvpAyF7xzWhRgcdTB6z1W_Wg4', text_rerank_model='qwen3-rerank', text_rerank_instruct='针对给定的查询，检索能够解答该查询的相关段落', bge_rerank_model='D:\\ai_models\\modelscope_cache\\models\\BAAI--bge-reranker-large\\snapshots\\master', bge_rerank_device='cpu', bge_rerank_fp16=True)
2026-07-24 10:11:26 - app.services.reranker_local - INFO - Reranker initialized
You're using a XLMRobertaTokenizerFast tokenizer. Please note that with a fast tokenizer, using the `__call__` method is faster than using a method to encode the text followed by a call to the `pad` method to get a padded encoding.
[
    0.01925404938221098,
    0.9953422224496216,
    0.051985629883683326,
    0.7046943997161241
]
"""