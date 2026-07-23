from dotenv import load_dotenv
load_dotenv(override=True)

from app.utils.logger import setup_logging
from app.processor.query_processor.nodes.node_web_search_mcp import NodeWebSearchMcp

if __name__ == "__main__":
    logger = setup_logging("DEBUG")

    init_state = {
        "rewritten_query": "关于brother HAK180烫金机，如何调节转印温度？"
    }
    node_web_search_mcp = NodeWebSearchMcp()
    result = node_web_search_mcp(init_state)

"""
(knowledge-base) D:\knowledge-base>python -m app.test.processor.query_processor.nodes.node_web_search_mcp
2026-07-23 19:40:27 - root - INFO - logging initialized: ./logs\knowledge_base.log
2026-07-23 19:40:27 - import.node_web_search_mcp - INFO - --- node_web_search_mcp started ---
2026-07-23 19:40:27 - asyncio - DEBUG - Using proactor: IocpProactor
2026-07-23 19:40:27 - mcp.client.streamable_http - DEBUG - Connecting to StreamableHTTP endpoint: https://dashscope.aliyuncs.com/api/v1/mcps/WebSearch/mcp
2026-07-23 19:40:27 - mcp.client.streamable_http - DEBUG - Sending client message: root=JSONRPCRequest(method='initialize', params={'protocolVersion': '2025-11-25', 'capabilities': {}, 'clientInfo': {'name': 'mcp', 'version': '0.1.0'}}, jsonrpc='2.0', id=0)
2026-07-23 19:40:27 - httpcore.connection - DEBUG - connect_tcp.started host='dashscope.aliyuncs.com' port=443 local_address=None timeout=10 socket_options=None
2026-07-23 19:40:28 - httpcore.connection - DEBUG - connect_tcp.complete return_value=<httpcore._backends.anyio.AnyIOStream object at 0x000001DC7260BB50>
2026-07-23 19:40:28 - httpcore.connection - DEBUG - start_tls.started ssl_context=<ssl.SSLContext object at 0x000001DC7258DD00> server_hostname='dashscope.aliyuncs.com' timeout=10
2026-07-23 19:40:28 - httpcore.connection - DEBUG - start_tls.complete return_value=<httpcore._backends.anyio.AnyIOStream object at 0x000001DC7260BA90>
2026-07-23 19:40:28 - httpcore.http11 - DEBUG - send_request_headers.started request=<Request [b'POST']>
2026-07-23 19:40:28 - httpcore.http11 - DEBUG - send_request_headers.complete
2026-07-23 19:40:28 - httpcore.http11 - DEBUG - send_request_body.started request=<Request [b'POST']>
2026-07-23 19:40:28 - httpcore.http11 - DEBUG - send_request_body.complete
2026-07-23 19:40:28 - httpcore.http11 - DEBUG - receive_response_headers.started request=<Request [b'POST']>
2026-07-23 19:40:28 - httpcore.http11 - DEBUG - receive_response_headers.complete return_value=(b'HTTP/1.1', 200, b'OK', [(b'x-request-id', b'd0bd97fe-f23d-939e-a360-e64cad888fe3'), (b'content-type', b'application/json;charset=utf-8'), (b'date', b'Thu, 23 Jul 2026 11:40:26 GMT'), (b'req-cost-time', b'25'), (b'req-arrive-time', b'1784806827134'), (b'resp-start-time', b'1784806827160'), (b'x-envoy-upstream-service-time', b'16'), (b'content-encoding', b'gzip'), (b'vary', b'Accept-Encoding'), (b'server', b'istio-envoy'), (b'transfer-encoding', b'chunked')])
2026-07-23 19:40:28 - httpx - INFO - HTTP Request: POST https://dashscope.aliyuncs.com/api/v1/mcps/WebSearch/mcp "HTTP/1.1 200 OK"
2026-07-23 19:40:28 - httpcore.http11 - DEBUG - receive_response_body.started request=<Request [b'POST']>
2026-07-23 19:40:28 - httpcore.http11 - DEBUG - receive_response_body.complete
2026-07-23 19:40:28 - httpcore.http11 - DEBUG - response_closed.started
2026-07-23 19:40:28 - httpcore.http11 - DEBUG - response_closed.complete
2026-07-23 19:40:28 - mcp.client.streamable_http - INFO - Negotiated protocol version: 2024-11-05
2026-07-23 19:40:28 - mcp.client.streamable_http - DEBUG - Sending client message: root=JSONRPCNotification(method='notifications/initialized', params=None, jsonrpc='2.0')
2026-07-23 19:40:28 - httpcore.http11 - DEBUG - send_request_headers.started request=<Request [b'POST']>
2026-07-23 19:40:28 - httpcore.http11 - DEBUG - send_request_headers.complete
2026-07-23 19:40:28 - httpcore.http11 - DEBUG - send_request_body.started request=<Request [b'POST']>
2026-07-23 19:40:28 - httpcore.http11 - DEBUG - send_request_body.complete
2026-07-23 19:40:28 - httpcore.http11 - DEBUG - receive_response_headers.started request=<Request [b'POST']>
2026-07-23 19:40:28 - httpcore.http11 - DEBUG - receive_response_headers.complete return_value=(b'HTTP/1.1', 202, b'Accepted', [(b'x-request-id', b'4ea1d234-7173-90c0-854d-da9e1dd22f19'), (b'content-type', b'application/json;charset=utf-8'), (b'content-length', b'0'), (b'date', b'Thu, 23 Jul 2026 11:40:27 GMT'), (b'req-cost-time', b'24'), (b'req-arrive-time', b'1784806827223'), (b'resp-start-time', b'1784806827247'), (b'x-envoy-upstream-service-time', b'13'), (b'server', b'istio-envoy')])
2026-07-23 19:40:28 - httpx - INFO - HTTP Request: POST https://dashscope.aliyuncs.com/api/v1/mcps/WebSearch/mcp "HTTP/1.1 202 Accepted"
2026-07-23 19:40:28 - mcp.client.streamable_http - DEBUG - Received 202 Accepted
2026-07-23 19:40:28 - httpcore.http11 - DEBUG - response_closed.started
2026-07-23 19:40:28 - httpcore.http11 - DEBUG - response_closed.complete
2026-07-23 19:40:28 - mcp.client.streamable_http - DEBUG - Sending client message: root=JSONRPCRequest(method='tools/call', params={'name': 'bailian_web_search', 'arguments': {'query': '关于brother HAK180烫金机，如何调节转印温度？', 'count': 5}}, jsonrpc='2.0', id=1)
2026-07-23 19:40:28 - httpcore.connection - DEBUG - connect_tcp.started host='dashscope.aliyuncs.com' port=443 local_address=None timeout=10 socket_options=None
2026-07-23 19:40:28 - httpcore.connection - DEBUG - connect_tcp.complete return_value=<httpcore._backends.anyio.AnyIOStream object at 0x000001DC72613090>
2026-07-23 19:40:28 - httpcore.connection - DEBUG - start_tls.started ssl_context=<ssl.SSLContext object at 0x000001DC7258DD00> server_hostname='dashscope.aliyuncs.com' timeout=10
2026-07-23 19:40:28 - httpcore.connection - DEBUG - start_tls.complete return_value=<httpcore._backends.anyio.AnyIOStream object at 0x000001DC72613750>
2026-07-23 19:40:28 - httpcore.http11 - DEBUG - send_request_headers.started request=<Request [b'POST']>
2026-07-23 19:40:28 - httpcore.http11 - DEBUG - send_request_headers.complete
2026-07-23 19:40:28 - httpcore.http11 - DEBUG - send_request_body.started request=<Request [b'POST']>
2026-07-23 19:40:28 - httpcore.http11 - DEBUG - send_request_body.complete
2026-07-23 19:40:28 - httpcore.http11 - DEBUG - receive_response_headers.started request=<Request [b'POST']>
2026-07-23 19:40:28 - httpcore.http11 - DEBUG - receive_response_headers.complete return_value=(b'HTTP/1.1', 200, b'OK', [(b'x-request-id', b'be4cd673-ed32-916f-b2a0-5dd8baa35870'), (b'content-type', b'application/json;charset=utf-8'), (b'date', b'Thu, 23 Jul 2026 11:40:27 GMT'), (b'req-cost-time', b'468'), (b'req-arrive-time', b'1784806827409'), (b'resp-start-time', b'1784806827877'), (b'x-envoy-upstream-service-time', b'459'), (b'content-encoding', b'gzip'), (b'vary', b'Accept-Encoding'), (b'server', b'istio-envoy'), (b'transfer-encoding', b'chunked')])
2026-07-23 19:40:28 - httpx - INFO - HTTP Request: POST https://dashscope.aliyuncs.com/api/v1/mcps/WebSearch/mcp "HTTP/1.1 200 OK"
2026-07-23 19:40:28 - httpcore.http11 - DEBUG - receive_response_body.started request=<Request [b'POST']>
2026-07-23 19:40:28 - httpcore.http11 - DEBUG - receive_response_body.complete
2026-07-23 19:40:28 - httpcore.http11 - DEBUG - response_closed.started
2026-07-23 19:40:28 - httpcore.http11 - DEBUG - response_closed.complete
2026-07-23 19:40:28 - mcp.client.streamable_http - DEBUG - Sending client message: root=JSONRPCRequest(method='tools/list', params=None, jsonrpc='2.0', id=2)
2026-07-23 19:40:29 - httpcore.http11 - DEBUG - send_request_headers.started request=<Request [b'POST']>
2026-07-23 19:40:29 - httpcore.http11 - DEBUG - send_request_headers.complete
2026-07-23 19:40:29 - httpcore.http11 - DEBUG - send_request_body.started request=<Request [b'POST']>
2026-07-23 19:40:29 - httpcore.http11 - DEBUG - send_request_body.complete
2026-07-23 19:40:29 - httpcore.http11 - DEBUG - receive_response_headers.started request=<Request [b'POST']>
2026-07-23 19:40:29 - httpcore.http11 - DEBUG - receive_response_headers.complete return_value=(b'HTTP/1.1', 200, b'OK', [(b'x-request-id', b'076f3561-0cb5-9966-9735-859533c6ce96'), (b'content-type', b'application/json;charset=utf-8'), (b'date', b'Thu, 23 Jul 2026 11:40:27 GMT'), (b'req-cost-time', b'22'), (b'req-arrive-time', b'1784806828067'), (b'resp-start-time', b'1784806828089'), (b'x-envoy-upstream-service-time', b'12'), (b'content-encoding', b'gzip'), (b'vary', b'Accept-Encoding'), (b'server', b'istio-envoy'), (b'transfer-encoding', b'chunked')])
2026-07-23 19:40:29 - httpx - INFO - HTTP Request: POST https://dashscope.aliyuncs.com/api/v1/mcps/WebSearch/mcp "HTTP/1.1 200 OK"
2026-07-23 19:40:29 - httpcore.http11 - DEBUG - receive_response_body.started request=<Request [b'POST']>
2026-07-23 19:40:29 - httpcore.http11 - DEBUG - receive_response_body.complete
2026-07-23 19:40:29 - httpcore.http11 - DEBUG - response_closed.started
2026-07-23 19:40:29 - httpcore.http11 - DEBUG - response_closed.complete
2026-07-23 19:40:29 - app.services.mcp_search_service - INFO - MCP web search result:
meta=None content=[TextContent(type='text', text='{"pages":[{"snippet":"烫金机 可选7PPM烫金速度  无版烫印  配备最大44页标准ADF进纸器  支持省膜模式  10字符x2行LCD液晶屏  HAK180烫金机,凭借其高速、高品质、以及出色的细节小字烫印效果,成为定制化专属机型。可烫印90g/m²~350g/m²的A4各类型纸张,支持各类广泛的应用领域。 高效、稳定的进纸结构 配备44页标准ADF进纸器,支持90g/m²~350g/m²的各类纸张(普通纸、薄纸、再生纸、厚纸等),进纸通道结构稳定可靠,支持连续烫印。 * 350g/m²支持12页自动进纸 * 最大支持44页进纸容量(90g/m²)烫印面朝下 高速连续烫金 HAK180针对不同厚度、介质的纸张提供两种可选烫金速度。15ppm满足普通规格纸张的高效烫金需求,7ppm适合稍厚纸张的烫金。 10字符×2行LCD液晶屏 10字符×2行LCD液晶屏,2个自定义按键,操作直观,方便快捷。 一般参数  正常工作环境(温度): 10 ~ 32 摄氏度(50 ~ 90 华氏度) 正常工作环境(相对湿度): 20 % ~ 80 % 机器尺寸: W 384.2mm×D 330.2mm×H 356.2mm 重量(含包装箱): 16.9kg 电源: 220~240 V 消费电力(烫印中): 少于340W 消费电力(待机中): 少于7W 消费电力(关机): 少于0.04W LCD液晶屏尺寸: 48.0mm×10.9mm 节省烫金膜功能: 支持(在省膜模式中“跳过”和“中间”功能, 仅适用全幅烫金膜盒) 烫印参数  最大烫印速度 (A4): 最高达15 ppm 可选烫印速度(A4): 7 ppm 烫金机-HAK180-烫印速度调整-7PPM 烫金机-HAK180-安装耗材 烫金机-HAK180-更换耗材","hostname":"兄弟(中国)商业有限公司","hostlogo":"","title":"HAK180","url":"https://www.brother.cn/hak/hak180"},{"snippet":"基于行业快速发展前景,高端文印市场的需求正日益突显。</p><p>为满足高端文印市场对于个性化烫金需求,解决繁杂制版工序及成本高企等的诸多困扰,兄弟(中国)商业有限公司正式发布Brother HAK180烫金机,融汇“便捷使用”和“精品烫印”于一身。</p><p><img data-alt=\\"Brother HAK180烫金机\\" src=\\"//img.huanqiucdn.cn/dp/api/files/imageDir/ee1cccb800ebdfd07c4e24f01a129fc3.png?imageView2/2/w/750\\" /></p><p>据悉,Brother HAK180烫金机集合了Brother始终坚持的高质量与高性价比的产品力,赋能其“无版烫印”、“多页连续烫金”、“纤毫毕现品质呈现”多重创新技术,提升用户烫金体验,为高端文印与商务交流提供更优质、更创新的解决方案。</p><p>兄弟(中国)全新推出的Brother HAK180烫金机,采用“无版烫金”技术,不仅降低私人定制成本,大幅提升工作效率,还能满足私人定制专属烫金需求。</p><p>面对个性化烫金需求时,Brother烫金机HAK180告别手送的烦杂流程,实现多页自动连续烫金。无版烫金的技术搭配连续烫金的能力,向来宾展示Brother HAK180烫金机宛如“魔术表演”般的多样魅力。</p><p>HAK180烫金机还广泛支持各类纸张,胜任各式复杂情况,高效便捷地完成繁重任务。比如精美邀请函,高档菜单与座位卡,激励学子的金色奖状等各类需要高品质,个性化定制的场景,满足学校,商务公司,高档宴会酒店等多用户需求。imageView2/2/w/750\\" /></p><p>在无版烫金与读秒烫金的基础之上,Brother HAK180烫金机采用“金”“银”“红”三色烫金薄膜设计,让烫金效果达到纤毫毕现的水准。无论是纤细线条,亦或是微小字体,都能精准呈现。清晰的烫印效果,杜绝棱角、毛边、断线、模糊等恼人问题。同时烫印的内容耐得住长期保存,即便用手指刮抠也不会掉色或脱落。","hostname":"环球网","hostlogo":"https://rs2.huanqiucdn.cn/huanqiu/image/m/share.jpg","title":"Brother HAK180烫金机正式发布,满足高端文印需求","url":"https://m.huanqiu.com/article/466lQrab1kv"},{"snippet":"去年底,Brother在进博会发布HAK180烫金机,作为Brother旗下新品类,烫金机是其在打印机、一体机、标签机、条码机、扫描仪等之后,布局的又一办公文印设备品。作为一款主要针对高端文印店推出的产品,HAK180的问世,令烫金品在文印店中即可完成,无需再像以前跑到制作工厂去定制,简化流程提升效率;对于烫金需求方而言,也就是企业、学校、花店等,无需频繁的确认,减少了制作流程,向文印店提出需求后,在文印店中就可完成,简单的烫金需求甚至可以做到“立等可取”,一改了传统需要在“需求方,供应商,制作工厂”间频繁沟通、确认、修改的流程,HAK180让烫金流程更省时、更省力、更省沟通。 细分市场需求,灵巧机身,任性安置 近年来,随着文印市场逐渐呈现精细化发展趋势,高端文印的需求逐渐增加,大势之下兄弟HAK180烫金机应运而生。烫金机,顾名思义,可以简单理解为,在纸张表面烫印一层金色,当然,此“金”非彼“金”,就像上面提到的奖状、春联,只是在技术上有些特殊。 第一眼看到兄弟HAK180烫金机,如非提前知晓这是一台烫金机,可能会让人误以为是一台馈纸式扫描仪,毕竟从外观来看,兄弟HAK180烫金机与扫描仪有着相似的外观,尤其是进纸、出纸托盘的设计,都有着一定相似度。 机身顶部的进纸托盘可以存放大量用于烫印的纸张,HAK180支持多种纸张质量规格,像办公常用70g/m²的A4纸张,以及更厚更重350g/m²的A4纸张都是可以正常实现烫印的,其中90g/m²纸张可以同时存放44张,350g/m²纸张可以同时存放12张,并可实现纸张自动、连续进纸烫金(如文章起始视频所示),这得益于其采用的“多页连续烫金”技术,可以处理批量烫印任务。 兄弟HAK180烫金机还支持“无版烫金”,整个烫印过程无需提前制版。如上图所示,比如我们需要制作一张用于表彰员工,或是学生的荣誉证书/奖状,只需提前制作一张《荣誉证书》的样式(设计图),利用激光打印机,将样式内容打印出来,再将带有内容的一侧,面向HAK180放入到进纸托盘中,点击启动键后,HAK180可自动识别激光打印机打印的内容,并在激光打印机打印的内容上,进行烫印工作,只需静待数秒,烫印成品就可从出纸托盘输出。","hostname":"百家号","hostlogo":"https://baijiahao.baidu.com/favicon.ico","title":"无版烫金+连续烫印?论一台优秀烫金机的自我修养!兄弟HAK180烫金机评测","url":"https://baijiahao.baidu.com/s?id=1737712132039151978&wfr=spider&for=pc"},{"snippet":"因此,文印店也开始“卷起来”了。但是传统的烫金机都需要制版,不仅麻烦,还费时,顾客也等不了这么长时间。所以,怎样才能既方便又快捷地就能拥有烫印的效果呢? Brother兄弟(以下简称“兄弟”)推出的HAK180烫金机凭借其高速、高品质、以及出色的细节小字烫印效果,成为定制化专属机型,专业实力为邀请函、贺卡、请柬等个性化定制需求提供了更多的便利,最终帮助用户实现产业升级、促进文印服务往高端化发展。同时,无版烫印、支持省膜模式,大幅降低运营成本,使用效率更高,免去使用者的顾虑,为业务保驾护航。产品颜色为黑色,磨砂的质感使得产品在使用时不易留下指纹,更具耐磨性。一体机整体观感棱角分明,但机身边角处均采用了圆润的设计,很大程度避免了用户在使用时发生不必要的磕碰。烫金机正面采用斜面设计,使得操作更加便捷舒适,摁键设置不用半蹲操作。并且外观还获得了2021年的日本GOOD\u2002DESIGN奖。 \u2002 \u2002 \u2002 在体积方面,兄弟HAK180体积大小为384.2mm*330.2mm*356.2mm,作为一台无版烫金机,这样的机身体积可以摆放在室内桌子上的任何位置。","hostname":"网易","hostlogo":"https://ss1.baidu.com/6ONXsjip0QIZ8tyhnq/it/u=1534926245,1016405979&fm=195&app=88&f=JPEG?w=200&h=200","title":"高速高品质 定制化专属,兄弟HAK180烫金机让你的文印店抢占先机","url":"https://www.163.com/dy/article/HC5ISR9H05119GO7.html"},{"snippet":"服务协议 亲爱的用户: 感谢您使用Brother产品及服务! 为了持续向您提供更加丰富的产品功能,更智能、高效的使用体验,不断提升用户满意度,基于产品功能运行与服务的迭代需求,我们需要对您在使用Brother产品及服务的过程中,产生的必要数据(如设备信息、配置参数等)进行收集、处理。这些数据将有助于我们精准优化打印效率、提升响应速度及满足个性化需求,让每一次操作都更贴合您的期望。 我们深知,您的信任是我们最宝贵的财富!我们非常重视保护您的个人信息、隐私及数据,始终将您的个人信息、隐私与数据安全置于首位,为此我们将在严格遵守中华人民共和国《网络安全法》、《数据安全法》、《个人信息保护法》等法律、行政法规的要求,并在落实国家有关标准与行业实践的基础上,以合法、正当、必要、诚信为原则,依法保护、处理您的个人信息、隐私及数据。 为了更好地保障您的知情权、选择权等合法权益,帮助您清晰、完整地了解我们如何收集、保护、处理您的个人信息,特别是涉及未成年人信息等重要场景,在您使用本产品及服务前,请务必全面、详细阅读以下“产品使用与隐私保护”、“数据保护与处理”、“未成年人信息保护”中的所有内容! 这既是对您自身权益的积极保护,也是对我们工作的有力支持。 感谢您的理解与配合! Brother将始终秉承“At your side.”的理念,在合规、安全、透明的基础上,与您携手,共创更美好的数字化办公体验! 一、产品使用与隐私保护; 本章节内容,将主要向您阐明:您在使用本产品及服务前,需要注意的相关事项,以及使用过程中,我们将如何收集、保护、处理您的个人信息、隐私等必要数据,包括: 收集的数据和用途(包括产品型号、序列号、使用日志、文件格式等); 相关数据原则上存储在中华人民共和国境内; 如何使用Cookie及相关技术等保护、处理您的个人信息; 如需进一步了解“产品使用与隐私保护”的其他内容,请点击了解更多 ✔ 我已了解并同意上述<产品使用与隐私保护>说明 二、数据保护与处理 本章节内容,将主要向您阐明:为了向您提供更为丰富、智能、高效的产品功能和用户体验,我们将可能委托Brother关联公司、第三方服务供应商提供相关数据处理、保护等服务,包括: 数据处理关联方、第三方信息(包括企业名称、联系方式等); 数据处理的必要性(包括处理数据的名称、目的、方式等); 我们确保数据处理方采取安全措施切实保护数据; 如需进一步了解“数据保护与处理”的其他内容,请点击了解更多 ✔ 我已了解并同意上述<数据保护与处理>说明","hostname":"兄弟（中国）商业有限公司呼叫中心网站","hostlogo":"","title":"服务协议 ","url":"https://www.95105369.com/"}],"request_id":"be4cd673-ed32-916f-b2a0-5dd8baa35870","tools":[],"status":0}', annotations=None, meta=None)] structuredContent=None isError=False
2026-07-23 19:40:29 - httpcore.connection - DEBUG - close.started
2026-07-23 19:40:29 - httpcore.connection - DEBUG - close.complete
2026-07-23 19:40:29 - import.node_web_search_mcp - INFO - MCP search result:
[
    {
        "title": "HAK180",
        "url": "https://www.brother.cn/hak/hak180",
        "snippet": "烫金机 可选7PPM烫金速度  无版烫印  配备最大44页标准ADF进纸器  支持省膜模式  10字符x2行LCD液晶屏  HAK180烫金机,凭借其高速、高品质、以及出色的细节小字烫印效果,成为定制化专属机型。可烫印90g/m²~350g/m²的A4各类型纸张,支持各类广泛的应用领域。 高效、稳定的进纸结构 配备44页标准ADF进纸器,支持90g/m²~350g/m²的各类纸张(普通纸、薄纸、再生纸、厚纸等),进纸通道结构稳定可靠,支持连续烫印。 * 350g/m²支持12页自动进纸 * 最大支持44页进纸容量(90g/m²)烫印面朝下 高速连续烫金 HAK180针对不同厚度、介质的纸张提供两种可选烫金速度。15ppm满足普通规格纸张的高效烫金需求,7ppm适合稍厚纸张的烫金。 10字符×2行LCD液晶屏 10字符×2行LCD液晶屏,2个自定义按键,操作直观,方便快捷。 一般参数  正常工作环境(温度): 10 ~ 32 摄氏度(50 ~ 90 华氏度) 正常工作环境(相对湿度): 20 % ~ 80 % 机器尺寸: W 384.2mm×D 330.2mm×H 356.2mm 重量(含包装箱): 16.9kg 电源: 220~240 V 消费电力(烫印中): 少于340W 消费电力(待机中): 少于7W 消费电力(关机): 少于0.04W LCD液晶屏尺寸: 48.0mm×10.9mm 节省烫金膜功能: 支持(在省膜模式中“跳过”和“中间”功能, 仅适用全幅烫金膜盒) 烫印参数  最大烫印速度 (A4): 最高达15 ppm 可选烫印速度(A4): 7 ppm 烫金机-HAK180-烫印速度调整-7PPM 烫金机-HAK180-安装耗材 烫金机-HAK180-更换耗材"
    },
    {
        "title": "Brother HAK180烫金机正式发布,满足高端文印需求",
        "url": "https://m.huanqiu.com/article/466lQrab1kv",
        "snippet": "基于行业快速发展前景,高端文印市场的需求正日益突显。</p><p>为满足高端文印市场对于个性化烫金需求,解决繁杂制版工序及成本高企等的诸多困扰,兄弟(中国)商业有限公司正式发布Brother HAK180烫金机,融汇“便捷使用”和“精品烫印”于一身。</p><p><img data-alt=\"Brother HAK180烫金机\" src=\"//img.huanqiucdn.cn/dp/api/files/imageDir/ee1cccb800ebdfd07c4e24f01a129fc3.png?imageView2/2/w/750\" /></p><p>据悉,Brother HAK180烫金机集合了Brother始终坚持的高质量与高性价比的产品力,赋能其“无版烫印”、“多页连续烫金”、“纤毫毕现品质呈现”多重创新技术,提升用户烫金体验,为高端文印与商务交流提供更优质、更创新的解决方案。</p><p>兄弟(中国)全新推出的Brother HAK180烫金机,采用“无版烫金”技术,不仅降低私人定制成本,大幅提升工作效率,还能满足私人定制专属烫金需求。</p><p>面对个性化烫金需求时,Brother烫金机HAK180告别手送的烦杂流程,实现多页自动连续烫金。无版烫金的技术搭配连续烫金的能力,向来宾展示Brother HAK180烫金机宛如“魔术表演”般的多样魅力。</p><p>HAK180烫金机还广泛支持各类纸张,胜任各式复杂情况,高效便捷地完成繁重任务。比如精美邀请函,高档菜单与座位卡,激励学子的金色奖状等各类需要高品质,个性化定制的场景,满足学校,商务公司,高档宴会酒店等多用户需求。imageView2/2/w/750\" /></p><p>在无版烫金与读秒烫金的基础之上,Brother HAK180烫金机采用“金”“银”“红”三色烫金薄膜设计,让烫金效果达到纤毫毕现的水准。无论是纤细线条,亦或是微小字体,都能精准呈现。清晰的烫印效果,杜绝棱角、毛边、断线、模糊等恼人问题。同时烫印的内容耐得住长期保存,即便用手指刮抠也不会掉色或脱落。"
    },
    {
        "title": "无版烫金+连续烫印?论一台优秀烫金机的自我修养!兄弟HAK180烫金机评测",
        "url": "https://baijiahao.baidu.com/s?id=1737712132039151978&wfr=spider&for=pc",
        "snippet": "去年底,Brother在进博会发布HAK180烫金机,作为Brother旗下新品类,烫金机是其在打印机、一体机、标签机、条码机、扫描仪等之后,布局的又一办公文印设备品。作为一款主要针对高端文印店推出的产品,HAK180的问世,令烫金品在文印店中即可完成,无需再像以前跑到制作工厂去定制,简化流程提升效率;对于烫金需求方而言,也就是企业、学校、花店等,无需频繁的确认,减少了制作流程,向文印店提出需求后,在文印店中就可完成,简单的烫金需求甚至可以做到“立等可取”,一改了传统需要在“需求方,供应商,制作工厂”间频繁沟通、确认、修改的流程,HAK180让烫金流程更省时、更省力、更省沟通。 细分市场需求,灵巧机身,任性安置 近年来,随着文印市场逐渐呈现精细化发展趋势,高端文印的需求逐渐增加,大势之下兄弟HAK180烫金机应运而生。烫金机,顾名思义,可以简单理解为,在纸张表面烫印一层金色,当然,此“金”非彼“金”,就像上面提到的奖状、春联,只是在技术上有些特殊。 第一眼看到兄弟HAK180烫金机,如非提前知晓这是一台烫金机,可能会让人误以为是一台馈纸式扫描仪,毕竟从外观来看,兄弟HAK180烫金机与扫描仪有着相似的外观,尤其是进纸、出纸托盘的设计,都有着一定相似度。 机身顶部的进纸托盘可以存放大量用于烫印的纸张,HAK180支持多种纸张质量规格,像办公常用70g/m²的A4纸张,以及更厚更重350g/m²的A4纸张都是可以正常实现烫印的,其中90g/m²纸张可以同时存放44张,350g/m²纸张可以同时存放12张,并可实现纸张自动、连续进纸烫金(如文章起始视频所示),这得益于其采用的“多页连续烫金”技术,可以处理批量烫印任务。 兄弟HAK180烫金机还支持“无版烫金”,整个烫印过程无需提前制版。如上图所示,比如我们需要制作一张用于表彰员工,或是学生的荣誉证书/奖状,只需提前制作一张《荣誉证书》的样式(设计图),利用激光打印机,将样式内容打印出来,再将带有内容的一侧,面向HAK180放入到进纸托盘中,点击启动键后,HAK180可自动识别激光打印机打印的内容,并在激光打印机打印的内容上,进行烫印工作,只需静待数秒,烫印成品就可从出纸托盘输出。"
    },
    {
        "title": "高速高品质 定制化专属,兄弟HAK180烫金机让你的文印店抢占先机",
        "url": "https://www.163.com/dy/article/HC5ISR9H05119GO7.html",
        "snippet": "因此,文印店也开始“卷起来”了。但是传统的烫金机都需要制版,不仅麻烦,还费时,顾客也等不了这么长时间。所以,怎样才能既方便又快捷地就能拥有烫印的效果呢? Brother兄弟(以下简称“兄弟”)推出的HAK180烫金机凭借其高速、高品质、以及出色的细节小字烫印效果,成为定制化专属机型,专业实力为邀请函、贺卡、请柬等个性化定制需求提供了更多的便利,最终帮助用户实现产业升级、促进文印服务往高端化发展。同时,无版烫印、支持省膜模式,大幅降低运营成本,使用效率更高,免去使用者的顾虑,为业务保驾护航。产品颜色为黑色,磨砂的质感使得产品在使用时不易留下指纹,更具耐磨性。一体机整体观感棱角分明,但机身边角处均采用了圆润的设计,很大程度避免了用户在使用时发生不必要的磕碰。烫金机正面采用斜面设计,使得操作更加便捷舒适,摁键设置不用半蹲操作。并且外观还获得了2021年的日本GOOD DESIGN奖。       在体积方面,兄弟HAK180体积大小为384.2mm*330.2mm*356.2mm,作为一台无版烫金机,这样的机身体积可以摆放在室内桌子上的任何位置。"
    },
    {
        "title": "服务协议",
        "url": "https://www.95105369.com/",
        "snippet": "服务协议 亲爱的用户: 感谢您使用Brother产品及服务! 为了持续向您提供更加丰富的产品功能,更智能、高效的使用体验,不断提升用户满意度,基于产品功能运行与服务的迭代需求,我们需要对您在使用Brother产品及服务的过程中,产生的必要数据(如设备信息、配置参数等)进行收集、处理。这些数据将有助于我们精准优化打印效率、提升响应速度及满足个性化需求,让每一次操作都更贴合您的期望。 我们深知,您的信任是我们最宝贵的财富!我们非常重视保护您的个人信息、隐私及数据,始终将您的个人信息、隐私与数据安全置于首位,为此我们将在严格遵守中华人民共和国《网络安全法》、《数据安全法》、《个人信息保护法》等法律、行政法规的要求,并在落实国家有关标准与行业实践的基础上,以合法、正当、必要、诚信为原则,依法保护、处理您的个人信息、隐私及数据。 为了更好地保障您的知情权、选择权等合法权益,帮助您清晰、完整地了解我们如何收集、保护、处理您的个人信息,特别是涉及未成年人信息等重要场景,在您使用本产品及服务前,请务必全面、详细阅读以下“产品使用与隐私保护”、“数据保护与处理”、“未成年人信息保护”中的所有内容! 这既是对您自身权益的积极保护,也是对我们工作的有力支持。 感谢您的理解与配合! Brother将始终秉承“At your side.”的理念,在合规、安全、透明的基础上,与您携手,共创更美好的数字化办公体验! 一、产品使用与隐私保护; 本章节内容,将主要向您阐明:您在使用本产品及服务前,需要注意的相关事项,以及使用过程中,我们将如何收集、保护、处理您的个人信息、隐私等必要数据,包括: 收集的数据和用途(包括产品型号、序列号、使用日志、文件格式等); 相关数据原则上存储在中华人民共和国境内; 如何使用Cookie及相关技术等保护、处理您的个人信息; 如需进一步了解“产品使用与隐私保护”的其他内容,请点击了解更多 ✔ 我已了解并同意上述<产品使用与隐私保护>说明 二、数据保护与处理 本章节内容,将主要向您阐明:为了向您提供更为丰富、智能、高效的产品功能和用户体验,我们将可能委托Brother关联公司、第三方服务供应商提供相关数据处理、保护等服务,包括: 数据处理关联方、第三方信息(包括企业名称、联系方式等); 数据处理的必要性(包括处理数据的名称、目的、方式等); 我们确保数据处理方采取安全措施切实保护数据; 如需进一步了解“数据保护与处理”的其他内容,请点击了解更多 ✔ 我已了解并同意上述<数据保护与处理>说明"
    }
]
2026-07-23 19:40:29 - import.node_web_search_mcp - INFO - --- node_web_search_mcp done ---
"""