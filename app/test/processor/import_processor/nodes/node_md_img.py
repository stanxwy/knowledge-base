from dotenv import load_dotenv
from app.utils.logger import setup_logging
from app.processor.import_processor.nodes.node_md_img import NodeMDImg

if __name__ == "__main__":
    load_dotenv(override=True)
    setup_logging()

    md_path = "./test_data/output/B3-211H/B3-211H.md"
    with open(md_path, "r", encoding="utf-8") as f:
        md_content = f.read()
    init_state = {
        "md_path": md_path,
        "md_content": md_content
    }
    node_md_img = NodeMDImg()
    node_md_img(init_state)

"""
(knowledge-base) PS D:\knowledge-base> python -m app.processor.import_processor.nodes.node_md_img
config loaded True...
ImportConfig instance not found...
creating ImportConfig instance...
2026-07-13 20:21:34 - import.node_md_img - INFO - --- node_md_img 开始 ---
2026-07-13 20:21:34 - import.node_md_img - DEBUG - 检查图片：501bb8d2d681e4502d87badb15a68939eadfa086d309c3599f1c36b0bc559177.jpg
2026-07-13 20:21:34 - import.node_md_img - DEBUG - 文档中找到图片 501bb8d2d681e4502d87badb15a68939eadfa086d309c3599f1c36b0bc559177.jpg 引用：2066-2146
2026-07-13 20:21:34 - import.node_md_img - DEBUG - 检查图片：5067b2891ca4f761e2874921e0eb433aa742afbf38ca8dc509afecbf0aa6a6b5.jpg
2026-07-13 20:21:34 - import.node_md_img - DEBUG - 文档中找到图片 5067b2891ca4f761e2874921e0eb433aa742afbf38ca8dc509afecbf0aa6a6b5.jpg 引用：3100-3180
2026-07-13 20:21:34 - import.node_md_img - DEBUG - 检查图片：677a08ee041965bbbdb6b483d6c17d5aaa36a26b6dc96870a2019f0307b8616f.jpg
2026-07-13 20:21:34 - import.node_md_img - DEBUG - 文档中找到图片 677a08ee041965bbbdb6b483d6c17d5aaa36a26b6dc96870a2019f0307b8616f.jpg 引用：0-80
2026-07-13 20:21:34 - import.node_md_img - DEBUG - 检查图片：8e839864036a7326885565163d99117ea943ecd29a656c85e7aa4052a9b9d28d.jpg
2026-07-13 20:21:34 - import.node_md_img - DEBUG - 文档中找到图片 8e839864036a7326885565163d99117ea943ecd29a656c85e7aa4052a9b9d28d.jpg 引用：3600-3680
2026-07-13 20:21:34 - import.node_md_img - DEBUG - 检查图片：c61a7f4e923881679f747508ae309c39dc221685344b068009256b1b3a40cc00.jpg
2026-07-13 20:21:34 - import.node_md_img - DEBUG - 文档中找到图片 c61a7f4e923881679f747508ae309c39dc221685344b068009256b1b3a40cc00.jpg 引用：3018-3098
2026-07-13 20:21:34 - import.node_md_img - DEBUG - 检查图片：cc5ee1ac24ebb2707d40dc7a234a8b243f55f5bf08fabc683859be6fdf096ffa.jpg
2026-07-13 20:21:34 - import.node_md_img - DEBUG - 文档中找到图片 cc5ee1ac24ebb2707d40dc7a234a8b243f55f5bf08fabc683859be6fdf096ffa.jpg 引用：3399-3479
2026-07-13 20:21:34 - import.node_md_img - DEBUG - 检查图片：d11bfff4c4658445e61ac557ef345593f56243b5a7b6956f952909e68eb69fea.jpg
2026-07-13 20:21:34 - import.node_md_img - DEBUG - 文档中未找到图片引用：d11bfff4c4658445e61ac557ef345593f56243b5a7b6956f952909e68eb69fea.jpg
2026-07-13 20:21:34 - import.node_md_img - WARNING - 图片未在MD中引用，跳过处理：d11bfff4c4658445e61ac557ef345593f56243b5a7b6956f952909e68eb69fea.jpg
2026-07-13 20:21:34 - import.node_md_img - DEBUG - 检查图片：f3349cded08d6686a93d0a81b9a64ec1e50d9a82cbb88541b37027f085813a15.jpg
2026-07-13 20:21:34 - import.node_md_img - DEBUG - 文档中找到图片 f3349cded08d6686a93d0a81b9a64ec1e50d9a82cbb88541b37027f085813a15.jpg 引用：1962-2042
2026-07-13 20:21:34 - import.node_md_img - INFO - 待处理图片数量：7
2026-07-13 20:21:34.235 | INFO     | app.utils.api_throttle:apply_api_rate_limit:39 - API请求时间戳已记录，当前60秒窗口内请求数：1
2026-07-13 20:21:34.989 | DEBUG    | app.utils.llm_utils:generate_image_caption:59 - 请求VLM生成图片总结 test_data\output\hak180\images\501bb8d2d681e4502d87badb15a68939eadfa086d309c3599f1c36b0bc559177.jpg
2026-07-13 20:21:35 - openai._base_client - DEBUG - Request options: {'method': 'post', 'url': '/chat/completions', 'headers': {'X-Stainless-Raw-Response': 'true'}, 'files': None, 'idempotency_key': 'stainless-python-retry-9cfd244f-e0f2-4808-b0e0-3895d21b36b5', 'security': {'bearer_auth': True}, 'content': None, 'json_data': {'messages': [{'content': [{'type': 'text', 'text': '这是"hak180"文件中的一张图片，图片上文部分为"images/f3349cded08d6686a93d0a81b9a64ec1e50d9a82cbb88541b37027f085813a15.jpg)  \n儎\u245fഴḽ䆜\u0a80ᛞ࠽व䀜\u1aae儎\u245fⲺ䇴༽䜞ԬȾ\n\n"，下文部分为"\n\n## 电源线\n\n•\t本设备通过 AC 220 V-240 V 50/60 Hz 电源供电。\n\n请勿将本设备连接到直流电源或逆变器（直流交流变换器）。存在火灾或触电的风险。\n\n•\t请勿用湿手触摸插头"，请用中文简要总结这张图片的内容，用于 Markdown 图片标题。尽量不要超过20个字'}, {'type': 'image_url', 'image_url': {'url': 'data:image/jpeg;base64,/'}}], 'role': 'user'}], 'model': 'qwen3-vl-flash', 'stream': False, 'temperature': 0.1}, 'extra_json': {'enable_thinking': False}}
2026-07-13 20:21:35 - openai._base_client - DEBUG - Sending HTTP Request: POST https://ws-xfsvflr5yndg90oh.cn-beijing.maas.aliyuncs.com/compatible-mode/v1/chat/completions
2026-07-13 20:21:35 - httpcore.connection - DEBUG - connect_tcp.started host='ws-xfsvflr5yndg90oh.cn-beijing.maas.aliyuncs.com' port=443 local_address=None timeout=None socket_options=[(65535, 8, 1)]
2026-07-13 20:21:35 - httpcore.connection - DEBUG - connect_tcp.complete return_value=<httpcore._backends.sync.SyncStream object at 0x00000221DD915010>
2026-07-13 20:21:35 - httpcore.connection - DEBUG - start_tls.started ssl_context=<ssl.SSLContext object at 0x00000221DBE2E2A0> server_hostname='ws-xfsvflr5yndg90oh.cn-beijing.maas.aliyuncs.com' timeout=None
2026-07-13 20:21:35 - httpcore.connection - DEBUG - start_tls.complete return_value=<httpcore._backends.sync.SyncStream object at 0x00000221DD914FD0>
2026-07-13 20:21:35 - httpcore.http11 - DEBUG - send_request_headers.started request=<Request [b'POST']>
2026-07-13 20:21:35 - httpcore.http11 - DEBUG - send_request_headers.complete
2026-07-13 20:21:35 - httpcore.http11 - DEBUG - send_request_body.started request=<Request [b'POST']>
2026-07-13 20:21:35 - httpcore.http11 - DEBUG - send_request_body.complete
2026-07-13 20:21:35 - httpcore.http11 - DEBUG - receive_response_headers.started request=<Request [b'POST']>
2026-07-13 20:21:35 - httpcore.http11 - DEBUG - receive_response_headers.complete return_value=(b'HTTP/1.1', 200, b'OK', [(b'content-type', b'application/json; charset=utf-8'), (b'grpc-encoding', b'identity'), (b'grpc-accept-encoding', b'gzip'), (b'x-envoy-upstream-service-time', b'300'), (b'content-encoding', b'gzip'), (b'vary', b'Accept-Encoding'), (b'date', b'Mon, 13 Jul 2026 12:21:35 GMT'), (b'server', b'istio-envoy'), (b'x-request-id', b'111c21c5-bca0-91bf-b77e-aaf4855459b6'), (b'req-cost-time', b'343'), (b'req-arrive-time', b'1783945295211'), (b'resp-start-time', b'1783945295554'), (b'transfer-encoding', b'chunked')])
2026-07-13 20:21:35 - httpx - INFO - HTTP Request: POST https://ws-xfsvflr5yndg90oh.cn-beijing.maas.aliyuncs.com/compatible-mode/v1/chat/completions "HTTP/1.1 200 OK"
2026-07-13 20:21:35 - httpcore.http11 - DEBUG - receive_response_body.started request=<Request [b'POST']>
2026-07-13 20:21:35 - httpcore.http11 - DEBUG - receive_response_body.complete
2026-07-13 20:21:35 - httpcore.http11 - DEBUG - response_closed.started
2026-07-13 20:21:35 - httpcore.http11 - DEBUG - response_closed.complete
2026-07-13 20:21:35 - openai._base_client - DEBUG - HTTP Response: POST https://ws-xfsvflr5yndg90oh.cn-beijing.maas.aliyuncs.com/compatible-mode/v1/chat/completions "200 OK" Headers({'content-type': 'application/json; charset=utf-8', 'grpc-encoding': 'identity', 'grpc-accept-encoding': 'gzip', 'x-envoy-upstream-service-time': '300', 'content-encoding': 'gzip', 'vary': 'Accept-Encoding', 'date': 'Mon, 13 Jul 2026 12:21:35 GMT', 'server': 'istio-envoy', 'x-request-id': '111c21c5-bca0-91bf-b77e-aaf4855459b6', 'req-cost-time': '343', 'req-arrive-time': '1783945295211', 'resp-start-time': '1783945295554', 'transfer-encoding': 'chunked'})
2026-07-13 20:21:35 - openai._base_client - DEBUG - request_id: 111c21c5-bca0-91bf-b77e-aaf4855459b6
2026-07-13 20:21:35.567 | INFO     | app.utils.llm_utils:generate_image_caption:61 - VLM生成图片 test_data\output\hak180\images\501bb8d2d681e4502d87badb15a68939eadfa086d309c3599f1c36b0bc559177.jpg 总结结果: 打印机内部部件操作示意图（手部插入组件）
2026-07-13 20:21:35.568 | INFO     | app.utils.api_throttle:apply_api_rate_limit:39 - API请求时间戳已记录，当前60秒窗口内请求数：2
2026-07-13 20:21:35.568 | DEBUG    | app.utils.llm_utils:generate_image_caption:59 - 请求VLM生成图片总结 test_data\output\hak180\images\5067b2891ca4f761e2874921e0eb433aa742afbf38ca8dc509afecbf0aa6a6b5.jpg
2026-07-13 20:21:35 - openai._base_client - DEBUG - Request options: {'method': 'post', 'url': '/chat/completions', 'headers': {'X-Stainless-Raw-Response': 'true'}, 'files': None, 'idempotency_key': 'stainless-python-retry-234d1aa4-9f2d-4392-b3f3-6d5acee108b6', 'security': {'bearer_auth': True}, 'content': None, 'json_data': {'messages': [{'content': [{'type': 'text', 'text': '这是"hak180"文件中的一张图片，图片上文部分为"免将手指放置在图中所示的区域中。\n\n![](images/c61a7f4e923881679f747508ae309c39dc221685344b068009256b1b3a40cc00.jpg)\n\n"，下文部分为"\n\n## 电源线\n\n•\t如果您长时间不会使用本设备，请从电源插座中拔掉电源线以确保安全。\n\n•\t本设备必须安装在可轻松使用电源插座的位置附近。如果发生意外情况，必须从电源插座中拔掉电源线以完全关闭电源"，请用中文简要总结这张图片的内容，用于 Markdown 图片标题。尽量不要超过20个字'}, {'type': 'image_url', 'image_url': {'url': 'data:image/jpeg;base64,/'}}], 'role': 'user'}], 'model': 'qwen3-vl-flash', 'stream': False, 'temperature': 0.1}, 'extra_json': {'enable_thinking': False}}
2026-07-13 20:21:35 - openai._base_client - DEBUG - Sending HTTP Request: POST https://ws-xfsvflr5yndg90oh.cn-beijing.maas.aliyuncs.com/compatible-mode/v1/chat/completions
2026-07-13 20:21:35 - httpcore.http11 - DEBUG - send_request_headers.started request=<Request [b'POST']>
2026-07-13 20:21:35 - httpcore.http11 - DEBUG - send_request_headers.complete
2026-07-13 20:21:35 - httpcore.http11 - DEBUG - send_request_body.started request=<Request [b'POST']>
2026-07-13 20:21:35 - httpcore.http11 - DEBUG - send_request_body.complete
2026-07-13 20:21:35 - httpcore.http11 - DEBUG - receive_response_headers.started request=<Request [b'POST']>
2026-07-13 20:21:35 - httpcore.http11 - DEBUG - receive_response_headers.complete return_value=(b'HTTP/1.1', 200, b'OK', [(b'content-type', b'application/json; charset=utf-8'), (b'grpc-encoding', b'identity'), (b'grpc-accept-encoding', b'gzip'), (b'x-envoy-upstream-service-time', b'269'), (b'content-encoding', b'gzip'), (b'vary', b'Accept-Encoding'), (b'date', b'Mon, 13 Jul 2026 12:21:35 GMT'), (b'server', b'istio-envoy'), (b'x-request-id', b'a2ccdf17-6aa3-940d-813b-ab6e8950a184'), (b'req-cost-time', b'271'), (b'req-arrive-time', b'1783945295618'), (b'resp-start-time', b'1783945295889'), (b'transfer-encoding', b'chunked')])
2026-07-13 20:21:35 - httpx - INFO - HTTP Request: POST https://ws-xfsvflr5yndg90oh.cn-beijing.maas.aliyuncs.com/compatible-mode/v1/chat/completions "HTTP/1.1 200 OK"
2026-07-13 20:21:35 - httpcore.http11 - DEBUG - receive_response_body.started request=<Request [b'POST']>
2026-07-13 20:21:35 - httpcore.http11 - DEBUG - receive_response_body.complete
2026-07-13 20:21:35 - httpcore.http11 - DEBUG - response_closed.started
2026-07-13 20:21:35 - httpcore.http11 - DEBUG - response_closed.complete
2026-07-13 20:21:35 - openai._base_client - DEBUG - HTTP Response: POST https://ws-xfsvflr5yndg90oh.cn-beijing.maas.aliyuncs.com/compatible-mode/v1/chat/completions "200 OK" Headers({'content-type': 'application/json; charset=utf-8', 'grpc-encoding': 'identity', 'grpc-accept-encoding': 'gzip', 'x-envoy-upstream-service-time': '269', 'content-encoding': 'gzip', 'vary': 'Accept-Encoding', 'date': 'Mon, 13 Jul 2026 12:21:35 GMT', 'server': 'istio-envoy', 'x-request-id': 'a2ccdf17-6aa3-940d-813b-ab6e8950a184', 'req-cost-time': '271', 'req-arrive-time': '1783945295618', 'resp-start-time': '1783945295889', 'transfer-encoding': 'chunked'})
2026-07-13 20:21:35 - openai._base_client - DEBUG - request_id: a2ccdf17-6aa3-940d-813b-ab6e8950a184
2026-07-13 20:21:35.889 | INFO     | app.utils.llm_utils:generate_image_caption:61 - VLM生成图片 test_data\output\hak180\images\5067b2891ca4f761e2874921e0eb433aa742afbf38ca8dc509afecbf0aa6a6b5.jpg 总结结果: 禁止将手指伸入设备指定区域
2026-07-13 20:21:35.889 | INFO     | app.utils.api_throttle:apply_api_rate_limit:39 - API请求时间戳已记录，当前60秒窗口内请求数：3
2026-07-13 20:21:35.890 | DEBUG    | app.utils.llm_utils:generate_image_caption:59 - 请求VLM生成图片总结 test_data\output\hak180\images\677a08ee041965bbbdb6b483d6c17d5aaa36a26b6dc96870a2019f0307b8616f.jpg
2026-07-13 20:21:35 - openai._base_client - DEBUG - Request options: {'method': 'post', 'url': '/chat/completions', 'headers': {'X-Stainless-Raw-Response': 'true'}, 'files': None, 'idempotency_key': 'stainless-python-retry-ff55f970-254d-4e97-a259-abfcccc2873f', 'security': {'bearer_auth': True}, 'content': None, 'json_data': {'messages': [{'content': [{'type': 'text', 'text': '这是"hak180"文件中的一张图片，图片上文部分为""，下文部分为"  \nD01WD7001-00\n\nSCHN\n\n## HAK 180 烫金机\n\n产品安全手册（简体中文）\n\n感谢您购买 HAK 180 烫金机。\n\n在使用本设备之前，请先阅读本手册，包括所有预防措施。阅"，请用中文简要总结这张图片的内容，用于 Markdown 图片标题。尽量不要超过20个字'}, {'type': 'image_url', 'image_url': {'url': 'data:image/jpeg;base64,/'}}], 'role': 'user'}], 'model': 'qwen3-vl-flash', 'stream': False, 'temperature': 0.1}, 'extra_json': {'enable_thinking': False}}
2026-07-13 20:21:35 - openai._base_client - DEBUG - Sending HTTP Request: POST https://ws-xfsvflr5yndg90oh.cn-beijing.maas.aliyuncs.com/compatible-mode/v1/chat/completions
2026-07-13 20:21:35 - httpcore.http11 - DEBUG - send_request_headers.started request=<Request [b'POST']>
2026-07-13 20:21:35 - httpcore.http11 - DEBUG - send_request_headers.complete
2026-07-13 20:21:35 - httpcore.http11 - DEBUG - send_request_body.started request=<Request [b'POST']>
2026-07-13 20:21:35 - httpcore.http11 - DEBUG - send_request_body.complete
2026-07-13 20:21:35 - httpcore.http11 - DEBUG - receive_response_headers.started request=<Request [b'POST']>
2026-07-13 20:21:36 - httpcore.http11 - DEBUG - receive_response_headers.complete return_value=(b'HTTP/1.1', 200, b'OK', [(b'content-type', b'application/json; charset=utf-8'), (b'grpc-encoding', b'identity'), (b'grpc-accept-encoding', b'gzip'), (b'x-envoy-upstream-service-time', b'453'), (b'content-encoding', b'gzip'), (b'vary', b'Accept-Encoding'), (b'date', b'Mon, 13 Jul 2026 12:21:35 GMT'), (b'server', b'istio-envoy'), (b'x-request-id', b'ae5fb4c3-a7d2-9e97-b796-6a2e2cfc204e'), (b'req-cost-time', b'454'), (b'req-arrive-time', b'1783945295937'), (b'resp-start-time', b'1783945296392'), (b'transfer-encoding', b'chunked')])
2026-07-13 20:21:36 - httpx - INFO - HTTP Request: POST https://ws-xfsvflr5yndg90oh.cn-beijing.maas.aliyuncs.com/compatible-mode/v1/chat/completions "HTTP/1.1 200 OK"
2026-07-13 20:21:36 - httpcore.http11 - DEBUG - receive_response_body.started request=<Request [b'POST']>
2026-07-13 20:21:36 - httpcore.http11 - DEBUG - receive_response_body.complete
2026-07-13 20:21:36 - httpcore.http11 - DEBUG - response_closed.started
2026-07-13 20:21:36 - httpcore.http11 - DEBUG - response_closed.complete
2026-07-13 20:21:36 - openai._base_client - DEBUG - HTTP Response: POST https://ws-xfsvflr5yndg90oh.cn-beijing.maas.aliyuncs.com/compatible-mode/v1/chat/completions "200 OK" Headers({'content-type': 'application/json; charset=utf-8', 'grpc-encoding': 'identity', 'grpc-accept-encoding': 'gzip', 'x-envoy-upstream-service-time': '453', 'content-encoding': 'gzip', 'vary': 'Accept-Encoding', 'date': 'Mon, 13 Jul 2026 12:21:35 GMT', 'server': 'istio-envoy', 'x-request-id': 'ae5fb4c3-a7d2-9e97-b796-6a2e2cfc204e', 'req-cost-time': '454', 'req-arrive-time': '1783945295937', 'resp-start-time': '1783945296392', 'transfer-encoding': 'chunked'})
2026-07-13 20:21:36 - openai._base_client - DEBUG - request_id: ae5fb4c3-a7d2-9e97-b796-6a2e2cfc204e
2026-07-13 20:21:36.393 | INFO     | app.utils.llm_utils:generate_image_caption:61 - VLM生成图片 test_data\output\hak180\images\677a08ee041965bbbdb6b483d6c17d5aaa36a26b6dc96870a2019f0307b8616f.jpg 总结结果: HAK 180 烫金机产品安全手册封面条形码
2026-07-13 20:21:36.393 | INFO     | app.utils.api_throttle:apply_api_rate_limit:39 - API请求时间戳已记录，当前60秒窗口内请求数：4
2026-07-13 20:21:36.394 | DEBUG    | app.utils.llm_utils:generate_image_caption:59 - 请求VLM生成图片总结 test_data\output\hak180\images\8e839864036a7326885565163d99117ea943ecd29a656c85e7aa4052a9b9d28d.jpg
2026-07-13 20:21:36 - openai._base_client - DEBUG - Request options: {'method': 'post', 'url': '/chat/completions', 'headers': {'X-Stainless-Raw-Response': 'true'}, 'files': None, 'idempotency_key': 'stainless-python-retry-1f063167-f6f3-4359-9004-106d07e4c92a', 'security': {'bearer_auth': True}, 'content': None, 'json_data': {'messages': [{'content': [{'type': 'text', 'text': '这是"hak180"文件中的一张图片，图片上文部分为"的桌面或支架。特别是当本设备位于桌面、支架等边缘时，请勿让出纸盒打开。确保本设备位于平整、水平且稳定的表面上，避免震动。不遵守这些预防措施可能导致设备跌落，从而导致用户的人身伤害以及设备严重损坏。\n\n"，下文部分为"\n\n“重要事项”表示可能导致财产损失或本设备功能丧失的潜在危险情况。\n\n## 设备\n\n如果遵守了操作说明进行操作，但是设备不能正确运行，请仅调整操作说明中涵盖的控制。错误调整其他控制可能导致损坏并且通"，请用中文简要总结这张图片的内容，用于 Markdown 图片标题。尽量不要超过20个字'}, {'type': 'image_url', 'image_url': {'url': 'data:image/jpeg;base64,/'}}], 'role': 'user'}], 'model': 'qwen3-vl-flash', 'stream': False, 'temperature': 0.1}, 'extra_json': {'enable_thinking': False}}
2026-07-13 20:21:36 - openai._base_client - DEBUG - Sending HTTP Request: POST https://ws-xfsvflr5yndg90oh.cn-beijing.maas.aliyuncs.com/compatible-mode/v1/chat/completions
2026-07-13 20:21:36 - httpcore.http11 - DEBUG - send_request_headers.started request=<Request [b'POST']>
2026-07-13 20:21:36 - httpcore.http11 - DEBUG - send_request_headers.complete
2026-07-13 20:21:36 - httpcore.http11 - DEBUG - send_request_body.started request=<Request [b'POST']>
2026-07-13 20:21:36 - httpcore.http11 - DEBUG - send_request_body.complete
2026-07-13 20:21:36 - httpcore.http11 - DEBUG - receive_response_headers.started request=<Request [b'POST']>
2026-07-13 20:21:37 - httpcore.http11 - DEBUG - receive_response_headers.complete return_value=(b'HTTP/1.1', 200, b'OK', [(b'content-type', b'application/json; charset=utf-8'), (b'grpc-encoding', b'identity'), (b'grpc-accept-encoding', b'gzip'), (b'x-envoy-upstream-service-time', b'1203'), (b'content-encoding', b'gzip'), (b'vary', b'Accept-Encoding'), (b'date', b'Mon, 13 Jul 2026 12:21:37 GMT'), (b'server', b'istio-envoy'), (b'x-request-id', b'5e10165a-2a79-943f-a860-78a7352c4c8e'), (b'req-cost-time', b'1207'), (b'req-arrive-time', b'1783945296444'), (b'resp-start-time', b'1783945297652'), (b'transfer-encoding', b'chunked')])
2026-07-13 20:21:37 - httpx - INFO - HTTP Request: POST https://ws-xfsvflr5yndg90oh.cn-beijing.maas.aliyuncs.com/compatible-mode/v1/chat/completions "HTTP/1.1 200 OK"
2026-07-13 20:21:37 - httpcore.http11 - DEBUG - receive_response_body.started request=<Request [b'POST']>
2026-07-13 20:21:37 - httpcore.http11 - DEBUG - receive_response_body.complete
2026-07-13 20:21:37 - httpcore.http11 - DEBUG - response_closed.started
2026-07-13 20:21:37 - httpcore.http11 - DEBUG - response_closed.complete
2026-07-13 20:21:37 - openai._base_client - DEBUG - HTTP Response: POST https://ws-xfsvflr5yndg90oh.cn-beijing.maas.aliyuncs.com/compatible-mode/v1/chat/completions "200 OK" Headers({'content-type': 'application/json; charset=utf-8', 'grpc-encoding': 'identity', 'grpc-accept-encoding': 'gzip', 'x-envoy-upstream-service-time': '1203', 'content-encoding': 'gzip', 'vary': 'Accept-Encoding', 'date': 'Mon, 13 Jul 2026 12:21:37 GMT', 'server': 'istio-envoy', 'x-request-id': '5e10165a-2a79-943f-a860-78a7352c4c8e', 'req-cost-time': '1207', 'req-arrive-time': '1783945296444', 'resp-start-time': '1783945297652', 'transfer-encoding': 'chunked'})
2026-07-13 20:21:37 - openai._base_client - DEBUG - request_id: 5e10165a-2a79-943f-a860-78a7352c4c8e
2026-07-13 20:21:37.654 | INFO     | app.utils.llm_utils:generate_image_caption:61 - VLM生成图片 test_data\output\hak180\images\8e839864036a7326885565163d99117ea943ecd29a656c85e7aa4052a9b9d28d.jpg 总结结果: 禁止将设备置于桌面边缘，防止跌落损坏或伤人。
2026-07-13 20:21:37.654 | INFO     | app.utils.api_throttle:apply_api_rate_limit:39 - API请求时间戳已记录，当前60秒窗口内请求数：5
2026-07-13 20:21:37.655 | DEBUG    | app.utils.llm_utils:generate_image_caption:59 - 请求VLM生成图片总结 test_data\output\hak180\images\c61a7f4e923881679f747508ae309c39dc221685344b068009256b1b3a40cc00.jpg
2026-07-13 20:21:37 - openai._base_client - DEBUG - Request options: {'method': 'post', 'url': '/chat/completions', 'headers': {'X-Stainless-Raw-Response': 'true'}, 'files': None, 'idempotency_key': 'stainless-python-retry-fbf1b22c-9ef7-444a-8143-4be994a6f87b', 'security': {'bearer_auth': True}, 'content': None, 'json_data': {'messages': [{'content': [{'type': 'text', 'text': '这是"hak180"文件中的一张图片，图片上文部分为"## 设备\n\n•\t将本设备放置在平整、水平且稳定的表面上（如桌面），避免震动和冲击。\n\n•\t将本设备放置在通风良好的环境中。\n\n•\t为了防止人员受伤，请谨慎操作，避免将手指放置在图中所示的区域中。\n\n"，下文部分为"\n\n![](images/5067b2891ca4f761e2874921e0eb433aa742afbf38ca8dc509afecbf0aa6a6b5.jpg)\n\n## 电源线\n\n•\t如果您长时间"，请用中文简要总结这张图片的内容，用于 Markdown 图片标题。尽量不要超过20个字'}, {'type': 'image_url', 'image_url': {'url': 'data:image/jpeg;base64,/'}}], 'role': 'user'}], 'model': 'qwen3-vl-flash', 'stream': False, 'temperature': 0.1}, 'extra_json': {'enable_thinking': False}}
2026-07-13 20:21:37 - openai._base_client - DEBUG - Sending HTTP Request: POST https://ws-xfsvflr5yndg90oh.cn-beijing.maas.aliyuncs.com/compatible-mode/v1/chat/completions
2026-07-13 20:21:37 - httpcore.http11 - DEBUG - send_request_headers.started request=<Request [b'POST']>
2026-07-13 20:21:37 - httpcore.http11 - DEBUG - send_request_headers.complete
2026-07-13 20:21:37 - httpcore.http11 - DEBUG - send_request_body.started request=<Request [b'POST']>
2026-07-13 20:21:37 - httpcore.http11 - DEBUG - send_request_body.complete
2026-07-13 20:21:37 - httpcore.http11 - DEBUG - receive_response_headers.started request=<Request [b'POST']>
2026-07-13 20:21:38 - httpcore.http11 - DEBUG - receive_response_headers.complete return_value=(b'HTTP/1.1', 200, b'OK', [(b'content-type', b'application/json; charset=utf-8'), (b'grpc-encoding', b'identity'), (b'grpc-accept-encoding', b'gzip'), (b'x-envoy-upstream-service-time', b'320'), (b'content-encoding', b'gzip'), (b'vary', b'Accept-Encoding'), (b'date', b'Mon, 13 Jul 2026 12:21:37 GMT'), (b'server', b'istio-envoy'), (b'x-request-id', b'bb0f9595-ea34-9f4d-aedc-2a4282b7bc57'), (b'req-cost-time', b'324'), (b'req-arrive-time', b'1783945297706'), (b'resp-start-time', b'1783945298030'), (b'transfer-encoding', b'chunked')])
2026-07-13 20:21:38 - httpx - INFO - HTTP Request: POST https://ws-xfsvflr5yndg90oh.cn-beijing.maas.aliyuncs.com/compatible-mode/v1/chat/completions "HTTP/1.1 200 OK"
2026-07-13 20:21:38 - httpcore.http11 - DEBUG - receive_response_body.started request=<Request [b'POST']>
2026-07-13 20:21:38 - httpcore.http11 - DEBUG - receive_response_body.complete
2026-07-13 20:21:38 - httpcore.http11 - DEBUG - response_closed.started
2026-07-13 20:21:38 - httpcore.http11 - DEBUG - response_closed.complete
2026-07-13 20:21:38 - openai._base_client - DEBUG - HTTP Response: POST https://ws-xfsvflr5yndg90oh.cn-beijing.maas.aliyuncs.com/compatible-mode/v1/chat/completions "200 OK" Headers({'content-type': 'application/json; charset=utf-8', 'grpc-encoding': 'identity', 'grpc-accept-encoding': 'gzip', 'x-envoy-upstream-service-time': '320', 'content-encoding': 'gzip', 'vary': 'Accept-Encoding', 'date': 'Mon, 13 Jul 2026 12:21:37 GMT', 'server': 'istio-envoy', 'x-request-id': 'bb0f9595-ea34-9f4d-aedc-2a4282b7bc57', 'req-cost-time': '324', 'req-arrive-time': '1783945297706', 'resp-start-time': '1783945298030', 'transfer-encoding': 'chunked'})
2026-07-13 20:21:38 - openai._base_client - DEBUG - request_id: bb0f9595-ea34-9f4d-aedc-2a4282b7bc57
2026-07-13 20:21:38.035 | INFO     | app.utils.llm_utils:generate_image_caption:61 - VLM生成图片 test_data\output\hak180\images\c61a7f4e923881679f747508ae309c39dc221685344b068009256b1b3a40cc00.jpg 总结结果: 禁止将手指伸入设备内部齿轮区域
2026-07-13 20:21:38.035 | INFO     | app.utils.api_throttle:apply_api_rate_limit:39 - API请求时间戳已记录，当前60秒窗口内请求数：6
2026-07-13 20:21:38.036 | DEBUG    | app.utils.llm_utils:generate_image_caption:59 - 请求VLM生成图片总结 test_data\output\hak180\images\cc5ee1ac24ebb2707d40dc7a234a8b243f55f5bf08fabc683859be6fdf096ffa.jpg
2026-07-13 20:21:38 - openai._base_client - DEBUG - Request options: {'method': 'post', 'url': '/chat/completions', 'headers': {'X-Stainless-Raw-Response': 'true'}, 'files': None, 'idempotency_key': 'stainless-python-retry-977e8bcc-7055-471f-8575-5c2fd7018d74', 'security': {'bearer_auth': True}, 'content': None, 'json_data': {'messages': [{'content': [{'type': 'text', 'text': '这是"hak180"文件中的一张图片，图片上文部分为"利的边缘可能导致受伤。\n\n## 为设备选择一个安全的位置\n\n•\t提起本设备时，请使用双手抓稳本设备的两侧。如果抓住的是进纸托板和出纸盒，它们可能会掉下来。必须通过将双手放在本设备下面来搬运本设备。\n\n"，下文部分为"  \n确保本设备的任何部位均未伸出设备所在的桌面或支架。特别是当本设备位于桌面、支架等边缘时，请勿让出纸盒打开。确保本设备位于平整、水平且稳定的表面上，避免震动。不遵守这些预防措施可能导致设备跌落，从"，请用中文简要总结这张图片的内容，用于 Markdown 图片标题。尽量不要超过20个字'}, {'type': 'image_url', 'image_url': {'url': 'data:image/jpeg;base64,/'}}], 'role': 'user'}], 'model': 'qwen3-vl-flash', 'stream': False, 'temperature': 0.1}, 'extra_json': {'enable_thinking': False}}
2026-07-13 20:21:38 - openai._base_client - DEBUG - Sending HTTP Request: POST https://ws-xfsvflr5yndg90oh.cn-beijing.maas.aliyuncs.com/compatible-mode/v1/chat/completions
2026-07-13 20:21:38 - httpcore.http11 - DEBUG - send_request_headers.started request=<Request [b'POST']>
2026-07-13 20:21:38 - httpcore.http11 - DEBUG - send_request_headers.complete
2026-07-13 20:21:38 - httpcore.http11 - DEBUG - send_request_body.started request=<Request [b'POST']>
2026-07-13 20:21:38 - httpcore.http11 - DEBUG - send_request_body.complete
2026-07-13 20:21:38 - httpcore.http11 - DEBUG - receive_response_headers.started request=<Request [b'POST']>
2026-07-13 20:21:38 - httpcore.http11 - DEBUG - receive_response_headers.complete return_value=(b'HTTP/1.1', 200, b'OK', [(b'content-type', b'application/json; charset=utf-8'), (b'grpc-encoding', b'identity'), (b'grpc-accept-encoding', b'gzip'), (b'x-envoy-upstream-service-time', b'304'), (b'content-encoding', b'gzip'), (b'vary', b'Accept-Encoding'), (b'date', b'Mon, 13 Jul 2026 12:21:38 GMT'), (b'server', b'istio-envoy'), (b'x-request-id', b'560f20c3-dba1-91b8-8fed-aebae60de6a8'), (b'req-cost-time', b'307'), (b'req-arrive-time', b'1783945298085'), (b'resp-start-time', b'1783945298393'), (b'transfer-encoding', b'chunked')])
2026-07-13 20:21:38 - httpx - INFO - HTTP Request: POST https://ws-xfsvflr5yndg90oh.cn-beijing.maas.aliyuncs.com/compatible-mode/v1/chat/completions "HTTP/1.1 200 OK"
2026-07-13 20:21:38 - httpcore.http11 - DEBUG - receive_response_body.started request=<Request [b'POST']>
2026-07-13 20:21:38 - httpcore.http11 - DEBUG - receive_response_body.complete
2026-07-13 20:21:38 - httpcore.http11 - DEBUG - response_closed.started
2026-07-13 20:21:38 - httpcore.http11 - DEBUG - response_closed.complete
2026-07-13 20:21:38 - openai._base_client - DEBUG - HTTP Response: POST https://ws-xfsvflr5yndg90oh.cn-beijing.maas.aliyuncs.com/compatible-mode/v1/chat/completions "200 OK" Headers({'content-type': 'application/json; charset=utf-8', 'grpc-encoding': 'identity', 'grpc-accept-encoding': 'gzip', 'x-envoy-upstream-service-time': '304', 'content-encoding': 'gzip', 'vary': 'Accept-Encoding', 'date': 'Mon, 13 Jul 2026 12:21:38 GMT', 'server': 'istio-envoy', 'x-request-id': '560f20c3-dba1-91b8-8fed-aebae60de6a8', 'req-cost-time': '307', 'req-arrive-time': '1783945298085', 'resp-start-time': '1783945298393', 'transfer-encoding': 'chunked'})
2026-07-13 20:21:38 - openai._base_client - DEBUG - request_id: 560f20c3-dba1-91b8-8fed-aebae60de6a8
2026-07-13 20:21:38.394 | INFO     | app.utils.llm_utils:generate_image_caption:61 - VLM生成图片 test_data\output\hak180\images\cc5ee1ac24ebb2707d40dc7a234a8b243f55f5bf08fabc683859be6fdf096ffa.jpg 总结结果: 正确与错误的设备搬运方式示意图
2026-07-13 20:21:38.394 | INFO     | app.utils.api_throttle:apply_api_rate_limit:39 - API请求时间戳已记录，当前60秒窗口内请求数：7
2026-07-13 20:21:38.395 | DEBUG    | app.utils.llm_utils:generate_image_caption:59 - 请求VLM生成图片总结 test_data\output\hak180\images\f3349cded08d6686a93d0a81b9a64ec1e50d9a82cbb88541b37027f085813a15.jpg
2026-07-13 20:21:38 - openai._base_client - DEBUG - Request options: {'method': 'post', 'url': '/chat/completions', 'headers': {'X-Stainless-Raw-Response': 'true'}, 'files': None, 'idempotency_key': 'stainless-python-retry-e49e4970-f979-4399-95e7-6541244b0be2', 'security': {'bearer_auth': True}, 'content': None, 'json_data': {'messages': [{'content': [{'type': 'text', 'text': '这是"hak180"文件中的一张图片，图片上文部分为"请远离本设备，并立即咨询医生。\n\n•\t使用本设备之后短时间内，本设备的一些内部零件仍然处于极热状态。打开前盖时，请勿触摸以灰色标记的区域。存在烧伤的风险。先等待设备冷却下来，再触摸设备的内部零件。\n\n"，下文部分为"  \n儎\u245fഴḽ䆜\u0a80ᛞ࠽व䀜\u1aae儎\u245fⲺ䇴༽䜞ԬȾ\n\n![](images/501bb8d2d681e4502d87badb15a68939eadfa086d309c3599f1c36b0bc559177."，请用中文简要总结这张图片的内容，用于 Markdown 图片标题。尽量不要超过20个字'}, {'type': 'image_url', 'image_url': {'url': 'data:image/jpeg;base64,/'}}], 'role': 'user'}], 'model': 'qwen3-vl-flash', 'stream': False, 'temperature': 0.1}, 'extra_json': {'enable_thinking': False}}
2026-07-13 20:21:38 - openai._base_client - DEBUG - Sending HTTP Request: POST https://ws-xfsvflr5yndg90oh.cn-beijing.maas.aliyuncs.com/compatible-mode/v1/chat/completions
2026-07-13 20:21:38 - httpcore.http11 - DEBUG - send_request_headers.started request=<Request [b'POST']>
2026-07-13 20:21:38 - httpcore.http11 - DEBUG - send_request_headers.complete
2026-07-13 20:21:38 - httpcore.http11 - DEBUG - send_request_body.started request=<Request [b'POST']>
2026-07-13 20:21:38 - httpcore.http11 - DEBUG - send_request_body.complete
2026-07-13 20:21:38 - httpcore.http11 - DEBUG - receive_response_headers.started request=<Request [b'POST']>
2026-07-13 20:21:38 - httpcore.http11 - DEBUG - receive_response_headers.complete return_value=(b'HTTP/1.1', 200, b'OK', [(b'content-type', b'application/json; charset=utf-8'), (b'grpc-encoding', b'identity'), (b'grpc-accept-encoding', b'gzip'), (b'x-envoy-upstream-service-time', b'339'), (b'content-encoding', b'gzip'), (b'vary', b'Accept-Encoding'), (b'date', b'Mon, 13 Jul 2026 12:21:38 GMT'), (b'server', b'istio-envoy'), (b'x-request-id', b'fa3e1256-9a31-9d18-b412-a9def22c5898'), (b'req-cost-time', b'345'), (b'req-arrive-time', b'1783945298446'), (b'resp-start-time', b'1783945298791'), (b'transfer-encoding', b'chunked')])
2026-07-13 20:21:38 - httpx - INFO - HTTP Request: POST https://ws-xfsvflr5yndg90oh.cn-beijing.maas.aliyuncs.com/compatible-mode/v1/chat/completions "HTTP/1.1 200 OK"
2026-07-13 20:21:38 - httpcore.http11 - DEBUG - receive_response_body.started request=<Request [b'POST']>
2026-07-13 20:21:38 - httpcore.http11 - DEBUG - receive_response_body.complete
2026-07-13 20:21:38 - httpcore.http11 - DEBUG - response_closed.started
2026-07-13 20:21:38 - httpcore.http11 - DEBUG - response_closed.complete
2026-07-13 20:21:38 - openai._base_client - DEBUG - HTTP Response: POST https://ws-xfsvflr5yndg90oh.cn-beijing.maas.aliyuncs.com/compatible-mode/v1/chat/completions "200 OK" Headers({'content-type': 'application/json; charset=utf-8', 'grpc-encoding': 'identity', 'grpc-accept-encoding': 'gzip', 'x-envoy-upstream-service-time': '339', 'content-encoding': 'gzip', 'vary': 'Accept-Encoding', 'date': 'Mon, 13 Jul 2026 12:21:38 GMT', 'server': 'istio-envoy', 'x-request-id': 'fa3e1256-9a31-9d18-b412-a9def22c5898', 'req-cost-time': '345', 'req-arrive-time': '1783945298446', 'resp-start-time': '1783945298791', 'transfer-encoding': 'chunked'})
2026-07-13 20:21:38 - openai._base_client - DEBUG - request_id: fa3e1256-9a31-9d18-b412-a9def22c5898
2026-07-13 20:21:38.793 | INFO     | app.utils.llm_utils:generate_image_caption:61 - VLM生成图片 test_data\output\hak180\images\f3349cded08d6686a93d0a81b9a64ec1e50d9a82cbb88541b37027f085813a15.jpg 总结结果: 设备高温警告：勿触灰色区域，待冷却后再操作
2026-07-13 20:21:38 - urllib3.connectionpool - DEBUG - http://192.168.245.133:9000 "GET /knowledge-base?delimiter=&encoding-type=url&list-type=2&max-keys=1000&prefix=upload-images%2Fhak180 HTTP/1.1" 200 0
2026-07-13 20:21:38 - urllib3.connectionpool - DEBUG - http://192.168.245.133:9000 "POST /knowledge-base?delete= HTTP/1.1" 200 0
2026-07-13 20:21:38 - urllib3.connectionpool - DEBUG - http://192.168.245.133:9000 "PUT /knowledge-base/upload-images/hak180/501bb8d2d681e4502d87badb15a68939eadfa086d309c3599f1c36b0bc559177.jpg HTTP/1.1" 200 0
2026-07-13 20:21:38 - import.node_md_img - DEBUG - 图片 501bb8d2d681e4502d87badb15a68939eadfa086d309c3599f1c36b0bc559177.jpg 上传成功 http://192.168.245.133:9000/knowledge-base/upload-images/hak180/501bb8d2d681e4502d87badb15a68939eadfa086d309c3599f1c36b0bc559177.jpg
2026-07-13 20:21:38 - urllib3.connectionpool - DEBUG - http://192.168.245.133:9000 "PUT /knowledge-base/upload-images/hak180/5067b2891ca4f761e2874921e0eb433aa742afbf38ca8dc509afecbf0aa6a6b5.jpg HTTP/1.1" 200 0
2026-07-13 20:21:38 - import.node_md_img - DEBUG - 图片 5067b2891ca4f761e2874921e0eb433aa742afbf38ca8dc509afecbf0aa6a6b5.jpg 上传成功 http://192.168.245.133:9000/knowledge-base/upload-images/hak180/5067b2891ca4f761e2874921e0eb433aa742afbf38ca8dc509afecbf0aa6a6b5.jpg
2026-07-13 20:21:38 - urllib3.connectionpool - DEBUG - http://192.168.245.133:9000 "PUT /knowledge-base/upload-images/hak180/677a08ee041965bbbdb6b483d6c17d5aaa36a26b6dc96870a2019f0307b8616f.jpg HTTP/1.1" 200 0
2026-07-13 20:21:38 - import.node_md_img - DEBUG - 图片 677a08ee041965bbbdb6b483d6c17d5aaa36a26b6dc96870a2019f0307b8616f.jpg 上传成功 http://192.168.245.133:9000/knowledge-base/upload-images/hak180/677a08ee041965bbbdb6b483d6c17d5aaa36a26b6dc96870a2019f0307b8616f.jpg
2026-07-13 20:21:38 - urllib3.connectionpool - DEBUG - http://192.168.245.133:9000 "PUT /knowledge-base/upload-images/hak180/8e839864036a7326885565163d99117ea943ecd29a656c85e7aa4052a9b9d28d.jpg HTTP/1.1" 200 0
2026-07-13 20:21:38 - import.node_md_img - DEBUG - 图片 8e839864036a7326885565163d99117ea943ecd29a656c85e7aa4052a9b9d28d.jpg 上传成功 http://192.168.245.133:9000/knowledge-base/upload-images/hak180/8e839864036a7326885565163d99117ea943ecd29a656c85e7aa4052a9b9d28d.jpg
2026-07-13 20:21:38 - urllib3.connectionpool - DEBUG - http://192.168.245.133:9000 "PUT /knowledge-base/upload-images/hak180/c61a7f4e923881679f747508ae309c39dc221685344b068009256b1b3a40cc00.jpg HTTP/1.1" 200 0
2026-07-13 20:21:38 - import.node_md_img - DEBUG - 图片 c61a7f4e923881679f747508ae309c39dc221685344b068009256b1b3a40cc00.jpg 上传成功 http://192.168.245.133:9000/knowledge-base/upload-images/hak180/c61a7f4e923881679f747508ae309c39dc221685344b068009256b1b3a40cc00.jpg
2026-07-13 20:21:38 - urllib3.connectionpool - DEBUG - http://192.168.245.133:9000 "PUT /knowledge-base/upload-images/hak180/cc5ee1ac24ebb2707d40dc7a234a8b243f55f5bf08fabc683859be6fdf096ffa.jpg HTTP/1.1" 200 0
2026-07-13 20:21:38 - import.node_md_img - DEBUG - 图片 cc5ee1ac24ebb2707d40dc7a234a8b243f55f5bf08fabc683859be6fdf096ffa.jpg 上传成功 http://192.168.245.133:9000/knowledge-base/upload-images/hak180/cc5ee1ac24ebb2707d40dc7a234a8b243f55f5bf08fabc683859be6fdf096ffa.jpg
2026-07-13 20:21:38 - urllib3.connectionpool - DEBUG - http://192.168.245.133:9000 "PUT /knowledge-base/upload-images/hak180/f3349cded08d6686a93d0a81b9a64ec1e50d9a82cbb88541b37027f085813a15.jpg HTTP/1.1" 200 0
2026-07-13 20:21:38 - import.node_md_img - DEBUG - 图片 f3349cded08d6686a93d0a81b9a64ec1e50d9a82cbb88541b37027f085813a15.jpg 上传成功 http://192.168.245.133:9000/knowledge-base/upload-images/hak180/f3349cded08d6686a93d0a81b9a64ec1e50d9a82cbb88541b37027f085813a15.jpg
2026-07-13 20:21:38 - import.node_md_img - INFO - 7张图片上传完成
2026-07-13 20:21:38 - import.node_md_img - INFO - MD文件图片引用替换完成，共替换7处图片引用
2026-07-13 20:21:38 - import.node_md_img - INFO - 处理后MD文件已保存，新文件路径：./test_data/output/hak180/hak180_new.md
2026-07-13 20:21:38 - import.node_md_img - INFO - --- node_md_img 完成 ---
2026-07-13 20:21:38 - root - INFO - {
    "md_path": "./test_data/output/hak180/hak180_new.md",
    "md_content": "![HAK 180 烫金机产品安全手册封面条形码](http://192.168.245.133:9000/knowledge-base/upload-images/hak180/677a08ee041965bbbdb6b483d6c17d5aaa36a26b6dc96870a2019f0307b8616f.jpg)..."
}
(knowledge-base) PS D:\knowledge-base>
"""