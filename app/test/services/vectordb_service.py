import json

from app.infra.persistence.vectordb import ItemNameVectorDBService

if __name__ == '__main__':
    item_names = ["烫金机", "电脑"]
    result = ItemNameVectorDBService().hybrid_search_item_name(item_names)
    print(f"\n{json.dumps(result, ensure_ascii=False, indent=4)}")

"""
(knowledge-base) D:\knowledge-base>python -m app.test.services.vectordb_service
2026-07-21 13:02:59,587 [WARNING][__init__]: Using fp16 with CPU can lead to runtime errors such as 'LayerNormKernelImpl', It's recommended to set 'use_fp16 = False' when using cpu.  (bge_m3.py:50)
You're using a XLMRobertaTokenizerFast tokenizer. Please note that with a fast tokenizer, using the `__call__` method is faster than using a method to encode the text followed by a call to the `pad` method to get a padded encoding.
2026-07-21 13:03:03.732 | INFO     | __main__:_hybrid_search:351 - Milvus混合搜索完成，集合[kb_item_names]共检索到5条结果
2026-07-21 13:03:03.732 | INFO     | __main__:hybrid_search_item_name:155 - 关键字[烫金机]在向量数据库中的检索结果：
[
    [
        {
            "pk": 467662309254248226,
            "distance": 0.8375090956687927,
            "entity": {
                "item_name": "HAK180烫金机"
            }
        },
        {
            "pk": 467684978484127359,
            "distance": 0.6518365740776062,
            "entity": {
                "item_name": "华为B530台式计算机"
            }
        },
        {
            "pk": 467684978484127436,
            "distance": 0.6430261135101318,
            "entity": {
                "item_name": "万用表RS-12"
            }
        },
        {
            "pk": 467684978484127344,
            "distance": 0.5528860092163086,
            "entity": {
                "item_name": "苏伯尓B3-211H显示器"
            }
        },
        {
            "pk": 467721339624402732,
            "distance": 0.548590898513794,
            "entity": {
                "item_name": "苏伯尓M272Q显示器"
            }
        }
    ]
]
2026-07-21 13:03:03.739 | INFO     | __main__:_hybrid_search:351 - Milvus混合搜索完成，集合[kb_item_names]共检索到5条结果
2026-07-21 13:03:03.740 | INFO     | __main__:hybrid_search_item_name:155 - 关键字[电脑]在向量数据库中的检索结果：
[
    [
        {
            "pk": 467684978484127359,
            "distance": 0.7222466468811035,
            "entity": {
                "item_name": "华为B530台式计算机"
            }
        },
        {
            "pk": 467684978484127415,
            "distance": 0.6882514953613281,
            "entity": {
                "item_name": "华为W585台式机"
            }
        },
        {
            "pk": 467662309254248226,
            "distance": 0.6682947278022766,
            "entity": {
                "item_name": "HAK180烫金机"
            }
        },
        {
            "pk": 467721339624402732,
            "distance": 0.585623562335968,
            "entity": {
                "item_name": "苏伯尓M272Q显示器"
            }
        },
        {
            "pk": 467684978484127344,
            "distance": 0.5783058404922485,
            "entity": {
                "item_name": "苏伯尓B3-211H显示器"
            }
        }
    ]
]
2026-07-21 13:03:03.740 | INFO     | __main__:<module>:360 - 
[
    {
        "extracted_name": "烫金机",
        "matches": [
            {
                "item_name": "HAK180烫金机",
                "score": 0.8375090956687927
            },
            {
                "item_name": "华为B530台式计算机",
                "score": 0.6518365740776062
            },
            {
                "item_name": "万用表RS-12",
                "score": 0.6430261135101318
            },
            {
                "item_name": "苏伯尓B3-211H显示器",
                "score": 0.5528860092163086
            },
            {
                "item_name": "苏伯尓M272Q显示器",
                "score": 0.548590898513794
            }
        ]
    },
    {
        "extracted_name": "电脑",
        "matches": [
            {
                "item_name": "华为B530台式计算机",
                "score": 0.7222466468811035
            },
            {
                "item_name": "华为W585台式机",
                "score": 0.6882514953613281
            },
            {
                "item_name": "HAK180烫金机",
                "score": 0.6682947278022766
            },
            {
                "item_name": "苏伯尓M272Q显示器",
                "score": 0.585623562335968
            },
            {
                "item_name": "苏伯尓B3-211H显示器",
                "score": 0.5783058404922485
            }
        ]
    }
]
"""