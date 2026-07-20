from typing import List, Tuple
from app.processor.query_processor.base import NodeBase
from app.processor.query_processor.state import QueryGraphState
from app.utils.json_format_utils import format_json
from app.utils.llm_utils import resolve_item_name_and_rewrite_query
from app.utils.milvus_utils import hybrid_search_item_name
from app.utils.mongo_history_utils import get_recent_messages, save_chat_message, update_message_item_names

class NodeItemNameConfirm(NodeBase):
    """
    节点功能：确认用户问题中的核心商品名称。
    """
    name: str = "node_item_name_confirm"

    def _step_1_validate_input_state(self, state: QueryGraphState) -> Tuple[str, str]:
        session_id = state.get("session_id") 
        if not session_id:
            raise ValueError("核心参数session_id缺失")

        original_query = state.get("original_query")
        if not original_query:
            raise ValueError("核心参数original_query缺失")

        return session_id, original_query
    
    def _step_6_align_item_names(self, query_results) -> dict:
        """
        6 根据Milvus搜索评分，逐个对齐step4提取的item_names，生成「确认商品名」和「候选商品名」
        对齐规则（优先级a>b>c>d）：
                a  如果只有一个匹配结果评分高于0.85 → 直接确认该商品名
                b  如果多条匹配结果评分超过0.85 → 优先取与原始提取名相同的，无则取分数最高的
                c  如果无0.85分以上结果 → 取分数≥0.6的最高前5个作为候选
                d  如果无0.6分及以上结果 → 不返回任何商品名（确认+候选均为空）
        :param query_results: 列表[字典] - step5的返回结果，每个商品名的搜索匹配数据（格式同step5返回值）
        :return: 字典 - 商品名对齐结果，包含确认列表和候选列表，格式：
                 {
                     "confirmed_item_names": ["确认商品名1", "确认商品名2"],  # 去重后的确认商品名，无则空列表
                     "options": ["候选商品名1", "候选商品名2", ...]          # 去重后的候选商品名，无则空列表
                 }
        """
        # 1、初始化确认商品名列表（符合高置信度规则的商品名）
        confirmed_item_names: List[str] = []
        # 2、初始化候选商品名列表（低置信度，需用户确认的商品名）
        options: List[str] = []

        for res in query_results:
            # 提取原始的数据，商品名和匹配结果
            extracted_name = (res.get("extracted_name", "") or  "").strip()
            # 获取匹配的商品名，无就获取空列表
            matches = res.get("matches", []) or []
            # 若无匹配结果，直接跳过当前商品名的对齐
            if not matches:
                continue

            # 筛选高置信度匹配结果：评分>0.85
            high = [m for m in matches if m.get("score", 0) > 0.85]
            # 筛选中置信度匹配结果：评分≥0.6（仅高置信度为空时生效）
            mid = [m for m in matches if m.get("score", 0) >= 0.6]

            # 优化 ab 所有评分高于0.85的都可以直接确认
            if len(high) > 0:
                self.logger.info(f"LLM商品识别“{extracted_name}”检索到 {len(high)} 个高置信度的结果，{high}")
                for m in high:
                    confirmed_item_names.append(m.get("item_name"))
                continue
            # 筛选高置信度得分的结果： >= 0.65
            # # a  如果只有一个匹配结果评分高于0.85 → 直接确认该商品名
            # if len(high) == 1:
            #     confirmed_item_names.append(high[0].get("item_name"))
            #     continue
            #
            # # b  如果多条匹配结果评分超过0.85 → 优先取与原始提取名相同的，无则取分数最高的
            # if len(high) > 1:
            #     picked = None
            #     if extracted_name:
            #
            #         # 优先取与原始提取名相同的
            #         for m in high:
            #             if m.get("item_name") == extracted_name:
            #                 picked = m
            #                 break
            #
            #     if not picked:
            #         # 无则取分数最高的
            #         picked = high[0]
            #
            #     confirmed_item_names.append(picked.get("item_name"))
            #     continue

            # 规则c: 无0.85分以上结果，取≥0.6分的最高前3个作为候选
            # 注：高置信度列表high为空时才会走到此处（规则a/b均不满足）
            if len(mid) > 0:
                self.logger.info(f"LLM商品识别“{extracted_name}”检索到 {len(mid)} 个中置信度的结果，{mid}")
                # 取中置信度结果的前5个，加入候选列表
                for m in mid[:3]:
                    options.append(m.get("item_name"))

            # 规则d: 无0.6分及以上结果 → 不做任何操作，确认+候选列表均为空
        # 返回最终对齐结果：确认列表和候选列表均做去重处理（list(set())）
        return list(set(confirmed_item_names)), list(set(options))  # 去重，避免重复候选
    
    def _step_7_check_confirmation(self, confirmed, options, history):
        """
        7 检查step6对齐后的商品名状态，分3种分支更新state，并同步更新历史消息的商品名关联
        :param state: 字典 - 原始会话状态，包含session_id/original_query等核心字段
        :param align_result: 字典 - step6的对齐结果
        :param history: 列表[字典] - 近期会话历史
        :return: 字典 - 更新后的会话状态，包含item_names/answer
        """

        # 分支A：有确认的商品名（高置信度，无需用户确认）
        if confirmed:
            # 收集历史消息中未关联商品名的消息ID（需批量更新关联）
            ids_to_update = []
            for msg in history:
                if not msg.get("item_names"):  # 仅更新item_names为空的历史消息
                    mid = msg.get("_id")  # 提取消息唯一ID
                    if mid:
                        ids_to_update.append(str(mid))  # 转为字符串，避免ID格式问题

            # 若存在需更新的消息ID，批量更新历史消息的商品名关联
            if ids_to_update:
                update_message_item_names(ids_to_update, confirmed)

            # 更新会话状态：设置确认商品名、改写后的查询
            # 返回更新后的状态
            return confirmed, ""

        # 分支B：无确认商品名，但有候选商品名（中置信度，需用户明确）
        if options:
            # 候选商品名拼接为字符串，格式："商品1、商品2、商品3"
            options_str = "、".join(options)
            # 构造向用户确认的提示语
            answer = f"您是想问以下哪个产品：{options_str}？请明确一下型号。"
            # 更新会话状态：设置确认提示语、清空商品名列表
            return [], answer

        # 分支C：无确认商品名，且无候选商品名（无匹配结果，需用户重新提供）
        return [], "抱歉，未找到相关产品，请提供准确型号以便我为您查询。"
    
    def _step_8_write_history(self, answer, item_names, session_id, original_query, rewritten_query, message_id):
        """
         8 把本次处理的核心信息（用户问题、助手答案、商品名、改写查询）写入MongoDB的会话历史
         包含2个核心操作：1. 写入助手答案（若有）；2. 更新用户原始问题的关联信息
         :param state: 字典 - step6更新后的会话状态，包含answer/item_names等字段
         :param session_id: 字符串 - 会话唯一标识
         :param rewritten_query: 字符串 - step3改写后的完整问题
         :param message_id: 字符串 - 本次用户问题的消息唯一ID
         :return:
         """
        # 若会话状态中有助手答案（分支B/C），写入助手消息到历史
        if answer:
            save_chat_message(
                session_id=session_id,  # 会话ID，关联所属会话
                role="assistant",  # 消息角色：助手
                text=answer,  # 消息内容：向用户确认的提示语/无结果提示语
                rewritten_query="",  # 助手消息无需改写查询，设为空
                item_names=item_names  # 关联的商品名列表（分支B/C均为空）
            )

        # 强制更新本次用户原始问题的关联信息（核心：补充改写查询、商品名）
        save_chat_message(
            session_id=session_id,  # 会话ID，关联所属会话
            role="user",  # 消息角色：用户
            text=original_query,  # 消息内容：用户原始查询
            rewritten_query=rewritten_query,  # 补充step3改写后的完整问题
            item_names=item_names,  # 补充关联的商品名列表
            message_id=message_id  # 消息ID，指定更新已存在的用户消息（而非新增）
        )
    
    def process(self, state: QueryGraphState) -> QueryGraphState:
        """
        必要参数：session_id、original_query
        更新参数：history、rewritten_query、item_names、answer
        """
        # 步骤1：校验参数
        session_id, original_query = self._step_1_validate_input_state(state)
        self.logger.info("步骤1：参数校验通过")

        # 步骤2：获取历史记录
        history = get_recent_messages(session_id)
        self.logger.info(f"步骤2：获取到 {len(history)} 条历史消息")

        # 步骤3：用户初始消息保存
        message_id = save_chat_message(session_id, "user", original_query)
        self.logger.info(f"步骤3：用户消息已初始保存, ID: {message_id}")

        # 步骤4：提取信息
        item_names, rewritten_query = resolve_item_name_and_rewrite_query(original_query, history)

        # 5. & 6. 如果有提取到商品名，进行搜索和对齐
        confirmed_item_names = []
        options = []
        if len(item_names) > 0:
            # 把LLM推测的商品名转换成向量，在向量库中检索匹配
            search_results = hybrid_search_item_name(item_names)
            # 把向量检索结果转换成高置信度，中置信度列表
            confirmed_item_names, options = self._step_6_align_item_names(search_results)
        else:
            self.logger.info("Node: 未提取到商品名，跳过向量检索")

        # 7. 检查确认状态
        item_names, answer = self._step_7_check_confirmation(confirmed_item_names, options, history)

        # 8. 写入最终历史
        self._step_8_write_history(answer, item_names, session_id, original_query, rewritten_query, message_id)    
        return {
            "history": history,
            "rewritten_query": rewritten_query,
            "item_names": item_names,
            "answer": answer
        }

if __name__ == "__main__":
    from app.utils.logger import setup_logging
    logger = setup_logging()
    # 初始化图状态
    init_state = {
        "session_id": "abc123",
        "original_query": "M272Q"
    }
    # 创建节点对象
    node_item_name_confirm = NodeItemNameConfirm()
    # 执行节点的单元测试
    result = node_item_name_confirm(init_state)
    # 将返回的图状态进行json序列化
    json_state = format_json(result)
    # 输出
    logger.info(json_state)