from loguru import logger
from pymilvus import MilvusClient, DataType, AnnSearchRequest, WeightedRanker
from typing import List, Dict

from app.config.milvus_config import milvus_config
from app.processor.import_processor.exceptions import MilvusError

_milvus_client = None

def escape_milvus_string(value: str) -> str:
    """
    Milvus数据库过滤表达式中字符串的安全转义函数（防止解析失败）
    作用：
        转义特殊字符（反斜杠、双引号），避免Milvus解析filter时报错
    参数：
        value: 需要转义的原始字符串
    返回：
        str: 转义后的安全字符串
    """
    # 转义反斜杠（\ → \\） 双引号（" → \"） 单引号（' → \'）
    value = value.replace("\\", "\\\\").replace('"', '\\"').replace("'", "\\'")
    return value

def get_milvus_client():
    global _milvus_client
    if _milvus_client is None:
        _milvus_client = MilvusClient(milvus_config.milvus_url)
    return _milvus_client

# item_name 集合操作
def create_item_name_collection():
    # 创建Schema（数据结构定义）
    # auto_id=True：主键自动生成；enable_dynamic_field=True：支持动态字段（允许插入 Schema 中未定义的字段）
    milvus_client = get_milvus_client()
    collection_name = milvus_config.item_name_collection  # 集合名称
    if milvus_client.has_collection(collection_name):
        logger.warning(f"Milvus 集合 {collection_name} 已存在，跳过创建")
        return

    schema = milvus_client.create_schema(auto_id=True, enable_dynamic_field=True)
    # 添加主键字段（INT64类型，自增）
    schema.add_field(
        field_name="pk",
        datatype=DataType.INT64,
        is_primary=True,
        auto_id=True
    )
    # 添加文件标题字段（VARCHAR类型，最大长度65535）
    schema.add_field(
        field_name="file_title",
        datatype=DataType.VARCHAR,
        max_length=100
    )
    # 添加商品名称字段（VARCHAR类型，最大长度65535）
    schema.add_field(
        field_name="item_name",
        datatype=DataType.VARCHAR,
        max_length=100
    )
    # 添加稠密向量字段（FLOAT_VECTOR类型，1024维，BGE-M3模型固定维度）
    schema.add_field(
        field_name="dense_vector",
        datatype=DataType.FLOAT_VECTOR,
        dim=1024
    )
    # 添加稀疏向量字段（SPARSE_FLOAT_VECTOR类型，变长，适配BGE-M3的稀疏向量）
    schema.add_field(field_name="sparse_vector", datatype=DataType.SPARSE_FLOAT_VECTOR)

    # 3. 构建索引参数（提升向量检索性能）
    index_params = milvus_client.prepare_index_params()
    # 为稠密向量创建索引（IVF_FLAT：兼容性好，适合小数据量）
    # 核心是 “先聚类分桶、再桶内暴力精确检索”。
    index_params.add_index(
        field_name="dense_vector",  # 字段名
        index_name="dense_vector_index",  # 索引名
        index_type="IVF_FLAT",  # 索引类型（兼容所有Milvus版本）
        metric_type="COSINE",  # 相似度计算方式（余弦相似度）
        params={"nlist": 128}  # 聚类数（影响检索精度/速度）
    )

    # 为稀疏向量创建索引（SPARSE_INVERTED_INDEX：稀疏向量专用索引）
    index_params.add_index(
        field_name="sparse_vector",  # 字段名
        index_name="sparse_vector_index",  # 索引名
        index_type="SPARSE_INVERTED_INDEX",  # 索引类型
        metric_type="IP",  # 相似度计算方式（内积）
        params={
            "inverted_index_algo": "DAAT_MAXSCORE",
            # 高效的稀疏检索算法

            "normalize": True,
            # ↑ L2 归一化，让内积 (IP) 等价于余弦相似度

            "quantization": "none"
            # ↑ 关闭量化，保持原始精度：模型生成的向量已经压缩的一半的精度了（BGE_FP16=1），这里就不再压缩了
            # "quantization": "none" → 存储原始向量，不压缩
            # "quantization": "sq8" → 存储压缩后的向量（8-bit 量化
        })

    # 4. 创建集合（Schema + 索引）
    milvus_client.create_collection(
        collection_name=collection_name,
        schema=schema,
        index_params=index_params
    )

def insert_into_item_name_collection(data: Dict):
    result = get_milvus_client().insert(collection_name=milvus_config.item_name_collection, data=[data])
    logger.info(f"Milvus 插入数据条数：{result.get('insert_count', 0)}")
    return result

def delete_from_item_name_collection(file_title: str):
    try:
        # 幂等性处理：删除同名商品数据（避免重复存储）
        # 转义商品名称（防止特殊字符导致filter解析失败）
        safe_file_title = escape_milvus_string(file_title)
        # 构建过滤表达式：item_name等于目标值
        result = get_milvus_client().delete(collection_name=milvus_config.item_name_collection, filter=f'file_title=="{safe_file_title}"')
        logger.debug("删除结果", result.get('delete_count', 0))
        return result
    except Exception as e:
        logger.error(f"Milvus 数据删除失败: {str(e)}")
        raise MilvusError(f"Milvus 数据删除失败: {str(e)}")

# chunks 集合操作
def create_chunks_collection(vector_dimension):
    milvus_client = get_milvus_client()
    # 集合不存在则创建
    collection_name = milvus_config.chunks_collection
    if milvus_client.has_collection(collection_name):
        logger.warning(f"Milvus 集合 {collection_name} 已存在，跳过创建")
        return
    
    # 1. 创建schema
    schema = milvus_client.create_schema(auto_id=True, enable_dynamic_field=True)
    # 2. 创建列
    schema.add_field(field_name="chunk_id", datatype=DataType.INT64, is_primary=True, auto_id=True)
    schema.add_field(field_name="content", datatype=DataType.VARCHAR, max_length=65535)  # 切片内容
    schema.add_field(field_name="title", datatype=DataType.VARCHAR, max_length=100)  # 切片标题
    schema.add_field(field_name="parent_title", datatype=DataType.VARCHAR, max_length=100)  # 父标题
    schema.add_field(field_name="part", datatype=DataType.INT8)  # 分片编号
    schema.add_field(field_name="file_title", datatype=DataType.VARCHAR, max_length=100)  # 源文件标题
    schema.add_field(field_name="item_name", datatype=DataType.VARCHAR, max_length=100)  # 商品名称（幂等性依据）
    schema.add_field(field_name="sparse_vector", datatype=DataType.SPARSE_FLOAT_VECTOR)  # 稀疏向量
    schema.add_field(field_name="dense_vector", datatype=DataType.FLOAT_VECTOR, dim=vector_dimension)  # 稠密向量

    # 3. 创建索引
    index_params = milvus_client.prepare_index_params()
    # 稠密向量索引：AUTOINDEX自动选最优索引类型+余弦相似度（语义检索常用）
    index_params.add_index(
        field_name="dense_vector",
        index_name="dense_vector_index",
        index_type="AUTOINDEX",
        metric_type="COSINE"
    )
    # 稀疏向量索引：专用SPARSE_INVERTED_INDEX+内积（IP），适配稀疏向量检索
    index_params.add_index(
        field_name="sparse_vector",
        index_name="sparse_inverted_index",
        index_type="SPARSE_INVERTED_INDEX",
        metric_type="IP",
        params={"inverted_index_algo": "DAAT_MAXSCORE", "normalize": True, "quantization": "none"}
    )

    # 创建集合
    milvus_client.create_collection(
        collection_name=collection_name,
        schema=schema,
        index_params=index_params
    )

def delete_from_chunks_collection(file_title: str):
    try:
        file_title = escape_milvus_string(file_title)
        result = get_milvus_client().delete(collection_name=milvus_config.chunks_collection, filter=f"file_title=='{file_title}'")
        logger.debug("删除结果", result.get('delete_count', 0))
        return result
    except Exception as e:
        logger.error(f"Milvus 数据删除失败: {str(e)}")
        raise MilvusError(f"Milvus 数据删除失败: {str(e)}")
    
def insert_into_chunks_collection(data: List[Dict]):
    result = get_milvus_client().insert(collection_name=milvus_config.chunks_collection, data=data)
    logger.info(f"Milvus 插入数据条数：{result.get('insert_count', 0)}")
    return result

# 搜索操作
def create_hybrid_search_requests(dense_vector, sparse_vector, dense_params=None, sparse_params=None, expr=None, limit=5):
    """
    构建Milvus混合搜索请求对象
    分别创建稠密/稀疏向量的搜索请求，用于后续混合搜索融合
    :param dense_vector: 文本生成的稠密向量
    :param sparse_vector: 文本生成的稀疏向量
    :param dense_params: 稠密向量搜索参数，默认使用余弦相似度
    :param sparse_params: 稀疏向量搜索参数，默认使用内积相似度
    :param expr: 搜索过滤表达式，用于精准筛选数据
    :param limit: 单向量搜索返回结果数量，默认5
    :return: 搜索请求列表，包含[dense_req, sparse_req]
    """
    # 稠密向量默认搜索参数：余弦相似度（COSINE），适配BGE-M3稠密向量
    if dense_params is None:
        dense_params = {"metric_type": "COSINE"}
    # 稀疏向量默认搜索参数：内积（IP），适配BGE-M3稀疏向量
    if sparse_params is None:
        sparse_params = {"metric_type": "IP"}

    # 构建稠密向量搜索请求，关联Milvus的dense_vector字段 近似最近邻（ANN）检索请求的核心类
    dense_req = AnnSearchRequest(
        data=[dense_vector],
        anns_field="dense_vector",
        param=dense_params,
        expr=expr,
        limit=limit
    )
    # 构建稀疏向量搜索请求，关联Milvus的sparse_vector字段
    sparse_req = AnnSearchRequest(
        data=[sparse_vector],
        anns_field="sparse_vector",
        param=sparse_params,
        expr=expr,
        limit=limit
    )
    return [dense_req, sparse_req]

def hybrid_search(collection_name, reqs, ranker_weights=(0.5, 0.5), norm_score=False, limit=5,
                  output_fields=None, search_params=None):
    """
    执行Milvus稠密+稀疏向量混合搜索
    基于WeightedRanker实现双向量搜索结果加权融合，提升检索准确性
    :param client: MilvusClient实例
    :param collection_name: 集合名称
    :param reqs: 搜索请求列表，固定为[dense_req, sparse_req]
    :param ranker_weights: 加权融合权重，默认(0.5,0.5)，依次对应稠密/稀疏向量
    :param norm_score: 是否归一化评分后再融合，避免评分量级差异导致权重失效
    :param limit: 混合搜索最终返回结果数量，默认5
    :param output_fields: 需要返回的字段列表，默认返回item_name
    :param search_params: 搜索参数，如ef/topk等，默认None
    :return: 混合搜索结果列表，搜索失败返回None
    """
    try:
        # 初始化加权排名器：按权重融合稠密/稀疏向量的搜索结果
        # norm_score=True：先将两个向量评分归一化到0~1区间，再加权计算，避免一个得分特别大、另一个特别小导致权重失效。
        # 版本：V2.4
        rerank = WeightedRanker(ranker_weights[0], ranker_weights[1], norm_score=norm_score)
        # 默认返回字段：文档标识字段
        if output_fields is None:
            output_fields = ["item_name"]

        # 执行混合搜索：融合稠密+稀疏向量结果，按权重重新排序
        res = get_milvus_client().hybrid_search(
            collection_name=collection_name,
            reqs=reqs,
            ranker=rerank,
            limit=limit,
            output_fields=output_fields,
            search_params=search_params
        )
        logger.info(f"Milvus混合搜索完成，集合[{collection_name}]共检索到{len(res[0])}条结果")
        return res
    except Exception as e:
        logger.error(f"Milvus混合搜索执行失败，集合[{collection_name}]：{str(e)}", exc_info=True)
        return None

if __name__ == '__main__':
    from app.utils.embedding_utils import generate_embeddings
    item_names = ["烫金机", "电脑"]
    embeddings = generate_embeddings(item_names)

    # 6、遍历每个商品名称，逐个执行向量搜索（保证结果与原始商品名一一对应）
    for i in range(len(item_names)):
        # 从批量生成的向量结果中，取出当前商品名对应的稠密向量（高维连续值，如[0.12, 0.35,...]）
        dense_vector = embeddings.get("dense")[i]
        # 从批量生成的向量结果中，取出当前商品名对应的稀疏向量（键值对，如{100:0.747, 205:0.664}）
        sparse_vector = embeddings.get("sparse")[i]

        # 构造Milvus混合搜索请求对象，传入稠/稀疏向量，指定返回Top5匹配结果
        # reqs返回格式：[稠密向量搜索请求, 稀疏向量搜索请求]
        reqs = create_hybrid_search_requests(
            dense_vector=dense_vector,
            sparse_vector=sparse_vector,
            limit=5
        )

        # 执行BGEM3混合向量搜索，获取数据库中的匹配结果和评分
        # 默认配置：稠/稀疏向量权重各0.8/0.2，开启评分归一化（将距离值转为0-1相似度评分）
        search_res = hybrid_search(
            collection_name=milvus_config.item_name_collection,  # 目标向量集合名（存储商品向量的表）
            reqs=reqs,  # 混合搜索请求对象列表
            ranker_weights=(0.8, 0.2),  # 稠/稀疏向量评分权重配比（和为1最佳）
            limit=5,  # 最终返回Top5匹配结果
            norm_score=True,  # 开启评分归一化，统一评分量级为0-1
            output_fields=["item_name"]  # 指定返回Milvus中存储的商品名字段（业务字段）
        )

"""
(knowledge-base) PS D:\knowledge-base> python -m app.utils.milvus_utils
2026-07-17 11:23:58,727 [WARNING][__init__]: Using fp16 with CPU can lead to runtime errors such as 'LayerNormKernelImpl', It's recommended to set 'use_fp16 = False' when using cpu.  (bge_m3.py:50)
Loading weights: 100%|█████████████████████████████████████████████████████████████████████████████████████████████████████████████████████████████████| 391/391 [00:00<00:00, 1204.39it/s]
2026-07-17 11:24:03.134 | INFO     | __main__:hybrid_search:260 - Milvus混合搜索完成，集合[kb_item_names]共检索到5条结果
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
            "pk": 467684978484127378,
            "distance": 0.5373769402503967,
            "entity": {
                "item_name": "AolynkCB304n网桥"
            }
        }
    ]
]
"""