import os
import logging
from FlagEmbedding import FlagReranker
from dotenv import load_dotenv

from app.config.reranker_config import reranker_config

load_dotenv(override=True)
logger = logging.getLogger(__name__)
# from app.utils.logger import setup_logging
# setup_logging()

__reranker_model = None

def get_reranker_model() -> FlagReranker:
    global __reranker_model
    try:
        if __reranker_model is None:
            model_path = os.getenv("BGE_RERANKER_LARGE")
            device = os.getenv("BGE_RERANKER_DEVICE", "cpu")
            use_fp16 = os.getenv("BGE_RERANKER_FP16", "False").lower() == "true"

            logger.info(f"正在初始化 Reranker 模型，路径: {model_path}, 设备: {device}, fp16: {use_fp16}")
            __reranker_model = FlagReranker(
                model_name_or_path=model_path,
                devices=device,
                use_fp16=False,
                normalize=True,
                # query_instruction_for_rerank=reranker_config.text_rerank_instruct,
            )
            print(type(__reranker_model.tokenizer))
            logger.info("Reranker 模型初始化成功！")
        return __reranker_model

    except Exception as e:
        logger.error(f"初始化 Reranker 模型失败: {e}", exc_info=True)
        return None

def rerank_documents(query: str, documents: list[str]) -> list[float]:
    pairs = [(query, doc) for doc in documents]
    return get_reranker_model().compute_score(pairs)

if __name__ == '__main__':
    query = "1956年发生了哪一事件标志着人工智能这一学科的正式诞生？"
    documents = [
        "1950 年，艾伦·图灵发表了其具有里程碑意义的论文《计算机与智能》，将图灵测试作为衡量智能的标准，这一概念在人工智能的哲学研究和发展中具有基础性意义。",
        "1956 年的达特茅斯会议被认为是人工智能作为一个学科领域的诞生之地；在此会议上，约翰·麦卡锡等人创造了“人工智能”这一术语，并明确了其基本目标.",
        "1951 年，英国数学家兼计算机科学家艾伦·图灵也开发出了首个用于下棋的程序，这展示了人工智能在游戏策略方面的一个早期应用实例.",
        "1955 年，艾伦·纽厄尔、赫伯特·A·西蒙和克利夫·肖共同发明的“逻辑理论家”程序标志着首个真正的人工智能程序的诞生，该程序能够解决逻辑问题，类似于证明数学定理。."
    ]
    scores = rerank_documents(query, documents)
    print(scores)

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
(knowledge-base) PS D:\code\atguigu\knowledge-base> python -m app.utils.bge_rerank_utils
2026-07-20 13:09:02 - root - INFO - 日志系统初始化完成，日志文件: ./logs\knowledge_base.log
2026-07-20 13:09:02 - __main__ - INFO - 正在初始化 Reranker 模型，路径: D:\ai_models\modelscope_cache\models\BAAI--bge-reranker-large\snapshots\master, 设备: cpu, fp16: False
<class 'transformers.models.xlm_roberta.tokenization_xlm_roberta_fast.XLMRobertaTokenizerFast'>
2026-07-20 13:09:03 - __main__ - INFO - Reranker 模型初始化成功！
You're using a XLMRobertaTokenizerFast tokenizer. Please note that with a fast tokenizer, using the `__call__` method is faster than using a method to encode the text followed by a call to the `pad` method to get a padded encoding.
[0.01925404938221098, 0.9953422224496216, 0.051985629883683326, 0.7046943997161241]
"""