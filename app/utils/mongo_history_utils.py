import os
import logging
from typing import List, Dict, Any
from datetime import datetime
from pymongo import MongoClient, DESCENDING
from bson import ObjectId

logger = logging.getLogger(__name__)

class HistoryMongoTool:
    """
    MongoDB 历史对话记录读写工具类 (基于原生 PyMongo 实现)
    核心功能：封装MongoDB的连接、集合初始化、索引创建，为上层提供统一的数据库操作入口
    扩展功能：支持与LangChain消息对象的格式转换（原代码预留能力）
    """
    def __init__(self):
        try:
            self.mongo_url = os.getenv("MONGO_URL")
            self.db_name = os.getenv("MONGO_DB_NAME")
            self.client = MongoClient(self.mongo_url)
            self.db = self.client[self.db_name]
            self.chat_message = self.db["chat_message"]

            # 为chat_message集合创建复合索引，提升查询性能
            # 索引规则：session_id升序 + ts降序，适配"按会话查最新记录"的核心查询场景
            # create_index自带幂等性：索引已存在时不会重复创建，无需额外判断
            self.chat_message.create_index([("session_id", 1), ("ts", -1)])
            logger.info(f"Successfully connected to MongoDB: {self.db_name}")
        except Exception as e:
            logger.error(f"Failed to connect to MongoDB: {e}")
            # 重新抛出异常，让调用方感知初始化失败，避免使用未初始化的实例
            raise


# 定义全局变量：存储HistoryMongoTool的单例实例
__history_mongo_tool = None

def _get_history_mongo_tool() -> HistoryMongoTool:
    # 声明使用全局变量，避免函数内视为局部变量
    global __history_mongo_tool
    # 懒加载：仅当全局实例为空时，才创建新的实例
    if __history_mongo_tool is None:
        __history_mongo_tool = HistoryMongoTool()
    return __history_mongo_tool

def clear_history(session_id: str) -> int:
    """
    清空指定会话的所有历史对话记录
    :param session_id: 会话唯一标识，用于筛选要删除的记录
    :return: 实际删除的文档数量，删除失败返回0
    """
    try:
        # 执行批量删除操作：删除所有session_id匹配的文档
        result = _get_history_mongo_tool().chat_message.delete_many({"session_id": session_id})
        # 记录删除成功日志，包含删除数量和会话ID，便于问题排查
        logger.info(f"Deleted {result.deleted_count} messages for session {session_id}")
        # 返回实际删除的数量（delete_many的返回对象包含deleted_count属性）
        return result.deleted_count
    except Exception as e:
        # 捕获删除异常，记录错误日志，包含会话ID
        logger.error(f"Error clearing history for session {session_id}: {e}")
        # 异常时返回0，标识删除失败
        return 0

def save_chat_message(
    session_id: str,
    role: str,
    text: str,
    rewritten_query: str = "",
    item_names: List[str] = None,
    image_urls: List[str] = None,
    message_id: str = None
) -> str:
    """
    写入/更新单条会话记录到MongoDB
    支持两种模式：无message_id时新增记录，有message_id时更新已有记录
    :param session_id: 会话唯一标识，关联对话所属的会话
    :param role: 消息角色，固定值：user（用户）/assistant（助手）
    :param text: 对话核心内容，用户的提问或助手的回答
    :param rewritten_query: 重写后的查询语句（可选，用于检索增强等场景，默认空字符串）
    :param item_names: 关联的商品名称列表（可选，支持多商品，默认None）
    :param image_urls: 关联的图片URL列表（可选，默认None）
    :param message_id: 记录主键ID（可选，有值则更新，无值则新增）
    :return: 插入/更新的记录唯一标识（新增返回ObjectId字符串，更新返回传入的message_id）
    """
    # 生成当前时间的时间戳（秒级），用于记录消息的创建时间，后续用于排序和查询
    ts = datetime.now().timestamp()

    # 构造要插入/更新的文档数据（MongoDB的基本数据单元是文档，类似Python字典）
    document = {
        "session_id": session_id,                   # 会话ID，关联维度
        "role": role,                               # 消息角色
        "text": text,                               # 消息内容
        "rewritten_query": rewritten_query or "",   # 问题优化后的改写，空值处理为空字符串
        "item_names": item_names,                   # 关联商品名称列表
        "image_urls": image_urls,                   # 关联图片URL列表
        "ts": ts                                    # 时间戳，排序和时间筛选维度
    }

    mongo_tool = _get_history_mongo_tool()
    # 判断是否传入主键ID，区分更新/新增逻辑
    if message_id:
        # 有message_id：执行更新操作（根据主键更新）
        result = mongo_tool.chat_message.update_one(
            {"_id": ObjectId(message_id)},
            {"$set": document}              
        )
        logger.info(f"chat message updated: {document}")
        return message_id
    else:
        # 无message_id：执行新增操作
        result = mongo_tool.chat_message.insert_one(document)
        logger.info(f"chat message inserted: {document}")
        # 新增操作返回插入的ObjectId并转为字符串，便于上层使用（避免直接返回ObjectId对象）
        return str(result.inserted_id)

def update_message_item_names(ids: List[str], item_names: List[str]) -> int:
    """
    批量更新历史会话记录的关联商品名称
    :param ids: 要更新的记录主键ID列表（字符串类型）
    :param item_names: 要设置的新商品名称列表
    :return: 实际更新的文档数量，更新失败返回0
    """
    try:
        result = _get_history_mongo_tool().chat_message.update_many(
            {
                "_id": {"$in": [ObjectId(i) for i in ids]}
            },
            {"$set": {"item_names": item_names}}
        )
        logger.info(f"Updated {result.modified_count} records to item_names: {item_names}")
        # 返回实际更新的数量（modified_count：真正被修改的文档数，区别于matched_count）
        return result.modified_count
    except Exception as e:
        logger.error(f"Error updating history item_names: {e}")
        return 0

def get_recent_messages(session_id: str = None, limit: int = 10) -> List[Dict[str, Any]]:
    """
    查询指定会话的最近N条对话记录，返回原始字典格式
    结果按时间正序排列，可直接喂给LLM作为上下文
    :param session_id: 会话唯一标识，用于筛选指定会话的记录
    :param limit: 条数限制，默认返回最近10条
    :return: 对话记录列表（字典格式），查询失败返回空列表
    """
    try:
        query = {"session_id": session_id} if session_id else {}
        cursor = _get_history_mongo_tool().chat_message.find(query).sort("ts", DESCENDING).limit(limit)
        # 将游标转为列表，触发实际数据库查询，获取所有符合条件的文档
        messages = list(cursor)
        for m in messages:
            logger.info(f'{datetime.fromtimestamp(m["ts"]).strftime("%Y-%m-%d %H:%M:%S")} - {m["role"]}: {m["text"]}')
        return messages
    except Exception as e:
        logger.error(f"Error getting recent messages: {e}")
        return []


if __name__ == "__main__":
    from dotenv import load_dotenv
    load_dotenv()
    # 简单测试代码：验证数据库的写入和查询功能是否正常
    # 测试会话ID，用于标识测试的对话记录
    sid = "000015_hybrid"
    # # 1. 写入用户消息
    # save_chat_message(sid, "user", "你好 (Hybrid)")
    # # 2. 写入助手回复
    # save_chat_message(sid, "assistant", "你好！我是基于原生 Mongo + LangChain 对象的助手。")
    # # 3. 写入带关联商品的用户消息
    # save_chat_message(sid, "user", "这个万用表怎么换电池？", item_names=["混合万用表"])


    # sid = "test_session_002"
    # save_chat_message(sid, "user", "你好，有烫金机吗？")
    # save_chat_message(sid, "assistant", "你好！请问你想询问哪个型号？")
    # save_chat_message(sid, "user", "brother的HAK180烫金机")
    # save_chat_message(sid, "assistant", "有的")

    # sid = "test_session_003"
    # save_chat_message(sid, "user", "你好，有万用表吗？")
    # save_chat_message(sid, "assistant", "你好！请问你想询问哪个型号？")
    # save_chat_message(sid, "user", "RS12万用表")
    # save_chat_message(sid, "assistant", "有的")

    # sid = "test_session_004"
    # save_chat_message(sid, "user", "你好，请问有烫金机吗")
    # save_chat_message(sid, "assistant", "你好！请问你想询问哪个型号？")
    # save_chat_message(sid, "user", "HAK180和HAK181都可以")
    # save_chat_message(sid, "assistant", "有的")

    # 4. 查询指定会话的最近5条记录，验证查询功能
    print("--- 查询 LangChain 对象记录 ---")
    messages = get_recent_messages(sid, limit=5)
    # 打印查询到的记录数量
    print(f"查询到的记录数: {len(messages)}")
    # 遍历打印每条记录的详细内容
    # for m in messages:
    #     print(f" {m}  ")

    print(f"查询到的总记录数: {len(messages)}")
    messages = get_recent_messages()
    for m in messages:
        print(f" {m}  ")