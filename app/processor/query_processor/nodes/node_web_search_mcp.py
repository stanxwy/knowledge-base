import asyncio
import json

from agents.mcp import MCPServerStreamableHttp

from app.config.bailian_mcp_config import mcp_config
from app.processor.query_processor.base import NodeBase
from app.processor.query_processor.state import QueryGraphState
from app.utils.json_format_utils import format_json

class NodeWebSearchMcp(NodeBase):
    """
    节点功能，调用外部搜索引擎补充信息
    """
    name: str = "node_web_search_mcp"

    async def _mcp_call(self, query):
        search_mcp = MCPServerStreamableHttp(
            name="search_mcp",
            params={
                "url": mcp_config.mcp_base_url,
                "headers": {"Authorization": f"Bearer {mcp_config.api_key}"},
                "timeout": 10,
            },
            cache_tools_list=True,
            max_retry_attempts=3,
        )

        try:
            await search_mcp.connect()
            result = await search_mcp.call_tool(
                tool_name="bailian_web_search",
                arguments={"query": query, "count": 5},
            )
            self.logger.info(f"MCP 搜索响应: \n{result}")
            return result
        finally:
            await search_mcp.cleanup()
    
    def process(self, state: QueryGraphState) -> QueryGraphState:
        query = state.get("rewritten_query", "")
        docs = []
        # 如果没有查询内容，直接返回
        if query:
            result = asyncio.run(self._mcp_call(query))
            if result:
                pages = json.loads(result.content[0].text).get("pages") or []
                # 统一输出结构化结果，供后续 rerank/引用使用
                # 每条：{title, url, snippet}

                for item in pages:
                    snippet = (item.get("snippet") or "").strip()
                    url = (item.get("url") or "").strip()
                    title = (item.get("title") or "").strip()
                    if not snippet:
                        continue
                    docs.append({"title": title, "url": url, "snippet": snippet})
                self.logger.info(f"MCP 搜索结果: \n{format_json(docs)}")

        if docs:
            return { "web_search_docs": docs }
        return {}

if __name__ == "__main__":
    from app.utils.logger import setup_logging
    logger = setup_logging()
    init_state = {
        "rewritten_query": "关于brother HAK180烫金机，如何调节转印温度？"
    }
    node_web_search_mcp = NodeWebSearchMcp()
    result = node_web_search_mcp(init_state)

"""
(knowledge-base) PS D:\knowledge-base> python -m app.processor.query_processor.nodes.node_web_search_mcp
2026-07-18 19:24:43 - root - INFO - 日志系统初始化完成，日志文件: ./logs\knowledge_base.log
2026-07-18 19:24:43 - import.node_web_search_mcp - INFO - --- node_web_search_mcp 开始啦 ---
2026-07-18 19:24:43 - httpx - INFO - HTTP Request: POST https://dashscope.aliyuncs.com/api/v1/mcps/WebSearch/mcp "HTTP/1.1 200 OK"
2026-07-18 19:24:43 - mcp.client.streamable_http - INFO - Negotiated protocol version: 2024-11-05
2026-07-18 19:24:44 - httpx - INFO - HTTP Request: POST https://dashscope.aliyuncs.com/api/v1/mcps/WebSearch/mcp "HTTP/1.1 202 Accepted"
2026-07-18 19:24:44 - httpx - INFO - HTTP Request: POST https://dashscope.aliyuncs.com/api/v1/mcps/WebSearch/mcp "HTTP/1.1 200 OK"
2026-07-18 19:24:44 - httpx - INFO - HTTP Request: POST https://dashscope.aliyuncs.com/api/v1/mcps/WebSearch/mcp "HTTP/1.1 200 OK"
2026-07-18 19:24:44 - import.node_web_search_mcp - INFO - MCP 搜索响应:
meta=None content=[TextContent(type='text', text='{"pages":[{"snippet":"重要提示 量Brother保留对本说明书中包含的规格和材料进行更改而不进行通知的权利,并且对于依赖提供的材料 (包括但不限于印刷以及与发布有关的其他错误)所导致的任何损害《包括间接损害)概不负责。 国请注意,对于使用本产品或通过本产品制作的内容造成的任何损坏或利润损失,或者故障、维修或耗材导 致的数据消失或更改,或者第三方提出的任何索赔,我们不承担任何责任。 量对于保养、调整或维修事宜,请联系Brother呼叫中心或您当地的Brother经销商。 量如果本设备工作不正常或出现任何功能异常,请关闭本设备,拔下所有电源线,然后联系Brotner呼叫中 心或您当地的Brother经销商。 曙在使用设备之前,请务必阅读设备随附的所有文档,以获得有关安全和正确操作的信息。 四@2021BrotherIndustries,Ltd.保留所有权利。 1.1提示定兴和1 2Brother设备简介2 2.1设备2 2.1.1”前视图.2 2.1.2”后视图.………3 2.2”操作面板和LED指示条4 3”使用本设备之前6 3.1”打开设备包装并检查组件.46 3.2”去除保护材料………… 3.3”初始设置.pp 3.3.1”连接设备并安装进纸托板和溪金膜使..… 3.3.2”选择液晶显示屏语言〈仅第一次开机时) 3.4”安装烫金膜盒.……p. 中]装入全幅汤金膜盒 3.4.2”装入半幅烫金膜盒 3.4.3”取出溪金膜盒支架 4”介质规格19 4.1可接受的介质19 5使用设备22 5.1。转印22 5.2”将肖金膜转印到双面纸张上ee23 5.3《装入介质23 5.3.1”装入标准尺寸介质.424 5.3.2”装入非标准尺寸介质ee26 6”更改设置27 6.1访问主菜单.427 6.2”菜单项.estsssnnn28 6.3”提高转印质量29 6.3.1调整转印温度29 6.4”节省泥金膜模式..|全 NE32","hostname":"无","hostlogo":"http://t8.baidu.com/it/u=3027949672,2003644166&fm=195&app=88&f=JPEG?w=200&h=200&s=76D1A8764C706C920AEEFAEE0200501D","title":"Brother兄弟烫金机HAK180使用说明书.pdf 60页","url":"https://m.book118.com/html/2025/0801/6045144214011210.shtm"},{"snippet":".","hostname":"京东商城;京东多媒体网","hostlogo":"https://www.jd.com/favicon.ico","title":"兄弟(brother) HAK180烫金机适用邀请函请柬奖状贺卡证书文印高速定制化热转印小型烫印 官方标配【图片 价格 品牌 报价】-京东","url":"https://item.jd.com/10082195754841.html"},{"snippet":"烫金机 可选7PPM烫金速度  无版烫印  配备最大44页标准ADF进纸器  支持省膜模式  10字符x2行LCD液晶屏  HAK180烫金机,凭借其高速、高品质、以及出色的细节小字烫印效果,成为定制化专属机型。可烫印90g/m²~350g/m²的A4各类型纸张,支持各类广泛的应用领域。 高效、稳定的进纸结构 配备44页标准ADF进纸器,支持90g/m²~350g/m²的各类纸张(普通纸、薄纸、再生纸、厚纸等),进纸通道结构稳定可靠,支持连续烫印。 * 350g/m²支持12页自动进纸 * 最大支持44页进纸容量(90g/m²)烫印面朝下 高速连续烫金 HAK180针对不同厚度、介质的纸张提供两种可选烫金速度。15ppm满足普通规格纸张的高效烫金需求,7ppm适合稍厚纸张的烫金。 10字符×2行LCD液晶屏 10字符×2行LCD液晶屏,2个自定义按键,操作直观,方便快捷。 一般参数  正常工作环境(温度): 10 ~ 32 摄氏度(50 ~ 90 华氏度) 正常工作环境(相对湿度): 20 % ~ 80 % 机器尺寸: W 384.2mm×D 330.2mm×H 356.2mm 重量(含包装箱): 16.9kg 电源: 220~240 V 消费电力(烫印中): 少于340W 消费电力(待机中): 少于7W 消费电力(关机): 少于0.04W LCD液晶屏尺寸: 48.0mm×10.9mm 节省烫金膜功能: 支持(在省膜模式中“跳过”和“中间”功能, 仅适用全幅烫金膜盒) 烫印参数  最大烫印速度 (A4): 最高达15 ppm 可选烫印速度(A4): 7 ppm 烫金机-HAK180-烫印速度调整-7PPM 烫金机-HAK180-安装耗材 烫金机-HAK180-更换耗材","hostname":"兄弟(中国)商业有限公司","hostlogo":"","title":"HAK180","url":"https://www.brother.cn/hak/hak180"},{"snippet":"基于行业快速发展前景,高端文印市场的需求正日益突显。</p><p>为满足高端文印市场对于个性化烫金需求,解决繁杂制版工序及成本高企等的诸多困扰,兄弟(中国)商业有限公司正式发布Brother HAK180烫金机,融汇“便捷使用”和“精品烫印”于一身。</p><p><img data-alt=\\"Brother HAK180烫金机\\" src=\\"//img.huanqiucdn.cn/dp/api/files/imageDir/ee1cccb800ebdfd07c4e24f01a129fc3.png?imageView2/2/w/750\\" /></p><p>据悉,Brother HAK180烫金机集合了Brother始终坚持的高质量与高性价比的产品力,赋能其“无版烫印”、“多页连续烫金”、“纤毫毕现品质呈现”多重创新技术,提升用户烫金体验,为高端文印与商务交流提供更优质、更创新的解决方案。</p><p>兄弟(中国)全新推出的Brother HAK180烫金机,采用“无版烫金”技术,不仅降低私人定制成本,大幅提升工作效率,还能满足私人定制专属烫金需求。</p><p>面对个性化烫金需求时,Brother烫金机HAK180告别手送的烦杂流程,实现多页自动连续烫金。无版烫金的技术搭配连续烫金的能力,向来宾展示Brother HAK180烫金机宛如“魔术表演”般的多样魅力。</p><p>HAK180烫金机还广泛支持各类纸张,胜任各式复杂情况,高效便捷地完成繁重任务。比如精美邀请函,高档菜单与座位卡,激励学子的金色奖状等各类需要高品质,个性化定制的场景,满足学校,商务公司,高档宴会酒店等多用户需求。imageView2/2/w/750\\" /></p><p>在无版烫金与读秒烫金的基础之上,Brother HAK180烫金机采用“金”“银”“红”三色烫金薄膜设计,让烫金效果达到纤毫毕现的水准。无论是纤细线条,亦或是微小字体,都能精准呈现。清晰的烫印效果,杜绝棱角、毛边、断线、模糊等恼人问题。同时烫印的内容耐得住长期保存,即便用手指刮抠也不会掉色或脱落。","hostname":"环球网","hostlogo":"https://rs2.huanqiucdn.cn/huanqiu/image/m/share.jpg","title":"Brother HAK180烫金机正式发布,满足高端文印需求","url":"https://m.huanqiu.com/article/466lQrab1kv"},{"snippet":"去年底,Brother在进博会发布HAK180烫金机,作为Brother旗下新品类,烫金机是其在打印机、一体机、标签机、条码机、扫描仪等之后,布局的又一办公文印设备品。作为一款主要针对高端文印店推出的产品,HAK180的问世,令烫金品在文印店中即可完成,无需再像以前跑到制作工厂去定制,简化流程提升效率;对于烫金需求方而言,也就是企业、学校、花店等,无需频繁的确认,减少了制作流程,向文印店提出需求后,在文印店中就可完成,简单的烫金需求甚至可以做到“立等可取”,一改了传统需要在“需求方,供应商,制作工厂”间频繁沟通、确认、修改的流程,HAK180让烫金流程更省时、更省力、更省沟通。 细分市场需求,灵巧机身,任性安置 近年来,随着文印市场逐渐呈现精细化发展趋势,高端文印的需求逐渐增加,大势之下兄弟HAK180烫金机应运而生。烫金机,顾名思义,可以简单理解为,在纸张表面烫印一层金色,当然,此“金”非彼“金”,就像上面提到的奖状、春联,只是在技术上有些特殊。 第一眼看到兄弟HAK180烫金机,如非提前知晓这是一台烫金机,可能会让人误以为是一台馈纸式扫描仪,毕竟从外观来看,兄弟HAK180烫金机与扫描仪有着相似的外观,尤其是进纸、出纸托盘的设计,都有着一定相似度。 机身顶部的进纸托盘可以存放大量用于烫印的纸张,HAK180支持多种纸张质量规格,像办公常用70g/m²的A4纸张,以及更厚更重350g/m²的A4纸张都是可以正常实现烫印的,其中90g/m²纸张可以同时存放44张,350g/m²纸张可以同时存放12张,并可实现纸张自动、连续进纸烫金(如文章起始视频所示),这得益于其采用的“多页连续烫金”技术,可以处理批量烫印任务。 兄弟HAK180烫金机还支持“无版烫金”,整个烫印过程无需提前制版。如上图所示,比如我们需要制作一张用于表彰员工,或是学生的荣誉证书/奖状,只需提前制作一张《荣誉证书》的样式(设计图),利用激光打印机,将样式内容打印出来,再将带有内容的一侧,面向HAK180放入到进纸托盘中,点击启动键后,HAK180可自动识别激光打印机打印的内容,并在激光打印机打印的内容上,进行烫印工作,只需静待数秒,烫印成品就可从出纸托盘输出。","hostname":"百家号","hostlogo":"https://baijiahao.baidu.com/favicon.ico","title":"无版烫金+连续烫印?论一台优秀烫金机的自我修养!兄弟HAK180烫金机评测","url":"https://baijiahao.baidu.com/s?id=1737712132039151978&wfr=spider&for=pc"}],"request_id":"0a199b9b-5a7d-91f6-995a-d735b6e24126","tools":[],"status":0}', annotations=None, meta=None)] structuredContent=None isError=False
2026-07-18 19:24:44 - import.node_web_search_mcp - INFO - MCP 搜索结果: 
[
    {
        "title": "Brother兄弟烫金机HAK180使用说明书.pdf 60页",
        "url": "https://m.book118.com/html/2025/0801/6045144214011210.shtm",
        "snippet": "重要提示 量Brother保留对本说明书中包含的规格和材料进行更改而不进行通知的权利,并且对于依赖提供的材料 (包括但不限于印刷以及与发布有关的其他错误)所导致的任何损害《包括间接损害)概不负责。 国请注意,对于使用本产品或通过本产品制作的内容造成的任何损坏或利润损失,或者故障、维修或耗材导 致的数据消失或更改,或者第三方提出的任何索赔,我们不承担任何责任。 量对于保养、调整或维修事宜,请联系Brother呼叫中心或您当地的Brother经销商。 量如果本设备工作不正常或出现任何功能异常,请关闭本设备,拔下所有电源线,然后联系Brotner呼叫中 心或您当地的Brother经销商。 曙在使用设备之前,请务必阅读设备随附的所有文档,以获得有关安全和正确操作的信息。 四@2021BrotherIndustries,Ltd.保留所有权利。 1.1提示定兴和1 2Brother设备简介2 2.1设备2 2.1.1”前视图.2 2.1.2”后视图.………3 2.2”操作面板和LED指示条4 3”使用本设备之前6 3.1”打开设备包装并检查组件.46 3.2”去除保护材料………… 3.3”初始设置.pp 3.3.1”连接设备并安装进纸托板和溪金膜使..… 3.3.2”选择液晶显示屏语言〈仅第一次开机时) 3.4”安装烫金膜盒.……p. 中]装入全幅汤金膜盒 3.4.2”装入半幅烫金膜盒 3.4.3”取出溪金膜盒支架 4”介质规格19 4.1可接受的介质19 5使用设备22 5.1。转印22 5.2”将肖金膜转印到双面纸张上ee23 5.3《装入介质23 5.3.1”装入标准尺寸介质.424 5.3.2”装入非标准尺寸介质ee26 6”更改设置27 6.1访问主菜单.427 6.2”菜单项.estsssnnn28 6.3”提高转印质量29 6.3.1调整转印温度29 6.4”节省泥金膜模式..|全 NE32"
    },
    {
        "title": "兄弟(brother) HAK180烫金机适用邀请函请柬奖状贺卡证书文印高速定制化热转印小型烫印 官方标配【图片 价格 品牌 报价】-京东",
        "url": "https://item.jd.com/10082195754841.html",
        "snippet": "."
    },
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
    }
]
2026-07-18 19:24:44 - import.node_web_search_mcp - INFO - --- node_web_search_mcp 完成啦 ---
"""