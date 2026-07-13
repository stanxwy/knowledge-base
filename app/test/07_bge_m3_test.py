from rich import print as rprint
from app.utils.embedding_utils import get_bge_m3_ef

# 加载BGE-M3模型单例
model = get_bge_m3_ef()

# 模型编码生成向量，返回dense（稠密向量）+sparse（CSR格式稀疏向量）
texts = ["测试","hello"]
embeddings = model.encode_documents(texts)

print("获取成功！")
rprint(embeddings)

# 稠密向量获取
dense_obj = embeddings["dense"]
dense_list = [emb.tolist() for emb in dense_obj]
rprint(len(dense_list), len(dense_list[0]))

# 稀疏向量获取：解析为字典格式（适配序列化/存储）
sparse_obj = embeddings["sparse"]
processed_sparse = []
for i in range(len(texts)):

    # 提取第i个文本的稀疏向量索引
    sparse_indices = sparse_obj.indices[
        sparse_obj.indptr[i]:sparse_obj.indptr[i + 1]
    ].tolist()

    # 提取第i个文本的稀疏向量权重
    sparse_data = sparse_obj.data[
        sparse_obj.indptr[i]:sparse_obj.indptr[i + 1]
    ].tolist()

    # 构造{特征索引: 归一化权重}的稀疏向量字典
    # 把两个列表“打包”成一个字典（Milvus 数据库的要求）
    sparse_dict = {k: v for k, v in zip(sparse_indices, sparse_data)}
    processed_sparse.append(sparse_dict)

    #sparse_indices = [0, 5, 23, 156]    # 特征在词汇表中的位置编号
    #sparse_data = [0.8, 0.3, 0.9, 0.2]  # 每个特征的权重
    # zip 后生成：[(0, 0.8), (5, 0.3), (23, 0.9), (156, 0.2)]
    #              ↑   ↑
    #            索引 权重
# 数据结构：
# 稠密向量：这是一个包含两个 array 的列表。每个 array 长度为 1024，数据类型是 float16（半精度）。
# 稀疏向量：这是一个 Compressed Sparse Row sparse array（压缩稀疏行矩阵），形状是 (2, 250002)，250002 代表模型词汇表的大小（大约有 25 万个可能的词），2表示当前是2个词的向量
rprint(processed_sparse)

"""
(knowledge-base) PS D:\knowledge-base> python -m app.test.07_bge_m3_test
config loaded True...
2026-07-13 14:22:01,407 [WARNING][__init__]: Using fp16 with CPU can lead to runtime errors such as 'LayerNormKernelImpl', It's recommended to set 'use_fp16 = False' when using cpu.  (bge_m3.py:50)
Loading weights: 100%|█████████████████████████████████████████████████████████████████████████████████████████████| 391/391 [00:00<00:00, 1738.02it/s]
2026-07-13 14:22:04 - FlagEmbedding.finetune.embedder.encoder_only.m3.runner - INFO - loading existing colbert_linear and sparse_linear---------
获取成功！
{
    'dense': [
        array([-0.02734504,  0.01174424, -0.0349596 , ..., -0.01917966,
       -0.03857379,  0.02639256], shape=(1024,), dtype=float32),
        array([-0.03202488,  0.02325127, -0.04159372, ...,  0.01847975,
       -0.03722385,  0.05963241], shape=(1024,), dtype=float32)
    ],
    'sparse': <Compressed Sparse Row sparse array of dtype 'float64'
        with 4 stored elements and shape (2, 250002)>
}
2 1024
[{6: 0.06369282305240631, 49125: 0.3608279526233673}, {31: 0.2433895766735077, 33600: 0.25838327407836914}]
"""