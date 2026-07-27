from dotenv import load_dotenv
from app.services.mongo import get_mongo_service

if __name__ == "__main__":
    load_dotenv()
    
    mongo = get_mongo_service()
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
    messages = mongo.get_recent_messages(sid, limit=5)
    # 打印查询到的记录数量
    print(f"查询到的记录数: {len(messages)}")
    # 遍历打印每条记录的详细内容
    # for m in messages:
    #     print(f" {m}  ")

    print(f"查询到的总记录数: {len(messages)}")
    messages = mongo.get_recent_messages()
    for m in messages:
        print(f" {m}  ")