from dotenv import load_dotenv
load_dotenv()

from app.processor.query_processor.nodes.node_answer_output import NodeAnswerOutput
from app.utils.logger import setup_logging

if __name__ == "__main__":
    setup_logging("DEBUG")
    print("开始测试: 答案生成节点")
    # 1. 构造模拟数据
    # 模拟重排序后的文档列表 (reranked_docs)
    # 包含：本地文档（带Markdown图片）、联网结果（带URL字段）、纯文本文档
    mock_reranked_docs = [
        {
            "chunk_id": "local_101",
            "source": "local",
            "title": "HAK 180 烫金机操作手册_v2",
            "score": 0.95,
            "url": None,
            "content": """
            HAK 180 烫金机的操作面板位于机器正前方。
            开启电源后，您需要先设置温度，默认建议设置在 110℃ 左右。
            具体的操作面板布局请参考下图：
            ![操作面板布局图](http://local-server/images/panel_view.jpg)

            如果是进行局部烫金，请调节侧面的旋钮。
            ![侧面旋钮细节](http://local-server/images/knob_detail.png)
            """
        },
        {
            "chunk_id": None,
            "source": "web",
            "title": "HAK 180 常见故障排除 - 官网",
            "score": 0.88,
            "url": "http://example.com/hak180_troubleshooting.jpeg", # 这是一个直接指向图片的URL（虽然少见，但用于测试提取）
            "content": "如果机器无法加热，请检查保险丝是否熔断..."
        },
        {
            "chunk_id": "local_102",
            "source": "local",
            "title": "安全注意事项",
            "score": 0.82,
            "url": None,
            "content": "操作时请务必佩戴隔热手套，避免高温烫伤。"
        }
    ]
    # 模拟历史记录
    mock_history = [
        {"role": "user", "text": "你好，这款机器怎么用？"},
        {"role": "assistant", "text": "您好！请问您具体指的是哪一款机器？"},
        {"role": "user", "text": "HAK 180 烫金机"}
    ]
    # 模拟输入状态
    mock_state = {
        "session_id": "test_answer_session_001",
        "original_query": "HAK 180 烫金机怎么操作？",
        "rewritten_query": "HAK 180 烫金机的具体操作步骤和面板设置方法",
        "item_names": ["HAK 180 烫金机"],
        "history": mock_history,
        "reranked_docs": mock_reranked_docs,
        "is_stream": False, # 测试非流式
        # "is_stream": True, # 若要测试流式，需确保 SSE 环境或 mock 相关函数
        "answer": None # 初始无答案
    }

    node_answer_output = NodeAnswerOutput()
    result = node_answer_output(mock_state)

    # 1. 验证 Prompt 构建
    if "prompt" in result:
        print(f"[PASS] Prompt 构建成功 (长度: {len(result['prompt'])})")
        print(f"Prompt 预览:\n{result['prompt'][:200]}...")
    else:
        print("[FAIL] Prompt 未构建")

    # 2. 验证答案生成
    answer = result.get("answer")
    if answer and len(answer) > 10:
        print(f"[PASS] 答案生成成功 (长度: {len(answer)})")
        print(f"答案预览: {answer[:50]}...")
    else:
        print(f"[WARN] 答案生成可能异常 (Content: {answer})")

    # 3. 验证图片提取
    # 我们期望提取到 3 张图片：
    # 1. http://local-server/images/panel_view.jpg (来自 local_101)
    # 2. http://local-server/images/knob_detail.png (来自 local_101)
    # 3. http://example.com/hak180_troubleshooting.jpeg (来自 web 结果的 url 字段)

    # 注意：这里我们没办法直接从 result state 里拿到 image_urls，因为它是作为 SSE 推送出去的，或者存库了
    # 但我们可以通过日志观察 _extract_images_from_docs 的输出
    # 如果需要验证，可以临时修改 node_answer_output 返回 image_urls
    print("[INFO] 请检查上方日志中是否包含 '图片提取完成' 及以下 URL:")
    print(" - http://local-server/images/panel_view.jpg")
    print(" - http://local-server/images/knob_detail.png")
    print(" - http://example.com/hak180_troubleshooting.jpeg")


"""
(knowledge-base) D:\code\atguigu\knowledge-base>python -m app.test.processor.query_processor.nodes.node_answer_output
2026-07-25 20:55:26 - root - INFO - logging initialized: ./logs\knowledge_base.log
开始测试: 答案生成节点
2026-07-25 20:55:26 - import.node_answer_output - INFO - --- node_answer_output started ---
2026-07-25 20:55:26 - import.node_answer_output - INFO - Prompt constructed:
你是一个智能助手，请根据参考内容回答用户的问题。
要求：
1 尽量基于【参考内容】和【用户问题】 作答，不要编造不存在的事实。
2 如果用户的问题需要通过图片来辅助说明（例如：外观、结构、接线、示意图等）,图片只能来自于本地切片文本中的图片，请在答案最后追加一个独立的图片区块，格式严格如下：
【图片】
<图片URL1>
<图片URL2>
（每行一个URL；如果没有合适图片则不要输出【图片】区块）

【参考内容】
[1] [source=local] [chunk_id=local_101] [url=None] [title=HAK 180 烫金机操作手册_v2] [score=0.9500]

            HAK 180 烫金机的操作面板位于机器正前方。
            开启电源后，您需要先设置温度，默认建议设置在 110℃ 左右。
            具体的操作面板布局请参考下图：
            ![操作面板布局图](http://local-server/images/panel_view.jpg)

            如果是进行局部烫金，请调节侧面的旋钮。
            ![侧面旋钮细节](http://local-server/images/knob_detail.png)


[2] [source=web] [chunk_id=None] [url=http://example.com/hak180_troubleshooting.jpeg] [title=HAK 180 常见故障排除 - 官网] [score=0.8800]
如果机器无法加热，请检查保险丝是否熔断...

[3] [source=local] [chunk_id=local_102] [url=None] [title=安全注意事项] [score=0.8200]
操作时请务必佩戴隔热手套，避免高温烫伤。

【历史对话】
user: 你好，这款机器怎么用？
assistant: 您好！请问您具体指的是哪一款机器？
user: HAK 180 烫金机

【相关商品/实体】
HAK 180 烫金机

【用户问题】
HAK 180 烫金机的具体操作步骤和面板设置方法

请回答：
2026-07-25 20:55:26 - import.node_answer_output - INFO - ---Step 3: LLM Generation---
2026-07-25 20:55:26 - app.services.llm_service - DEBUG - Getting LangChain ChatOpenAI None client instance...
2026-07-25 20:55:27 - app.services.llm_service - INFO - LangChain ChatOpenAI ('qwen-flash', False) client instance created...
2026-07-25 20:55:27 - import.node_answer_output - INFO - Blocking mode, session: test_answer_session_001
2026-07-25 20:55:27 - openai._base_client - DEBUG - Request options: {'method': 'post', 'url': '/chat/completions', 'headers': {'X-Stainless-Raw-Response': 'true'}, 'files': None, 'idempotency_key': 'stainless-python-retry-8a125c35-d920-4cb8-a93f-e91a1ef613f2', 'security': {'bearer_auth': True}, 'content': None, 'json_data': {'messages': [{'content': '你是一个智能助手，请根据参考内容回答用户的问题。\n要求：\n1 尽量基于【参考内容】和【用户问题】 作答，不要编造不存在的事实。\n2 如果用户的问题需要通过图片来辅助说明（例如：外观、结构、接线、示意图等）,图片只能来自于本地切片文本中的图片，请在答案最后追加一个独立的图片区块，格式严格如下：\n【图片】\n<图片URL1>\n<图片URL2>\n（每行一个URL；如果没有合适图片则不要输出【图片】区块）\n\n【参考内容】\n[1] [source=local] [chunk_id=local_101] [url=None] [title=HAK 180 烫金机操作手册_v2] [score=0.9500]\n\n            HAK 180 烫金机的操作面板位于机器正前方。\n            开启电源后，您需要先设置温度，默认建议设置在 110℃ 左右。\n            具体的操作面板布局请参考下图：\n            ![操作面板布局图](http://local-server/images/panel_view.jpg)\n\n            如果是进行局部烫金，请调节侧面的旋钮。\n            ![侧面旋钮细节](http://local-server/images/knob_detail.png)\n            \n\n[2] [source=web] [chunk_id=None] [url=http://example.com/hak180_troubleshooting.jpeg] [title=HAK 180 常见故障排除 - 官网] [score=0.8800]\n如果机器无法加热，请检查保险丝是否熔断...\n\n[3] [source=local] [chunk_id=local_102] [url=None] [title=安全注意事项] [score=0.8200]\n操作时请务必佩戴隔热手套，避免高温烫伤。\n\n【历史对话】\nuser: 你好，这款机器怎么用？\nassistant: 您好！请问您具体指的是哪一款机器？\nuser: HAK 180 烫金机\n\n【相关商品/实体】\nHAK 180 烫金机\n\n【用户问题】\nHAK 180 烫金机的具体操作步骤和面板设置方法\n\n请回答：', 'role': 'user'}], 'model': 'qwen-flash', 'stream': False, 'temperature': 0.1}, 'extra_json': {'enable_thinking': False}}
2026-07-25 20:55:27 - openai._base_client - DEBUG - Sending HTTP Request: POST https://ws-xfsvflr5yndg90oh.cn-beijing.maas.aliyuncs.com/compatible-mode/v1/chat/completions
2026-07-25 20:55:27 - httpcore.connection - DEBUG - connect_tcp.started host='ws-xfsvflr5yndg90oh.cn-beijing.maas.aliyuncs.com' port=443 local_address=None timeout=None socket_options=[(65535, 8, 1)]
2026-07-25 20:55:27 - httpcore.connection - DEBUG - connect_tcp.complete return_value=<httpcore._backends.sync.SyncStream object at 0x00000210EE5FC750>
2026-07-25 20:55:27 - httpcore.connection - DEBUG - start_tls.started ssl_context=<ssl.SSLContext object at 0x00000210ECB9F530> server_hostname='ws-xfsvflr5yndg90oh.cn-beijing.maas.aliyuncs.com' timeout=None
2026-07-25 20:55:27 - httpcore.connection - DEBUG - start_tls.complete return_value=<httpcore._backends.sync.SyncStream object at 0x00000210EE5FC710>
2026-07-25 20:55:27 - httpcore.http11 - DEBUG - send_request_headers.started request=<Request [b'POST']>
2026-07-25 20:55:27 - httpcore.http11 - DEBUG - send_request_headers.complete
2026-07-25 20:55:27 - httpcore.http11 - DEBUG - send_request_body.started request=<Request [b'POST']>
2026-07-25 20:55:27 - httpcore.http11 - DEBUG - send_request_body.complete
2026-07-25 20:55:27 - httpcore.http11 - DEBUG - receive_response_headers.started request=<Request [b'POST']>
2026-07-25 20:55:29 - httpcore.http11 - DEBUG - receive_response_headers.complete return_value=(b'HTTP/1.1', 200, b'OK', [(b'content-type', b'application/json; charset=utf-8'), (b'grpc-encoding', b'identity'), (b'grpc-accept-encoding', b'gzip'), (b'x-envoy-upstream-service-time', b'2024'), (b'content-encoding', b'gzip'), (b'vary', b'Accept-Encoding'), (b'date', b'Sat, 25 Jul 2026 12:55:29 GMT'), (b'server', b'istio-envoy'), (b'x-request-id', b'78a953c8-0d64-96a2-ab99-fd89e117609e'), (b'req-cost-time', b'2044'), (b'req-arrive-time', b'1784984127077'), (b'resp-start-time', b'1784984129121'), (b'transfer-encoding', b'chunked')])
2026-07-25 20:55:29 - httpx - INFO - HTTP Request: POST https://ws-xfsvflr5yndg90oh.cn-beijing.maas.aliyuncs.com/compatible-mode/v1/chat/completions "HTTP/1.1 200 OK"
2026-07-25 20:55:29 - httpcore.http11 - DEBUG - receive_response_body.started request=<Request [b'POST']>
2026-07-25 20:55:29 - httpcore.http11 - DEBUG - receive_response_body.complete
2026-07-25 20:55:29 - httpcore.http11 - DEBUG - response_closed.started
2026-07-25 20:55:29 - httpcore.http11 - DEBUG - response_closed.complete
2026-07-25 20:55:29 - openai._base_client - DEBUG - HTTP Response: POST https://ws-xfsvflr5yndg90oh.cn-beijing.maas.aliyuncs.com/compatible-mode/v1/chat/completions "200 OK" Headers({'content-type': 'application/json; charset=utf-8', 'grpc-encoding': 'identity', 'grpc-accept-encoding': 'gzip', 'x-envoy-upstream-service-time': '2024', 'content-encoding': 'gzip', 'vary': 'Accept-Encoding', 'date': 'Sat, 25 Jul 2026 12:55:29 GMT', 'server': 'istio-envoy', 'x-request-id': '78a953c8-0d64-96a2-ab99-fd89e117609e', 'req-cost-time': '2044', 'req-arrive-time': '1784984127077', 'resp-start-time': '1784984129121', 'transfer-encoding': 'chunked'})
2026-07-25 20:55:29 - openai._base_client - DEBUG - request_id: 78a953c8-0d64-96a2-ab99-fd89e117609e
2026-07-25 20:55:29 - import.node_answer_output - INFO - Generation completed, content length: 381
2026-07-25 20:55:29 - import.node_answer_output - INFO - 开始提取图片，待处理文档数: 3
2026-07-25 20:55:29 - import.node_answer_output - DEBUG - 文档[0] 正文发现 Markdown 图片: http://local-server/images/panel_view.jpg
2026-07-25 20:55:29 - import.node_answer_output - DEBUG - 文档[0] 正文发现 Markdown 图片: http://local-server/images/knob_detail.png
2026-07-25 20:55:29 - import.node_answer_output - DEBUG - 文档[1] 发现图片 URL (字段): http://example.com/hak180_troubleshooting.jpeg
2026-07-25 20:55:29 - import.node_answer_output - INFO - 图片提取完成，共找到 3 张唯一图片: ['http://local-server/images/panel_view.jpg', 'http://local-server/images/knob_detail.png', 'http://example.com/hak180_troubleshooting.jpeg']
2026-07-25 20:55:29 - pymongo.topology - DEBUG - {"message": "Starting topology monitoring", "topologyId": {"$oid": "6a64b241936ef93d6719d87e"}}
2026-07-25 20:55:29 - pymongo.topology - DEBUG - {"message": "Topology description changed", "topologyId": {"$oid": "6a64b241936ef93d6719d87e"}, "previousDescription": "<TopologyDescription id: 6a64b241936ef93d6719d87e, topology_type: Unknown, servers: []>", "newDescription": "<TopologyDescription id: 6a64b241936ef93d6719d87e, topology_type: Unknown, servers: [<ServerDescription ('192.168.222.8', 27017) server_type: Unknown, rtt: None>]>"}
2026-07-25 20:55:29 - pymongo.topology - DEBUG - {"message": "Starting server monitoring", "topologyId": {"$oid": "6a64b241936ef93d6719d87e"}, "serverHost": "192.168.222.8", "serverPort": 27017}
2026-07-25 20:55:29 - pymongo.connection - DEBUG - {"message": "Connection pool created", "clientId": {"$oid": "6a64b241936ef93d6719d87e"}, "serverHost": "192.168.222.8", "serverPort": 27017}
2026-07-25 20:55:29 - pymongo.serverSelection - DEBUG - {"message": "Server selection started", "selector": "<function writable_server_selector at 0x00000210EC47A660>", "operation": "createIndexes", "topologyDescription": "<TopologyDescription id: 6a64b241936ef93d6719d87e, topology_type: Unknown, servers: [<ServerDescription ('192.168.222.8', 27017) server_type: Unknown, rtt: None>]>", "clientId": {"$oid": "6a64b241936ef93d6719d87e"}}
2026-07-25 20:55:29 - pymongo.serverSelection - DEBUG - {"message": "Waiting for suitable server to become available", "selector": "<function writable_server_selector at 0x00000210EC47A660>", "operation": "createIndexes", "topologyDescription": "<TopologyDescription id: 6a64b241936ef93d6719d87e, topology_type: Unknown, servers: [<ServerDescription ('192.168.222.8', 27017) server_type: Unknown, rtt: None>]>", "clientId": {"$oid": "6a64b241936ef93d6719d87e"}, "remainingTimeMS": 30000}
2026-07-25 20:55:29 - pymongo.topology - DEBUG - {"message": "Server heartbeat started", "topologyId": {"$oid": "6a64b241936ef93d6719d87e"}, "driverConnectionId": 1, "serverHost": "192.168.222.8", "serverPort": 27017, "awaited": false}
2026-07-25 20:55:29 - pymongo.topology - DEBUG - {"message": "Server heartbeat succeeded", "topologyId": {"$oid": "6a64b241936ef93d6719d87e"}, "driverConnectionId": 1, "serverConnectionId": 8, "serverHost": "192.168.222.8", "serverPort": 27017, "awaited": false, "durationMS": 0.0, "reply": "{\"helloOk\": true, \"ismaster\": true, \"topologyVersion\": {\"processId\": {\"$oid\": \"6a64afd5eec0bf79f499e56e\"}}, \"maxBsonObjectSize\": 16777216, \"maxMessageSizeBytes\": 48000000, \"maxWriteBatchSize\": 100000, \"localTime\": {\"$date\": \"2026-07-25T12:55:29.233Z\"}, \"logicalSessionTimeoutMinutes\": 30, \"connectionId\": 8, \"maxWireVersion\": 27, \"ok\": 1.0}"}
2026-07-25 20:55:29 - pymongo.connection - DEBUG - {"message": "Connection pool ready", "clientId": {"$oid": "6a64b241936ef93d6719d87e"}, "serverHost": "192.168.222.8", "serverPort": 27017}
2026-07-25 20:55:29 - pymongo.topology - DEBUG - {"message": "Topology description changed", "topologyId": {"$oid": "6a64b241936ef93d6719d87e"}, "previousDescription": "<TopologyDescription id: 6a64b241936ef93d6719d87e, topology_type: Unknown, servers: [<ServerDescription ('192.168.222.8', 27017) server_type: Unknown, rtt: None>]>", "newDescription": "<TopologyDescription id: 6a64b241936ef93d6719d87e, topology_type: Single, servers: [<ServerDescription ('192.168.222.8', 27017) server_type: Standalone, rtt: 0.0>]>"}
2026-07-25 20:55:29 - pymongo.serverSelection - DEBUG - {"message": "Server selection succeeded", "selector": "<function writable_server_selector at 0x00000210EC47A660>", "operation": "createIndexes", "topologyDescription": "<TopologyDescription id: 6a64b241936ef93d6719d87e, topology_type: Single, servers: [<ServerDescription ('192.168.222.8', 27017) server_type: Standalone, rtt: 0.0>]>", "clientId": {"$oid": "6a64b241936ef93d6719d87e"}, "serverHost": "192.168.222.8", "serverPort": 27017}
2026-07-25 20:55:29 - pymongo.connection - DEBUG - {"message": "Connection checkout started", "clientId": {"$oid": "6a64b241936ef93d6719d87e"}, "serverHost": "192.168.222.8", "serverPort": 27017}
2026-07-25 20:55:29 - pymongo.topology - DEBUG - {"message": "Server heartbeat started", "topologyId": {"$oid": "6a64b241936ef93d6719d87e"}, "driverConnectionId": 1, "serverConnectionId": 8, "serverHost": "192.168.222.8", "serverPort": 27017, "awaited": true}
2026-07-25 20:55:29 - pymongo.connection - DEBUG - {"message": "Connection created", "clientId": {"$oid": "6a64b241936ef93d6719d87e"}, "serverHost": "192.168.222.8", "serverPort": 27017, "driverConnectionId": 1}
2026-07-25 20:55:29 - pymongo.connection - DEBUG - {"message": "Connection ready", "clientId": {"$oid": "6a64b241936ef93d6719d87e"}, "serverHost": "192.168.222.8", "serverPort": 27017, "driverConnectionId": 1, "durationMS": 0.0}
2026-07-25 20:55:29 - pymongo.connection - DEBUG - {"message": "Connection checked out", "clientId": {"$oid": "6a64b241936ef93d6719d87e"}, "serverHost": "192.168.222.8", "serverPort": 27017, "driverConnectionId": 1, "durationMS": 0.01500000013038516}
2026-07-25 20:55:29 - pymongo.command - DEBUG - {"message": "Command started", "clientId": {"$oid": "6a64b241936ef93d6719d87e"}, "command": "{\"createIndexes\": \"chat_message\", \"indexes\": [{\"name\": \"session_id_1_ts_-1\", \"key\": {\"session_id\": 1, \"ts\": -1}}], \"lsid\": {\"id\": {\"$binary\": {\"base64\": \"4Ji4LcCmTnywf/OFFSH7Xg==\", \"subType\": \"04\"}}}, \"$db\": \"kb001\"}", "commandName": "createIndexes", "databaseName": "kb001", "requestId": 18467, "operationId": 18467, "driverConnectionId": 1, "serverConnectionId": 10, "serverHost": "192.168.222.8", "serverPort": 27017}
2026-07-25 20:55:29 - pymongo.command - DEBUG - {"message": "Command succeeded", "clientId": {"$oid": "6a64b241936ef93d6719d87e"}, "durationMS": 2.69, "reply": "{\"numIndexesBefore\": 2, \"numIndexesAfter\": 2, \"note\": \"all indexes already exist\", \"ok\": 1.0}", "commandName": "createIndexes", "databaseName": "kb001", "requestId": 18467, "operationId": 18467, "driverConnectionId": 1, "serverConnectionId": 10, "serverHost": "192.168.222.8", "serverPort": 27017}
2026-07-25 20:55:29 - pymongo.connection - DEBUG - {"message": "Connection checked in", "clientId": {"$oid": "6a64b241936ef93d6719d87e"}, "serverHost": "192.168.222.8", "serverPort": 27017, "driverConnectionId": 1}
2026-07-25 20:55:29 - app.services.mongo_service - INFO - Successfully connected to MongoDB: kb001
2026-07-25 20:55:29 - pymongo.serverSelection - DEBUG - {"message": "Server selection started", "selector": "<function writable_server_selector at 0x00000210EC47A660>", "operation": "insert", "topologyDescription": "<TopologyDescription id: 6a64b241936ef93d6719d87e, topology_type: Single, servers: [<ServerDescription ('192.168.222.8', 27017) server_type: Standalone, rtt: 0.0>]>", "clientId": {"$oid": "6a64b241936ef93d6719d87e"}}
2026-07-25 20:55:29 - pymongo.serverSelection - DEBUG - {"message": "Server selection succeeded", "selector": "<function writable_server_selector at 0x00000210EC47A660>", "operation": "insert", "topologyDescription": "<TopologyDescription id: 6a64b241936ef93d6719d87e, topology_type: Single, servers: [<ServerDescription ('192.168.222.8', 27017) server_type: Standalone, rtt: 0.0>]>", "clientId": {"$oid": "6a64b241936ef93d6719d87e"}, "serverHost": "192.168.222.8", "serverPort": 27017}
2026-07-25 20:55:29 - pymongo.connection - DEBUG - {"message": "Connection checkout started", "clientId": {"$oid": "6a64b241936ef93d6719d87e"}, "serverHost": "192.168.222.8", "serverPort": 27017}
2026-07-25 20:55:29 - pymongo.connection - DEBUG - {"message": "Connection checked out", "clientId": {"$oid": "6a64b241936ef93d6719d87e"}, "serverHost": "192.168.222.8", "serverPort": 27017, "driverConnectionId": 1, "durationMS": 0.0}
2026-07-25 20:55:29 - pymongo.command - DEBUG - {"message": "Command started", "clientId": {"$oid": "6a64b241936ef93d6719d87e"}, "command": "{\"insert\": \"chat_message\", \"ordered\": true, \"lsid\": {\"id\": {\"$binary\": {\"base64\": \"4Ji4LcCmTnywf/OFFSH7Xg==\", \"subType\": \"04\"}}}, \"$db\": \"kb001\", \"documents\": [{\"session_id\": \"test_answer_session_001\", \"role\": \"assistant\", \"text\": \"HAK 180 \u70eb\u91d1\u673a\u7684\u5177\u4f53\u64cd\u4f5c\u6b65\u9aa4\u548c\u9762\u677f\u8bbe\u7f6e\u65b9\u6cd5\u5982\u4e0b\uff1a\n\n1. **\u5f00\u542f\u7535\u6e90**\uff1a\u5c06\u673a\u5668\u7535\u6e90\u6253\u5f00\uff0c\u7b49\u5f85\u7cfb\u7edf\u542f\u52a8\u3002\n\n2. **\u8bbe\u7f6e\u6e29\u5ea6**\uff1a\u9ed8\u8ba4\u5efa\u8bae\u5c06\u70eb\u91d1\u6e29\u5ea6\u8bbe\u7f6e\u5728 110\u2103 \u5de6\u53f3\u3002\u60a8\u53ef\u4ee5\u5728\u64cd\u4f5c\u9762\u677f\u4e0a\u8fdb\u884c\u6e29\u5ea6\u8c03\u8282\u3002\n\n3. **\u64cd\u4f5c\u9762\u677f\u5e03\u5c40**\uff1a\u64cd\u4f5c\u9762\u677f\u4f4d\u4e8e\u673a\u5668\u6b63\u524d\u65b9\uff0c\u5177\u4f53\u5e03\u5c40\u8bf7\u53c2\u8003\u4ee5\u4e0b\u793a\u610f\u56fe\uff1a\n   ![\u64cd\u4f5c\u9762\u677f\u5e03\u5c40\u56fe](http://local-serv...", "commandName": "insert", "databaseName": "kb001", "requestId": 6334, "operationId": 6334, "driverConnectionId": 1, "serverConnectionId": 10, "serverHost": "192.168.222.8", "serverPort": 27017}
2026-07-25 20:55:30 - pymongo.command - DEBUG - {"message": "Command succeeded", "clientId": {"$oid": "6a64b241936ef93d6719d87e"}, "durationMS": 11.321, "reply": "{\"n\": 1, \"ok\": 1.0}", "commandName": "insert", "databaseName": "kb001", "requestId": 6334, "operationId": 6334, "driverConnectionId": 1, "serverConnectionId": 10, "serverHost": "192.168.222.8", "serverPort": 27017}
2026-07-25 20:55:30 - pymongo.connection - DEBUG - {"message": "Connection checked in", "clientId": {"$oid": "6a64b241936ef93d6719d87e"}, "serverHost": "192.168.222.8", "serverPort": 27017, "driverConnectionId": 1}
2026-07-25 20:55:30 - app.services.mongo_service - INFO - Chat message inserted: {'session_id': 'test_answer_session_001', 'role': 'assistant', 'text': 'HAK 180 烫金机的具体操作步骤和面板设置方法如下：\n\n1. **开启电源**：将机器电源打开，等待系统启动。\n\n2. **设置温度**：默认建议将烫金温度设置在 110℃ 左右。您可以在操作面板上进行温度调节。\n\n3. **操作面板布局**：操作面板位于机器正前方，具体布局请参考以下示意图：\n   ![操作面板布局图](http://local-server/images/panel_view.jpg)\n\n4. **局部烫金设置**：如果需要进行局部烫金，请调节机器侧面的旋钮以控制烫金区域。\n\n5. **安全注意事项**：操作时务必佩戴隔热手套，避免高温烫伤。\n\n【图片】\n<http://local-server/images/panel_view.jpg>\n<http://local-server/images/knob_detail.png>', 'rewritten_query': '', 'item_names': ['HAK 180 烫金机'], 'image_urls': ['http://local-server/images/panel_view.jpg', 'http://local-server/images/knob_detail.png', 'http://example.com/hak180_troubleshooting.jpeg'], 'ts': 1784984129.990565, '_id': ObjectId('6a64b241936ef93d6719d87f')}
2026-07-25 20:55:30 - import.node_answer_output - INFO - ---发送 final 事件---图片为：['http://local-server/images/panel_view.jpg', 'http://local-server/images/knob_detail.png', 'http://example.com/hak180_troubleshooting.jpeg']
2026-07-25 20:55:30 - import.node_answer_output - INFO - --- node_answer_output done ---
[FAIL] Prompt 未构建
[WARN] 答案生成可能异常 (Content: None)
[INFO] 请检查上方日志中是否包含 '图片提取完成' 及以下 URL:
 - http://local-server/images/panel_view.jpg
 - http://local-server/images/knob_detail.png
 - http://example.com/hak180_troubleshooting.jpeg
2026-07-25 20:55:30 - pymongo.topology - DEBUG - {"message": "Server heartbeat failed", "topologyId": {"$oid": "6a64b241936ef93d6719d87e"}, "serverHost": "192.168.222.8", "serverPort": 27017, "awaited": true, "durationMS": 515.0000001303852, "failure": "\"_OperationCancelled('operation cancelled')\"", "driverConnectionId": 1}
"""