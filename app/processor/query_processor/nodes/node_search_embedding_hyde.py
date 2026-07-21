from app.processor.query_processor.base import NodeBase
from app.processor.query_processor.state import QueryGraphState

from app.utils.json_format_utils import format_json
from app.utils.llm_utils import generate_hyde_doc
from app.services.vectordb_service import ChunksVectorDBService, get_chunks_vector_db

class NodeSearchEmbeddingHyde(NodeBase):
    """
    节点功能：HyDE (Hypothetical Document Embedding)
    先让 LLM 生成假设性答案，再对答案进行向量检索，提高召回率。
    """
    name: str = "node_search_embedding_hyde"

    def __init__(self, chunks_vector_db: ChunksVectorDBService = get_chunks_vector_db()):
        super().__init__()
        self._chunks_vector_db = chunks_vector_db

    def _step_1_create_hyde_doc(self, rewritten_query: str) -> str:
        """
        阶段1：利用大模型根据用户查询生成假设性文档（Hypothetical Document）。
        HyDE的核心在于：利用LLM生成一个“虚构但相关”的文档，用该文档的向量去检索真实的文档，
        从而缓解短查询（Query）与长文档（Document）在语义空间不匹配的问题。

        :param rewritten_query: 用户改写后的查询语句
        :return: LLM生成的假设性文档内容
        """
        self.logger.info("步骤1: 开始生成假设性文档")
        return generate_hyde_doc(rewritten_query)
    
    def _step_2_search_embedding_hyde(self, rewritten_query: str, hyde_doc: str, item_names=None):
        """
        阶段2：利用“重写问题 + 假设性文档”生成 embedding，并到向量库检索切片。

        :param rewritten_query: 改写后的查询
        :param hyde_doc: Step 1 生成的假设性文档
        :param item_names: 商品名称列表，用于元数据过滤 (item_name in [...])
        :return: 检索结果列表
        """
        self.logger.info("步骤2: 开始执行 Milvus 混合检索...")
        combined_text = rewritten_query + " " + hyde_doc
        return self._chunks_vector_db.hybrid_search_chunks(combined_text, item_names)

    def process(self, state: QueryGraphState) -> QueryGraphState:
        """
        HyDE (Hypothetical Document Embedding) 检索节点
        核心思想：通过LLM生成假设性答案（HyDE文档），将其向量化后用于检索，以解决短查询语义稀疏问题。

        执行步骤：
        1. 参数提取：从会话状态中获取改写后的查询（rewritten_query）和已确认的商品名（item_names）。
        2. 生成假设文档 (Step 1)：调用LLM，基于用户问题生成一段假设性的理想回答（即HyDE文档）。
        3. 混合检索 (Step 2)：
           - 将“用户问题 + 假设文档”合并，生成BGE-M3稠密+稀疏向量。
           - 在Milvus中执行混合检索（带商品名过滤），召回最相似的知识切片。
        4. 结果封装：返回检索到的切片列表和生成的假设文档，更新会话状态。

        :param state: 会话状态字典，包含 rewritten_query, item_names 等
        :return: 包含 hyde_embedding_chunks (检索结果) 和 hyde_doc (假设文档) 的字典
        """
        # 1、用户问题和已确认商品名
        rewritten_query = state.get("rewritten_query")
        item_names = state.get("item_names")

        try:
            # 2、生成假设性文档
            hyde_doc = self._step_1_create_hyde_doc(rewritten_query)

            # 3、用“重写问题 + 假设文档”检索切片
            res = self._step_2_search_embedding_hyde(rewritten_query, hyde_doc, item_names)

            # 4、结果封装
            return {
                "hyde_embedding_chunks": res,
                "hyde_doc": hyde_doc,
            }
        except Exception as e:
            self.logger.exception(f"假设性文档向量搜索失败: {e}")
            return {}
    
if __name__ == "__main__":
    from app.utils.logger import setup_logging
    logger = setup_logging()
    init_state = {
        "rewritten_query": "关于brother HAK180烫金机，如何调节转印温度？",
        "item_names": ["BrotherHAK180烫金机", "BrotherHAK-180烫金机", "HAK180烫金机"]
    }
    node_search_embedding_hyde = NodeSearchEmbeddingHyde()
    result = node_search_embedding_hyde(init_state)
    logger.info(format_json(result, indent=4))

"""
(knowledge-base) PS D:\knowledge-base> python -m app.processor.query_processor.nodes.node_search_embedding_hyde
2026-07-18 09:51:38 - root - INFO - 日志系统初始化完成，日志文件: ./logs\knowledge_base.log
2026-07-18 09:51:38 - import.node_search_embedding_hyde - INFO - --- node_search_embedding_hyde 开始啦 ---
2026-07-18 09:51:38 - import.node_search_embedding_hyde - INFO - 步骤1: 开始生成假设性文档
2026-07-18 09:51:39 - root - INFO - LangChain ChatOpenAI ('qwen-flash', False) 客户端实例获取成功...
2026-07-18 09:51:41 - httpx - INFO - HTTP Request: POST https://ws-xfsvflr5yndg90oh.cn-beijing.maas.aliyuncs.com/compatible-mode/v1/chat/completions "HTTP/1.1 200 OK"
2026-07-18 09:51:41 - root - INFO - 生成假设文档响应：content='Brother HAK180烫金机的转印温度调节需通过控制面板进行设定。首先，开启设备并预热至工作温度（建议初始设置为160°C–180°C）。在操作界面选择“温度设置”菜单，使用上下键精确调整目标温度，单位为℃。根据所用烫金箔材质特性，调整至推荐温度范围：普通亮面箔为170°C，哑光或特殊涂层箔可调至160°C–175°C。温度设定后，等待加热指示灯熄灭，表示达到稳定温度。实际应用中，建议先进行试烫，依据烫印效果微调温度。避免过高温度导致烫金箔碳化或基材损伤，过低则造成附着力不足。调节完成后，保持温度稳定，确保连续作业质量一致。' additional_kwargs={'refusal': None} response_metadata={'token_usage': {'completion_tokens': 182, 'prompt_tokens': 113, 'total_tokens': 295, 'completion_tokens_details': None, 'prompt_tokens_details': {'audio_tokens': None, 'cache_write_tokens': None, 'cached_tokens': 0}}, 'model_provider': 'openai', 'model_name': 'qwen-flash', 'system_fingerprint': None, 'id': 'chatcmpl-5d3f6a6b-975a-9608-9f97-84327136dc22', 'finish_reason': 'stop', 'logprobs': None} id='lc_run--019f72ec-0ab7-7102-bcf4-843e6f0a3429-0' tool_calls=[] invalid_tool_calls=[] usage_metadata={'input_tokens': 113, 'output_tokens': 182, 'total_tokens': 295, 'input_token_details': {'cache_read': 0}, 'output_token_details': {}}
2026-07-18 09:51:43,695 [WARNING][__init__]: Using fp16 with CPU can lead to runtime errors such as 'LayerNormKernelImpl', It's recommended to set 'use_fp16 = False' when using cpu.  (bge_m3.py:50)
Loading weights: 100%|██████████████████████████████████████████████████████████████████████████████████████████████████████████████████████████████████| 391/391 [00:00<00:00, 638.51it/s]
2026-07-18 09:51:47 - FlagEmbedding.finetune.embedder.encoder_only.m3.runner - INFO - loading existing colbert_linear and sparse_linear---------
2026-07-18 09:51:49 - import.node_search_embedding_hyde - INFO - 步骤2: 过滤条件: item_name in ['BrotherHAK180烫金机', 'BrotherHAK-180烫金机', 'HAK180烫金机']
2026-07-18 09:51:49 - import.node_search_embedding_hyde - INFO - 步骤2: 开始执行 Milvus 混合检索...
2026-07-18 09:51:49.840 | INFO     | app.utils.milvus_utils:hybrid_search:258 - Milvus混合搜索完成，集合[kb_chunks]共检索到5条结果
2026-07-18 09:51:49 - import.node_search_embedding_hyde - INFO - --- node_search_embedding_hyde 完成啦 ---
2026-07-18 09:51:49 - root - INFO - {
    "hyde_embedding_chunks": [
        {
            "chunk_id": 467672046675989611,
            "distance": 0.8116987943649292,
            "entity": {
                "chunk_id": 467672046675989611,
                "content": "![](images/677a08ee041965bbbdb6b483d6c17d5aaa36a26b6dc96870a2019f0307b8616f.jpg)  \nD01WD7001-00\n\nSCHN\n\n\n## HAK 180 烫金机\n\n产品安全手册（简体中文）\n\n感谢您购买 HAK 180 烫金机。\n\n在使用本设备之前，请先阅读本手册，包括所有预防措施。阅读本手册后，请妥善保管。\n\n有关使用本设备的更多信息，请参阅使用说明书，其可在兄弟 (中国)商业有限公司技术服务支持网站 http://www.95105369.com/Web/Manuals.aspx 上找到。建议您先通读使用说明书，再使用本设备。\n\n如需获得常见问题解答、故障排除和说明书，请访问\n\nhttp://www.95105369.com。\n\n对于本设备所有者不遵守本指南中规定的说明操作而导致的损害，Brother 不承担任何责任。\n\n•\t对于保养、调整或维修事宜，请联系 Brother 呼叫中心或您当地的Brother 经销商。\n\n•\t如果本设备工作不正常或发生任何错误，请关闭本设备，拔下所有电缆，然后联系 Brother 呼叫中心或您当地的 Brother 经销商。\n\n•\t本文档中提供的信息可能会随时更改，恕不另行通知。\n\n•\t严禁未经授权擅自复制或重制本文档的任何部分或全部内容。\n\n•\t请注意，对于使用通过本设备制作的产品造成的任何损坏或利润损失，或者故障、维修导致的数据消失或更改，或者第三方提出的任何索赔，我们不承担任何责任。\n",
                "item_name": "HAK180烫金机"
            }
        },
        {
            "chunk_id": 467672046675989612,
            "distance": 0.8088580965995789,
            "entity": {
                "chunk_id": 467672046675989612,
                "content": "## 警告\n\n不遵守说明和警告可能导致人员死亡或严重受伤。遵守这些指引以避免冒烟、发热、爆炸、火灾或人员受伤的风险。\n\n\n## 设备\n\n•\t请先阅读这本手册，再尝试操作本设备或尝试进行任何维护。不按照这些说明操作可能会提高发生人员受伤或财产损坏（包括火灾、触电、烧伤或窒息所致）的风险。对于本设备所有者不遵守本指南中规定的说明操作而导致的损害，Brother 不承担任何责任。\n\n•\t请勿在未去除所有包装材料的情况下使用本设备，包括本设备内部的任何附加的包装材料。否则可能会产生火灾的风险。\n\n•\t请勿拆解本设备。拆解本设备可能会导致火灾或触电。\n\n•\t请勿尝试自行维修本设备。打开或拆下盖子可能使您接触到危险电压点以及带来其他风险，并且可能使您的保修失效。对于所有维修事宜，请联系 Brother 呼叫中心或您当地的 Brother 经销商。\n\n•\t请在以下环境使用本设备：温度保持在 10 °C 和 32 °C 之间，湿度保持在 20% 和 80% 之间，无冷凝。\n\n•\t请勿使本设备受到阳光直射、过热、接触明火、腐蚀性气体、湿气或灰尘。否则可能产生触电、短路或火灾的风险，从而导致损坏设备和/或导致设备无法运行。\n\n•\t请勿将设备放在加热器、空调、电风扇或水附近。\n\n否则当水（包括加热 空调 通风设备所产生的冷凝水）接触本设备时可能产生短路或火灾的风险。\n\n•\t如果设备变得异常高温、冒烟、产生任何强烈味道，或者如果您意外在设备上倒入任何液体，请立即从电源插座拔掉设备的插头。请联系 Brother 呼叫中心或您当地的 Brother 经销商。\n\n如果设备跌落或者已损坏，则有触电的可能性。请从电源插座中拔掉设备的插头，然后联系 呼叫中心或您当地的 经销商。\n\n•\t如果水、其他液体或金属物体进入设备内部，请立即从电源插座中拔掉设备的插头，然后联系 Brother 呼叫中心或您当地的 Brother经销商。\n\n•\t请勿在卡纸或有纸张散落在设备内部的情况下尝试使用本设备。纸张与定影单元长时间接触可能导致火灾。\n\n请勿使用任何易燃物品、任何类型的喷雾剂包含酒精或氨水的有机溶剂/液体来清洁本设备的内部或外部。否则可能导致火灾。请改用无绒干抹布。有关如何清洁本设备的说明，请参阅 。\n\n•\t请勿将本设备放在化学品附近，或者将本设备放置在可能会泼溅到化学品的位置。万一化学品接触本设备，则存在火灾或触电的风险。特别是有机溶剂或液体（如苯、油漆稀释剂、抛光剂或除臭剂）可能导致塑料盖和/或电缆溶解或分解，从而产生火灾或触电的风险。这些化学品或其他化学品可能导致本设备故障或褪色。\n\n•\t本设备的包装中使用了塑料袋。塑料袋并不是玩具。为避免窒息的危险，请将这些塑料袋远离婴儿和儿童，并正确弃置这些塑料袋。\n\n•\t对于使用起搏器的用户：\n\n本设备可能会产生弱磁场。如果您在本设备附近感觉到起搏器工作不正常，请远离本设备，并立即咨询医生。\n\n•\t使用本设备之后短时间内，本设备的一些内部零件仍然处于极热状态。打开前盖时，请勿触摸以灰色标记的区域。存在烧伤的风险。先等待设备冷却下来，再触摸设备的内部零件。\n\n![](images/f3349cded08d6686a93d0a81b9a64ec1e50d9a82cbb88541b37027f085813a15.jpg)  \n儎⑟ഴḽ䆜઀ᛞ࠽व䀜᪮儎⑟Ⲻ䇴༽䜞ԬȾ\n\n![](images/501bb8d2d681e4502d87badb15a68939eadfa086d309c3599f1c36b0bc559177.jpg)\n",
                "item_name": "HAK180烫金机"
            }
        },
        {
            "chunk_id": 467672046675989615,
            "distance": 0.8022468686103821,
            "entity": {
                "chunk_id": 467672046675989615,
                "content": "## 设备\n\n如果遵守了操作说明进行操作，但是设备不能正确运行，请仅调整操作说明中涵盖的控制。错误调整其他控制可能导致损坏并且通常需要合格技术进行全面工作以将本设备恢复到正常操作。Brother不建议使用 Brother 正品烫金膜盒以外的其他品牌烫金膜盒。如果使用与本设备不兼容的耗材导致损坏本设备的任何零件，由此导致的任何维修可能不在保修范围内。\n\n\n## 电源线\n\n请勿将设备连接到受墙壁开关或自动计时器控制的电源插座，或者与大型设备或需要大量电力的其他设备连接到同一个电路中。否则可能会损坏电源。电源损坏还可能会从本设备的内存中删除信息，并且反复打开/关闭电源可能会损坏本设备。\n\n\n## 警告标签\n\n请勿撕下或损坏设备上的任何注意/ 警告标签以及序列号标签。\n\n\n## 设备保修和责任\n\n本手册中的任何内容都将不会影响现有设备保修，也不应被视为授予任何其他设备保修。不遵循本手册中的安全说明可能导致本设备的保修失效。\n\n\n## 设备和电源线\n\n•\t请仅使用本设备随附的电源线。\n\n•\t不要在本设备周围放置任何物体。在紧急情况下，此类物体会阻碍接近电源插座。必须保证在需要时可以拔出设备的插头。\n\n•\t请遵守所有适用法规来处理本设备。\n",
                "item_name": "HAK180烫金机"
            }
        },
        {
            "chunk_id": 467672046675989613,
            "distance": 0.7914022207260132,
            "entity": {
                "chunk_id": 467672046675989613,
                "content": "## 电源线\n\n•\t本设备通过 AC 220 V-240 V 50/60 Hz 电源供电。\n\n请勿将本设备连接到直流电源或逆变器（直流交流变换器）。存在火灾或触电的风险。\n\n•\t请勿用湿手触摸插头。这样可能导致触电。如果不确定您拥有哪种类型的电源，请联系合格的电工。\n\n•\t始终确保插头已完全插入。如果电源线磨损或损坏，请勿使用设备或用手触摸电源线。\n\n•\t设备内部有高压电极。\n\n先拔掉电源线，再清洁设备内部。拔出电源线时，不要拉电线，而是捏住插头往外拔。存在发生火灾、触电或设备故障的风险。\n\n•\t请勿将任何物体压在电源线上。\n\n•\t请勿将本设备放在人们可能踏过电源线的位置。\n\n•\t请勿将本设备放置在会使得拉伸或拉紧电源线的位置，否则电源线可能会磨损或损坏。\n\n•\t始终确保插头已完全插入。如果电源线磨损或损坏，请勿使用设备或用手触摸电源线。如果拔出设备的电源插头，请勿触摸损坏 磨损的部分。\n\n•\t请勿让设备压在电源线上。\n\n•\t请勿在雷暴天气期间使用本设备。存在闪电导致触电的潜在风险。\n\n•\t请勿使用任何非指定的电缆。否则可能导致火灾或人员受伤。必须按照 正确安装。\n\n•\t请勿让任何金属硬件或任何类型的液体落在设备的电源插头上。否则可能导致触电或火灾。\n\n•\tBrother 强烈建议您不要使用任何类型的延长线。\n\n•\t定期拔出电源插头进行清洁。使用干布清洁插头插脚根部以及插脚之间的位置。如果电源插头长时间插入在电源插座中，灰尘会堆积在插头插脚周围，这可能会导致短路，从而引起火灾。\n\n•\t本设备装有接地的插头。此插头只能插入接地的电源插座中。这是一项安全功能。如果您无法将插头插入到插座中，请让电工更换过时的插座。请勿试图破坏接地插头的作用。\n\n不遵守说明和警告可能导致人员中度或严重受伤。遵守这些指引以避免人员受伤。\n",
                "item_name": "HAK180烫金机"
            }
        },
        {
            "chunk_id": 467672046675989614,
            "distance": 0.7814245223999023,
            "entity": {
                "chunk_id": 467672046675989614,
                "content": "## 设备\n\n•\t将本设备放置在平整、水平且稳定的表面上（如桌面），避免震动和冲击。\n\n•\t将本设备放置在通风良好的环境中。\n\n•\t为了防止人员受伤，请谨慎操作，避免将手指放置在图中所示的区域中。\n\n![](images/c61a7f4e923881679f747508ae309c39dc221685344b068009256b1b3a40cc00.jpg)\n\n![](images/5067b2891ca4f761e2874921e0eb433aa742afbf38ca8dc509afecbf0aa6a6b5.jpg)\n\n\n## 电源线\n\n•\t如果您长时间不会使用本设备，请从电源插座中拔掉电源线以确保安全。\n\n•\t本设备必须安装在可轻松使用电源插座的位置附近。如果发生意外情况，必须从电源插座中拔掉电源线以完全关闭电源。\n\n•\t请勿将手放在纸张边缘。纸张锋利的边缘可能导致受伤。\n\n\n## 为设备选择一个安全的位置\n\n•\t提起本设备时，请使用双手抓稳本设备的两侧。如果抓住的是进纸托板和出纸盒，它们可能会掉下来。必须通过将双手放在本设备下面来搬运本设备。\n\n![](images/cc5ee1ac24ebb2707d40dc7a234a8b243f55f5bf08fabc683859be6fdf096ffa.jpg)  \n确保本设备的任何部位均未伸出设备所在的桌面或支架。特别是当本设备位于桌面、支架等边缘时，请勿让出纸盒打开。确保本设备位于平整、水平且稳定的表面上，避免震动。不遵守这些预防措施可能导致设备跌落，从而导致用户的人身伤害以及设备严重损坏。\n\n![](images/8e839864036a7326885565163d99117ea943ecd29a656c85e7aa4052a9b9d28d.jpg)\n\n“重要事项”表示可能导致财产损失或本设备功能丧失的潜在危险情况。\n",
                "item_name": "HAK180烫金机"
            }
        }
    ],
    "hyde_doc": "Brother HAK180烫金机的转印温度调节需通过控制面板进行设定。首先，开启设备并预热至工作温度（建议初始设置为160°C–180°C）。在操作界面选择“温度设置”菜单，使用上下键精确调整目标温度，单位为℃。根据所用烫金箔材质特性，调整至推荐温度范围：普通亮面箔为170°C，哑光或特殊涂层箔可调至160°C–175°C。温度设定后，等待加热指示灯熄灭，表示达到稳定温度。实际应用中，建议先进行试烫，依据烫印效果微调温度。避免过高温度导致烫金箔碳化或基材损伤，过低则造成附着力不足。调节完成后，保持温度稳定，确保连续作业质量一致。"
}
"""