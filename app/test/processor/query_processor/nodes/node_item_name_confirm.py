from app.processor.query_processor.nodes.node_item_name_confirm import NodeItemNameConfirm
from app.utils.logger import setup_logging

if __name__ == "__main__":
    logger = setup_logging("DEBUG")
    init_state = {
        "session_id": "abc123",
        "original_query": "华为显示器不会捣鼓咋整"
    }
    node_item_name_confirm = NodeItemNameConfirm()
    result = node_item_name_confirm(init_state)
    logger.info(result)

"""
(knowledge-base) D:\knowledge-base>python -m app.test.processor.query_processor.nodes.node_item_name_confirm
2026-07-23 16:56:42 - root - INFO - logging initialized: ./logs\knowledge_base.log
2026-07-23 16:56:42 - import.node_item_name_confirm - INFO - --- node_item_name_confirm started ---
2026-07-23 16:56:42 - pymongo.topology - DEBUG - {"message": "Starting topology monitoring", "topologyId": {"$oid": "6a61d74a5cfaff4cb8358ede"}}
2026-07-23 16:56:42 - pymongo.topology - DEBUG - {"message": "Topology description changed", "topologyId": {"$oid": "6a61d74a5cfaff4cb8358ede"}, "previousDescription": "<TopologyDescription id: 6a61d74a5cfaff4cb8358ede, topology_type: Unknown, servers: []>", "newDescription": "<TopologyDescription id: 6a61d74a5cfaff4cb8358ede, topology_type: Unknown, servers: [<ServerDescription ('192.168.222.8', 27017) server_type: Unknown, rtt: None>]>"}
2026-07-23 16:56:42 - pymongo.topology - DEBUG - {"message": "Starting server monitoring", "topologyId": {"$oid": "6a61d74a5cfaff4cb8358ede"}, "serverHost": "192.168.222.8", "serverPort": 27017}
2026-07-23 16:56:42 - pymongo.connection - DEBUG - {"message": "Connection pool created", "clientId": {"$oid": "6a61d74a5cfaff4cb8358ede"}, "serverHost": "192.168.222.8", "serverPort": 27017}
2026-07-23 16:56:42 - pymongo.serverSelection - DEBUG - {"message": "Server selection started", "selector": "<function writable_server_selector at 0x0000022DFF7FFF60>", "operation": "createIndexes", "topologyDescription": "<TopologyDescription id: 6a61d74a5cfaff4cb8358ede, topology_type: Unknown, servers: [<ServerDescription ('192.168.222.8', 27017) server_type: Unknown, rtt: None>]>", "clientId": {"$oid": "6a61d74a5cfaff4cb8358ede"}}
2026-07-23 16:56:42 - pymongo.topology - DEBUG - {"message": "Server heartbeat started", "topologyId": {"$oid": "6a61d74a5cfaff4cb8358ede"}, "driverConnectionId": 1, "serverHost": "192.168.222.8", "serverPort": 27017, "awaited": false}
2026-07-23 16:56:42 - pymongo.serverSelection - DEBUG - {"message": "Waiting for suitable server to become available", "selector": "<function writable_server_selector at 0x0000022DFF7FFF60>", "operation": "createIndexes", "topologyDescription": "<TopologyDescription id: 6a61d74a5cfaff4cb8358ede, topology_type: Unknown, servers: [<ServerDescription ('192.168.222.8', 27017) server_type: Unknown, rtt: None>]>", "clientId": {"$oid": "6a61d74a5cfaff4cb8358ede"}, "remainingTimeMS": 30000}
2026-07-23 16:56:42 - pymongo.topology - DEBUG - {"message": "Server heartbeat succeeded", "topologyId": {"$oid": "6a61d74a5cfaff4cb8358ede"}, "driverConnectionId": 1, "serverConnectionId": 6, "serverHost": "192.168.222.8", "serverPort": 27017, "awaited": false, "durationMS": 15.999999945051968, "reply": "{\"helloOk\": true, \"ismaster\": true, \"topologyVersion\": {\"processId\": {\"$oid\": \"6a6159fee854a48366bbb27d\"}}, \"maxBsonObjectSize\": 16777216, \"maxMessageSizeBytes\": 48000000, \"maxWriteBatchSize\": 100000, \"localTime\": {\"$date\": \"2026-07-23T08:56:42.274Z\"}, \"logicalSessionTimeoutMinutes\": 30, \"connectionId\": 6, \"maxWireVersion\": 27, \"ok\": 1.0}"}
2026-07-23 16:56:42 - pymongo.connection - DEBUG - {"message": "Connection pool ready", "clientId": {"$oid": "6a61d74a5cfaff4cb8358ede"}, "serverHost": "192.168.222.8", "serverPort": 27017}
2026-07-23 16:56:42 - pymongo.topology - DEBUG - {"message": "Topology description changed", "topologyId": {"$oid": "6a61d74a5cfaff4cb8358ede"}, "previousDescription": "<TopologyDescription id: 6a61d74a5cfaff4cb8358ede, topology_type: Unknown, servers: [<ServerDescription ('192.168.222.8', 27017) server_type: Unknown, rtt: None>]>", "newDescription": "<TopologyDescription id: 6a61d74a5cfaff4cb8358ede, topology_type: Single, servers: [<ServerDescription ('192.168.222.8', 27017) server_type: Standalone, rtt: 0.015999999945051968>]>"}
2026-07-23 16:56:42 - pymongo.serverSelection - DEBUG - {"message": "Server selection succeeded", "selector": "<function writable_server_selector at 0x0000022DFF7FFF60>", "operation": "createIndexes", "topologyDescription": "<TopologyDescription id: 6a61d74a5cfaff4cb8358ede, topology_type: Single, servers: [<ServerDescription ('192.168.222.8', 27017) server_type: Standalone, rtt: 0.015999999945051968>]>", "clientId": {"$oid": "6a61d74a5cfaff4cb8358ede"}, "serverHost": "192.168.222.8", "serverPort": 27017}
2026-07-23 16:56:42 - pymongo.topology - DEBUG - {"message": "Server heartbeat started", "topologyId": {"$oid": "6a61d74a5cfaff4cb8358ede"}, "driverConnectionId": 1, "serverConnectionId": 6, "serverHost": "192.168.222.8", "serverPort": 27017, "awaited": true}
2026-07-23 16:56:42 - pymongo.connection - DEBUG - {"message": "Connection checkout started", "clientId": {"$oid": "6a61d74a5cfaff4cb8358ede"}, "serverHost": "192.168.222.8", "serverPort": 27017}
2026-07-23 16:56:42 - pymongo.connection - DEBUG - {"message": "Connection created", "clientId": {"$oid": "6a61d74a5cfaff4cb8358ede"}, "serverHost": "192.168.222.8", "serverPort": 27017, "driverConnectionId": 1}
2026-07-23 16:56:42 - pymongo.connection - DEBUG - {"message": "Connection ready", "clientId": {"$oid": "6a61d74a5cfaff4cb8358ede"}, "serverHost": "192.168.222.8", "serverPort": 27017, "driverConnectionId": 1, "durationMS": 0.01600000006146729}
2026-07-23 16:56:42 - pymongo.connection - DEBUG - {"message": "Connection checked out", "clientId": {"$oid": "6a61d74a5cfaff4cb8358ede"}, "serverHost": "192.168.222.8", "serverPort": 27017, "driverConnectionId": 1, "durationMS": 0.03100000007543713}
2026-07-23 16:56:42 - pymongo.command - DEBUG - {"message": "Command started", "clientId": {"$oid": "6a61d74a5cfaff4cb8358ede"}, "command": "{\"createIndexes\": \"chat_message\", \"indexes\": [{\"name\": \"session_id_1_ts_-1\", \"key\": {\"session_id\": 1, \"ts\": -1}}], \"lsid\": {\"id\": {\"$binary\": {\"base64\": \"I5pbKcywQP2KyNPuuWwxWA==\", \"subType\": \"04\"}}}, \"$db\": \"kb001\"}", "commandName": "createIndexes", "databaseName": "kb001", "requestId": 18467, "operationId": 18467, "driverConnectionId": 1, "serverConnectionId": 8, "serverHost": "192.168.222.8", "serverPort": 27017}
2026-07-23 16:56:42 - pymongo.command - DEBUG - {"message": "Command succeeded", "clientId": {"$oid": "6a61d74a5cfaff4cb8358ede"}, "durationMS": 3.777, "reply": "{\"numIndexesBefore\": 2, \"numIndexesAfter\": 2, \"note\": \"all indexes already exist\", \"ok\": 1.0}", "commandName": "createIndexes", "databaseName": "kb001", "requestId": 18467, "operationId": 18467, "driverConnectionId": 1, "serverConnectionId": 8, "serverHost": "192.168.222.8", "serverPort": 27017}
2026-07-23 16:56:42 - pymongo.connection - DEBUG - {"message": "Connection checked in", "clientId": {"$oid": "6a61d74a5cfaff4cb8358ede"}, "serverHost": "192.168.222.8", "serverPort": 27017, "driverConnectionId": 1}
2026-07-23 16:56:42 - app.services.mongo_service - INFO - Successfully connected to MongoDB: kb001
2026-07-23 16:56:42 - pymongo.serverSelection - DEBUG - {"message": "Server selection started", "selector": "Primary()", "operation": "find", "topologyDescription": "<TopologyDescription id: 6a61d74a5cfaff4cb8358ede, topology_type: Single, servers: [<ServerDescription ('192.168.222.8', 27017) server_type: Standalone, rtt: 0.015999999945051968>]>", "clientId": {"$oid": "6a61d74a5cfaff4cb8358ede"}}
2026-07-23 16:56:42 - pymongo.serverSelection - DEBUG - {"message": "Server selection succeeded", "selector": "Primary()", "operation": "find", "topologyDescription": "<TopologyDescription id: 6a61d74a5cfaff4cb8358ede, topology_type: Single, servers: [<ServerDescription ('192.168.222.8', 27017) server_type: Standalone, rtt: 0.015999999945051968>]>", "clientId": {"$oid": "6a61d74a5cfaff4cb8358ede"}, "serverHost": "192.168.222.8", "serverPort": 27017}
2026-07-23 16:56:42 - pymongo.connection - DEBUG - {"message": "Connection checkout started", "clientId": {"$oid": "6a61d74a5cfaff4cb8358ede"}, "serverHost": "192.168.222.8", "serverPort": 27017}
2026-07-23 16:56:42 - pymongo.connection - DEBUG - {"message": "Connection checked out", "clientId": {"$oid": "6a61d74a5cfaff4cb8358ede"}, "serverHost": "192.168.222.8", "serverPort": 27017, "driverConnectionId": 1, "durationMS": 0.0}
2026-07-23 16:56:42 - pymongo.command - DEBUG - {"message": "Command started", "clientId": {"$oid": "6a61d74a5cfaff4cb8358ede"}, "command": "{\"find\": \"chat_message\", \"filter\": {\"session_id\": \"abc123\"}, \"sort\": {\"ts\": -1}, \"limit\": 10, \"lsid\": {\"id\": {\"$binary\": {\"base64\": \"I5pbKcywQP2KyNPuuWwxWA==\", \"subType\": \"04\"}}}, \"$db\": \"kb001\"}", "commandName": "find", "databaseName": "kb001", "requestId": 6334, "operationId": 6334, "driverConnectionId": 1, "serverConnectionId": 8, "serverHost": "192.168.222.8", "serverPort": 27017}
2026-07-23 16:56:42 - pymongo.command - DEBUG - {"message": "Command succeeded", "clientId": {"$oid": "6a61d74a5cfaff4cb8358ede"}, "durationMS": 3.0010000000000003, "reply": "{\"cursor\": {\"firstBatch\": [{\"_id\": {\"$oid\": \"6a5a22398da24fcbce12d0b7\"}, \"session_id\": \"abc123\", \"role\": \"user\", \"text\": \"M272Q\", \"rewritten_query\": \"\u82cf\u4f2f\u5c13M272Q\u663e\u793a\u566827\u5bf8\u663e\u793a\u5668\u600e\u4e48\u5f00\u673a\uff1f\", \"item_names\": [\"\u82cf\u4f2f\u5c13M272Q\u663e\u793a\u5668\"], \"ts\": 1784291904.0104}, {\"_id\": {\"$oid\": \"6a5a1981687a46a2f25cba6e\"}, \"session_id\": \"abc123\", \"role\": \"user\", \"text\": \"27\u5bf8\u663e\u793a\u5668\u600e\u4e48\u5f00\u673a?\", \"rewritten_query\": \"27\u5bf8\u663e\u793a\u5668\u600e\u4e48\u5f00\u673a\uff1f\", \"item_names\": [\"\u82cf\u4f2f\u5c13M272Q\u663e\u793a\u5668\"], \"ts\": 1784289672.339298}, {\"_id\": {\"$oid\": \"6a5a1988687a46a2f25cba6f\"}, \"session_id\": \"abc123\", \"role\": \"assistant\", \"text\": \"\u60a8\u662f\u60f3\u95ee\u4ee5\u4e0b\u54ea\u4e2a\u4ea7\u54c1\uff1a\u82cf\u4f2f\u5c13M272Q\u663e\u793a\u5668\u3001\u82cf\u4f2f\u5c13B3-211H\u663e\u793a\u5668\uff1f\u8bf7\u660e\u786e\u4e00\u4e0b\u578b\u53f7\u3002\", \"item_names\": [\"\u82cf\u4f2f\u5c13M27...", "commandName": "find", "databaseName": "kb001", "requestId": 6334, "operationId": 6334, "driverConnectionId": 1, "serverConnectionId": 8, "serverHost": "192.168.222.8", "serverPort": 27017}
2026-07-23 16:56:42 - pymongo.connection - DEBUG - {"message": "Connection checked in", "clientId": {"$oid": "6a61d74a5cfaff4cb8358ede"}, "serverHost": "192.168.222.8", "serverPort": 27017, "driverConnectionId": 1}
2026-07-23 16:56:42 - app.services.mongo_service - DEBUG - 2026-07-17 20:38:24 - user: M272Q
2026-07-23 16:56:42 - app.services.mongo_service - DEBUG - 2026-07-17 20:01:12 - user: 27寸显示器怎么开机?
2026-07-23 16:56:42 - app.services.mongo_service - DEBUG - 2026-07-17 20:01:12 - assistant: 您是想问以下哪个产品：苏伯尓M272Q显示器、苏伯尓B3-211H显示器？请明确一下型号。
2026-07-23 16:56:42 - pymongo.serverSelection - DEBUG - {"message": "Server selection started", "selector": "<function writable_server_selector at 0x0000022DFF7FFF60>", "operation": "insert", "topologyDescription": "<TopologyDescription id: 6a61d74a5cfaff4cb8358ede, topology_type: Single, servers: [<ServerDescription ('192.168.222.8', 27017) server_type: Standalone, rtt: 0.015999999945051968>]>", "clientId": {"$oid": "6a61d74a5cfaff4cb8358ede"}}
2026-07-23 16:56:42 - pymongo.serverSelection - DEBUG - {"message": "Server selection succeeded", "selector": "<function writable_server_selector at 0x0000022DFF7FFF60>", "operation": "insert", "topologyDescription": "<TopologyDescription id: 6a61d74a5cfaff4cb8358ede, topology_type: Single, servers: [<ServerDescription ('192.168.222.8', 27017) server_type: Standalone, rtt: 0.015999999945051968>]>", "clientId": {"$oid": "6a61d74a5cfaff4cb8358ede"}, "serverHost": "192.168.222.8", "serverPort": 27017}
2026-07-23 16:56:42 - pymongo.connection - DEBUG - {"message": "Connection checkout started", "clientId": {"$oid": "6a61d74a5cfaff4cb8358ede"}, "serverHost": "192.168.222.8", "serverPort": 27017}
2026-07-23 16:56:42 - pymongo.connection - DEBUG - {"message": "Connection checked out", "clientId": {"$oid": "6a61d74a5cfaff4cb8358ede"}, "serverHost": "192.168.222.8", "serverPort": 27017, "driverConnectionId": 1, "durationMS": 0.0}
2026-07-23 16:56:42 - pymongo.command - DEBUG - {"message": "Command started", "clientId": {"$oid": "6a61d74a5cfaff4cb8358ede"}, "command": "{\"insert\": \"chat_message\", \"ordered\": true, \"lsid\": {\"id\": {\"$binary\": {\"base64\": \"I5pbKcywQP2KyNPuuWwxWA==\", \"subType\": \"04\"}}}, \"$db\": \"kb001\", \"documents\": [{\"session_id\": \"abc123\", \"role\": \"user\", \"text\": \"\\u534e\\u4e3a\\u663e\\u793a\\u5668\\u4e0d\\u4f1a\\u6363\\u9f13\\u548b\\u6574\", \"ts\": 1784797002.966194, \"_id\": {\"$oid\": \"6a61d74a5cfaff4cb8358edf\"}}]}", "commandName": "insert", "databaseName": "kb001", "requestId": 26500, "operationId": 26500, "driverConnectionId": 1, "serverConnectionId": 8, "serverHost": "192.168.222.8", "serverPort": 27017}
2026-07-23 16:56:42 - pymongo.command - DEBUG - {"message": "Command succeeded", "clientId": {"$oid": "6a61d74a5cfaff4cb8358ede"}, "durationMS": 2.506, "reply": "{\"n\": 1, \"ok\": 1.0}", "commandName": "insert", "databaseName": "kb001", "requestId": 26500, "operationId": 26500, "driverConnectionId": 1, "serverConnectionId": 8, "serverHost": "192.168.222.8", "serverPort": 27017}
2026-07-23 16:56:42 - pymongo.connection - DEBUG - {"message": "Connection checked in", "clientId": {"$oid": "6a61d74a5cfaff4cb8358ede"}, "serverHost": "192.168.222.8", "serverPort": 27017, "driverConnectionId": 1}
2026-07-23 16:56:42 - app.services.mongo_service - INFO - Chat message inserted: {'session_id': 'abc123', 'role': 'user', 'text': '华为显示器不会捣鼓咋整', 'rewritten_query': '', 'item_names': None, 'image_urls': None, 'ts': 1784797002.966194, '_id': ObjectId('6a61d74a5cfaff4cb8358edf')}
2026-07-23 16:56:42 - app.services.llm_service - DEBUG - User prompt for LLM:

历史会话：
assistant: 您是想问以下哪个产品：苏伯尓M272Q显示器、苏伯尓B3-211H显示器？请明确一下型号。
user: 27寸显示器怎么开机?
user: M272Q


当前用户问题：
华为显示器不会捣鼓咋整

请根据历史会话和当前问题，提取用户正在询问的商品名称（item_names）。
1. 如果用户明确提到了商品名称，请提取出来。可能有一个或多个，但不能重复。
2. 如果用户使用了代词（如"这个"、"它"），请结合历史会话指代消解，确定商品名称。
3. 如果无法确定商品名称，item_names 返回空列表。
4. 请重新改写用户的问题（rewritten_query），使其成为包含商品名称的独立完整问题。

请直接返回JSON格式结果，格式如下：
{
    "item_names": ["商品A", "商品B"],
    "rewritten_query": "关于商品A和商品B，..."
}

2026-07-23 16:56:42 - root - DEBUG - lm_config loaded LLMConfig(base_url='https://ws-xfsvflr5yndg90oh.cn-beijing.maas.aliyuncs.com/compatible-mode/v1', api_key='sk-ws-H.EMRLMMH.b5oG.MEUCIEUTDFBGW2yxwBPgwwFev5thtDIbXTtyUJEdmj3X3uNDAiEAqUguWZEovOVdVtkQN7WvpAyF7xzWhRgcdTB6z1W_Wg4', default_model='qwen-flash', vl_model='qwen3-vl-flash', item_model='qwen-flash', llm_temperature=0.1)
2026-07-23 16:56:42 - app.services.llm_service - DEBUG - Getting LangChain ChatOpenAI qwen-flash client instance...
2026-07-23 16:56:43 - app.services.llm_service - INFO - LangChain ChatOpenAI ('qwen-flash', True) client instance created...
2026-07-23 16:56:43 - openai._base_client - DEBUG - Request options: {'method': 'post', 'url': '/chat/completions', 'headers': {'X-Stainless-Helper-Method': 'chat.completions.parse', 'X-Stainless-Raw-Response': 'true'}, 'files': None, 'idempotency_key': 'stainless-python-retry-a760ab38-8519-4728-bde8-7a1981a8be17', 'post_parser': <function Completions.parse.<locals>.parser at 0x0000022D8A6DE520>, 'security': {'bearer_auth': True}, 'content': None, 'json_data': {'messages': [{'content': '你是一个专业的客服助手，擅长理解用户意图和提取关键信息。', 'role': 'system'}, {'content': '\n历史会话：\nassistant: 您是想问以下哪个产品：苏伯尓M272Q显示器、苏伯尓B3-211H显示器？请明确一下型号。\nuser: 27寸显示器怎么开机?\nuser: M272Q\n\n\n当前用户问题：\n华为显示器不会捣鼓咋整\n\n请根据历史会话和当前问题，提取用户正在询问的商品名称（item_names）。\n1. 如果用户明确提到了商品名称，请提取出来。可能有一个或多个，但不能重复。\n2. 如果用户使用了代词（如"这个"、"它"），请结合历史会话指代消解，确定商品名称。\n3. 如果无法确定商品名称，item_names 返回空列表。\n4. 请重新改写用户的问题（rewritten_query），使其成为包含商品名称的独立完整问题。\n\n请直接返回JSON格式结果，格式如下：\n{\n    "item_names": ["商品A", "商品B"],\n    "rewritten_query": "关于商品A和商品B，..."\n}\n', 'role': 'user'}], 'model': 'qwen-flash', 'response_format': {'type': 'json_object'}, 'stream': False, 'temperature': 0.1}, 'extra_json': {'enable_thinking': False}}
2026-07-23 16:56:43 - openai._base_client - DEBUG - Sending HTTP Request: POST https://ws-xfsvflr5yndg90oh.cn-beijing.maas.aliyuncs.com/compatible-mode/v1/chat/completions
2026-07-23 16:56:43 - httpcore.connection - DEBUG - connect_tcp.started host='ws-xfsvflr5yndg90oh.cn-beijing.maas.aliyuncs.com' port=443 local_address=None timeout=None socket_options=[(65535, 8, 1)]
2026-07-23 16:56:43 - httpcore.connection - DEBUG - connect_tcp.complete return_value=<httpcore._backends.sync.SyncStream object at 0x0000022D8A706A50>
2026-07-23 16:56:43 - httpcore.connection - DEBUG - start_tls.started ssl_context=<ssl.SSLContext object at 0x0000022DFFD1E570> server_hostname='ws-xfsvflr5yndg90oh.cn-beijing.maas.aliyuncs.com' timeout=None
2026-07-23 16:56:43 - httpcore.connection - DEBUG - start_tls.complete return_value=<httpcore._backends.sync.SyncStream object at 0x0000022D8A7193D0>
2026-07-23 16:56:43 - httpcore.http11 - DEBUG - send_request_headers.started request=<Request [b'POST']>
2026-07-23 16:56:43 - httpcore.http11 - DEBUG - send_request_headers.complete
2026-07-23 16:56:43 - httpcore.http11 - DEBUG - send_request_body.started request=<Request [b'POST']>
2026-07-23 16:56:43 - httpcore.http11 - DEBUG - send_request_body.complete
2026-07-23 16:56:43 - httpcore.http11 - DEBUG - receive_response_headers.started request=<Request [b'POST']>
2026-07-23 16:56:44 - httpcore.http11 - DEBUG - receive_response_headers.complete return_value=(b'HTTP/1.1', 200, b'OK', [(b'content-type', b'application/json; charset=utf-8'), (b'grpc-encoding', b'identity'), (b'grpc-accept-encoding', b'gzip'), (b'x-envoy-upstream-service-time', b'479'), (b'content-encoding', b'gzip'), (b'vary', b'Accept-Encoding'), (b'date', b'Thu, 23 Jul 2026 08:56:43 GMT'), (b'server', b'istio-envoy'), (b'x-request-id', b'9427fa2a-906d-92fd-aad2-f6536694ab48'), (b'req-cost-time', b'480'), (b'req-arrive-time', b'1784797003368'), (b'resp-start-time', b'1784797003849'), (b'transfer-encoding', b'chunked')])
2026-07-23 16:56:44 - httpx - INFO - HTTP Request: POST https://ws-xfsvflr5yndg90oh.cn-beijing.maas.aliyuncs.com/compatible-mode/v1/chat/completions "HTTP/1.1 200 OK"
2026-07-23 16:56:44 - httpcore.http11 - DEBUG - receive_response_body.started request=<Request [b'POST']>
2026-07-23 16:56:44 - httpcore.http11 - DEBUG - receive_response_body.complete
2026-07-23 16:56:44 - httpcore.http11 - DEBUG - response_closed.started
2026-07-23 16:56:44 - httpcore.http11 - DEBUG - response_closed.complete
2026-07-23 16:56:44 - openai._base_client - DEBUG - HTTP Response: POST https://ws-xfsvflr5yndg90oh.cn-beijing.maas.aliyuncs.com/compatible-mode/v1/chat/completions "200 OK" Headers({'content-type': 'application/json; charset=utf-8', 'grpc-encoding': 'identity', 'grpc-accept-encoding': 'gzip', 'x-envoy-upstream-service-time': '479', 'content-encoding': 'gzip', 'vary': 'Accept-Encoding', 'date': 'Thu, 23 Jul 2026 08:56:43 GMT', 'server': 'istio-envoy', 'x-request-id': '9427fa2a-906d-92fd-aad2-f6536694ab48', 'req-cost-time': '480', 'req-arrive-time': '1784797003368', 'resp-start-time': '1784797003849', 'transfer-encoding': 'chunked'})
2026-07-23 16:56:44 - openai._base_client - DEBUG - request_id: 9427fa2a-906d-92fd-aad2-f6536694ab48
2026-07-23 16:56:44 - app.services.llm_service - INFO - LLM response:
content='{\n    "item_names": ["苏伯尓M272Q显示器"],\n    "rewritten_query": "苏伯尓M272Q显示器怎么开机？"\n}' additional_kwargs={'parsed': None, 'refusal': None} response_metadata={'token_usage': {'completion_tokens': 40, 'prompt_tokens': 256, 'total_tokens': 296, 'completion_tokens_details': None, 'prompt_tokens_details': {'audio_tokens': None, 'cache_write_tokens': None, 'cached_tokens': 0}}, 'model_provider': 'openai', 'model_name': 'qwen-flash', 'system_fingerprint': None, 'id': 'chatcmpl-9427fa2a-906d-92fd-aad2-f6536694ab48', 'finish_reason': 'stop', 'logprobs': None} id='lc_run--019f8e31-0044-7e02-942e-55a49907df8a-0' tool_calls=[] invalid_tool_calls=[] usage_metadata={'input_tokens': 256, 'output_tokens': 40, 'total_tokens': 296, 'input_token_details': {'cache_read': 0}, 'output_token_details': {}}
2026-07-23 16:56:44 - datasets - DEBUG - PyTorch version 2.13.0 available.
2026-07-23 16:56:45,276 [WARNING][__init__]: Using fp16 with CPU can lead to runtime errors such as 'LayerNormKernelImpl', It's recommended to set 'use_fp16 = False' when using cpu.  (bge_m3.py:50)
2026-07-23 16:56:47 - FlagEmbedding.finetune.embedder.encoder_only.m3.runner - INFO - loading existing colbert_linear and sparse_linear---------
You're using a XLMRobertaTokenizerFast tokenizer. Please note that with a fast tokenizer, using the `__call__` method is faster than using a method to encode the text followed by a call to the `pad` method to get a padded encoding.
2026-07-23 16:56:49 - app.services.vectordb_service - INFO - Hybrid searching collection [kb_item_names] found 5 results
2026-07-23 16:56:49 - app.services.vectordb_service - INFO - Keyword [苏伯尓M272Q显示器] search result in vector db:
[
    [
        {
            "pk": 467721339624402732,
            "distance": 0.912263035774231,
            "entity": {
                "item_name": "苏伯尓M272Q显示器"
            }
        },
        {
            "pk": 467684978484127344,
            "distance": 0.7844224572181702,
            "entity": {
                "item_name": "苏伯尓B3-211H显示器"
            }
        },
        {
            "pk": 467844716533024051,
            "distance": 0.5843136310577393,
            "entity": {
                "item_name": "华为B530台式计算机"
            }
        },
        {
            "pk": 467844716533024105,
            "distance": 0.5812655687332153,
            "entity": {
                "item_name": "华为擎云B730"
            }
        },
        {
            "pk": 467865417353402144,
            "distance": 0.5776242613792419,
            "entity": {
                "item_name": "华为擎云W525主机"
            }
        }
    ]
]
2026-07-23 16:56:49 - import.node_item_name_confirm - INFO - LLM商品识别“苏伯尓M272Q显示器”检索到 1 个高置信度的结果，[{'item_name': '苏伯尓M272Q显示器', 'score': 0.912263035774231}]
2026-07-23 16:56:49 - pymongo.serverSelection - DEBUG - {"message": "Server selection started", "selector": "<function writable_server_selector at 0x0000022DFF7FFF60>", "operation": "update", "topologyDescription": "<TopologyDescription id: 6a61d74a5cfaff4cb8358ede, topology_type: Single, servers: [<ServerDescription ('192.168.222.8', 27017) server_type: Standalone, rtt: 0.015999999945051968>]>", "clientId": {"$oid": "6a61d74a5cfaff4cb8358ede"}}
2026-07-23 16:56:49 - pymongo.serverSelection - DEBUG - {"message": "Server selection succeeded", "selector": "<function writable_server_selector at 0x0000022DFF7FFF60>", "operation": "update", "topologyDescription": "<TopologyDescription id: 6a61d74a5cfaff4cb8358ede, topology_type: Single, servers: [<ServerDescription ('192.168.222.8', 27017) server_type: Standalone, rtt: 0.015999999945051968>]>", "clientId": {"$oid": "6a61d74a5cfaff4cb8358ede"}, "serverHost": "192.168.222.8", "serverPort": 27017}
2026-07-23 16:56:49 - pymongo.connection - DEBUG - {"message": "Connection checkout started", "clientId": {"$oid": "6a61d74a5cfaff4cb8358ede"}, "serverHost": "192.168.222.8", "serverPort": 27017}
2026-07-23 16:56:49 - pymongo.connection - DEBUG - {"message": "Connection checked out", "clientId": {"$oid": "6a61d74a5cfaff4cb8358ede"}, "serverHost": "192.168.222.8", "serverPort": 27017, "driverConnectionId": 1, "durationMS": 0.0}
2026-07-23 16:56:49 - pymongo.command - DEBUG - {"message": "Command started", "clientId": {"$oid": "6a61d74a5cfaff4cb8358ede"}, "command": "{\"update\": \"chat_message\", \"ordered\": true, \"lsid\": {\"id\": {\"$binary\": {\"base64\": \"I5pbKcywQP2KyNPuuWwxWA==\", \"subType\": \"04\"}}}, \"$db\": \"kb001\", \"updates\": [{\"q\": {\"_id\": {\"$oid\": \"6a61d74a5cfaff4cb8358edf\"}}, \"u\": {\"$set\": {\"session_id\": \"abc123\", \"role\": \"user\", \"text\": \"\\u534e\\u4e3a\\u663e\\u793a\\u5668\\u4e0d\\u4f1a\\u6363\\u9f13\\u548b\\u6574\", \"rewritten_query\": \"\\u82cf\\u4f2f\\u5c13M272Q\\u663e\\u793a\\u5668\\u600e\\u4e48\\u5f00\\u673a\\uff1f\", \"item_names\": [\"\\u82cf\\u4f2f\\u5c13M272Q\\u663e\\u793a\\u5668\"], \"ts\": 1784797009.21374}}}]}", "commandName": "update", "databaseName": "kb001", "requestId": 19169, "operationId": 19169, "driverConnectionId": 1, "serverConnectionId": 8, "serverHost": "192.168.222.8", "serverPort": 27017}
2026-07-23 16:56:49 - pymongo.command - DEBUG - {"message": "Command succeeded", "clientId": {"$oid": "6a61d74a5cfaff4cb8358ede"}, "durationMS": 3.012, "reply": "{\"n\": 1, \"nModified\": 1, \"ok\": 1.0}", "commandName": "update", "databaseName": "kb001", "requestId": 19169, "operationId": 19169, "driverConnectionId": 1, "serverConnectionId": 8, "serverHost": "192.168.222.8", "serverPort": 27017}
2026-07-23 16:56:49 - pymongo.connection - DEBUG - {"message": "Connection checked in", "clientId": {"$oid": "6a61d74a5cfaff4cb8358ede"}, "serverHost": "192.168.222.8", "serverPort": 27017, "driverConnectionId": 1}
2026-07-23 16:56:49 - app.services.mongo_service - INFO - Chat message updated: {'session_id': 'abc123', 'role': 'user', 'text': '华为显示器不会捣鼓咋整', 'rewritten_query': '苏伯尓M272Q显示器怎么开机？', 'item_names': ['苏伯尓M272Q显示器'], 'image_urls': None, 'ts': 1784797009.21374}
2026-07-23 16:56:49 - import.node_item_name_confirm - INFO - --- node_item_name_confirm done ---
2026-07-23 16:56:49 - root - INFO - {'history': [{'_id': ObjectId('6a5a22398da24fcbce12d0b7'), 'session_id': 'abc123', 'role': 'user', 'text': 'M272Q', 'rewritten_query': '苏伯尓M272Q显示器27寸显示器怎么开机？', 'item_names': ['苏伯尓M272Q显示器'], 'image_urls': None, 'ts': 1784291904.0104}, {'_id': ObjectId('6a5a1981687a46a2f25cba6e'), 'session_id': 'abc123', 'role': 'user', 'text': '27寸显示器怎么开机?', 'rewritten_query': '27寸显示器怎么开机？', 'item_names': ['苏伯尓M272Q显示器'], 'image_urls': None, 'ts': 1784289672.339298}, {'_id': ObjectId('6a5a1988687a46a2f25cba6f'), 'session_id': 'abc123', 'role': 'assistant', 'text': '您是想问以下哪个产品：苏伯尓M272Q显示器、苏伯尓B3-211H显示器？请明确一下型号。', 'rewritten_query': '', 'item_names': ['苏伯尓M272Q显示器'], 'image_urls': None, 'ts': 1784289672.336298}], 'rewritten_query': '苏伯尓M272Q显示器怎么开机？', 'item_names': ['苏伯尓M272Q显示器'], 'answer': ''}
2026-07-23 16:56:49 - pymongo.topology - DEBUG - {"message": "Server heartbeat failed", "topologyId": {"$oid": "6a61d74a5cfaff4cb8358ede"}, "serverHost": "192.168.222.8", "serverPort": 27017, "awaited": true, "durationMS": 6577.999999979511, "failure": "\"_OperationCancelled('operation cancelled')\"", "driverConnectionId": 1}
"""