import base64
import json
import logging
from typing import Any, Dict, List, Tuple

from langchain_core.messages import SystemMessage, HumanMessage
from langchain_openai import ChatOpenAI
from app.config.lm_config import get_lm_config
from app.processor.import_processor.prompt import ITEM_NAME_SYSTEM_PROMPT, ITEM_NAME_USER_PROMPT_TEMPLATE
from app.processor.query_processor.prompt import ITEM_NAME_EXTRACT_SYSTEM_PROMPT, ITEM_NAME_EXTRACT_TEMPLATE

_llm_client_cache = {}

def get_llm_client(model: str | None = None, json_mode: bool = False) -> ChatOpenAI:
    logging.getLogger().debug(f"开始获取 LangChain ChatOpenAI {model} 客户端实例...")
    lm_config = get_lm_config()
    m = model or lm_config.default_model

    key = (m, json_mode)
    if key in _llm_client_cache:
        return _llm_client_cache[key]

    extra_body = {"enable_thinking": False}

    model_kwargs: dict = {}
    if json_mode:
        model_kwargs["response_format"] = {"type": "json_object"}

    llm: ChatOpenAI = ChatOpenAI(
        model=m,
        api_key=lm_config.api_key,
        base_url=lm_config.base_url,
        temperature=lm_config.llm_temperature,
        extra_body=extra_body,
        model_kwargs=model_kwargs
    )

    _llm_client_cache[key] = llm
    logging.getLogger().info(f"LangChain ChatOpenAI {key} 客户端实例获取成功...")
    return llm

def generate_image_caption(image_path: str, doc_stem: str, image_context: Tuple[str, str]) -> str:
    """
        调用多模态大模型总结图片内容。

        参数：
        - image_path: 图片本地路径。
        - root_folder: 文档所属文件夹名（提供更多上下文）。
        - image_content: 图片在文档中的上下文 (前文, 后文)。
    """
    with open(image_path, "rb") as img_file:
        base64_image = base64.b64encode(img_file.read()).decode("utf-8")

    try:
        chat_model: ChatOpenAI = get_llm_client(get_lm_config().vl_model)
        messages = [{
            "role": "user",
            "content": [{
                "type": "text",
                "text": f"""这是"{doc_stem}"文件中的一张图片，图片上文部分为"{image_context[0]}"，下文部分为"{image_context[1]}"，请用中文简要总结这张图片的内容，用于 Markdown 图片标题。尽量不要超过20个字"""
            }, {
                "type": "image_url",
                "image_url": { "url": f"data:image/jpeg;base64,{base64_image}" }
            }]
        }]
        logging.getLogger().debug(f"请求VLM生成图片总结 {image_path}")
        response = chat_model.invoke(messages)
        logging.getLogger().info(f"VLM生成图片总结结果: {response.content}")
        # logger.verbose(json.dumps(response, ensure_ascii=False, indent=2)) # Object of type AIMessage is not JSON serializable
        return response.content.strip().replace("\n", "")

    except Exception as e:
        logging.getLogger().error(f"图像总结失败：{image_path}, 错误{e}")
        return "图片描述"
    
def identify_main_product(filename: str, context: str) -> str:
    """
    调用大模型实现商品名称/型号精准识别
    核心逻辑：
        1. 上下文为空 → 直接返回filename（兜底，无需调用大模型）
        2. 上下文非空 → 加载标准化prompt模板，构建大模型对话消息
        3. 调用大模型后对返回结果做清洗，过滤无效字符
        4. 大模型返回空/调用异常 → 均返回filename兜底，保证流程不中断
    核心特性：
        - 提示词解耦：通过load_prompt加载本地模板，无需硬编码
        - 格式兼容：兼容不同LLM客户端返回格式，防止属性报错
        - 异常兜底：全异常捕获，大模型服务不可用时不影响主流程
    参数：
        filename: 处理后的文件标题（异常/空值时的兜底值）
        context: 步骤2构建的结构化切片上下文（大模型识别的核心依据）
    返回值：
        str: 清洗后的商品名称（异常/空值时返回原始filename）
    """
    if not context:
        return filename

    try:
        llm = get_llm_client()
        user_prompt = ITEM_NAME_USER_PROMPT_TEMPLATE.format(
            filename=filename, context=context
        )
        messages = [
            SystemMessage(content=ITEM_NAME_SYSTEM_PROMPT),
            HumanMessage(content=user_prompt)
        ]
        response = llm.invoke(messages)
        product_name = response.content
        logging.getLogger().info(f"商品名称识别结果：{product_name}")

        # data cleanup
        product_name = (product_name.replace(" ", "")
                        .replace("\n", "")
                        .replace("\t", "")
                        .replace("\r", ""))

        if not product_name:
            return filename
        return product_name

    except Exception as e:
        logging.getLogger().error(f"大模型调用异常：{e}")
        return filename
    
def resolve_item_name_and_rewrite_query(query: str, history: List[Dict[str, Any]]) -> Tuple[List[str], str]:
    """
    利用LLM从当前问题以及历史会话中提取出主要询问的商品名称item_names（可多个，JSON列表形式）
    若商品名不够明确则返回空列表，同时根据上下文重新改写问题，保证问题独立完整
    :param query: 字符串 - 用户当前原始查询问题（如："这个多少钱？"）
    :param history: 列表[字典] - 近期会话历史，每条消息含role/text等字段，
                    格式：[{"role": "user/assistant", "text": "消息内容", "_id": "消息ID"}, ...]
    :return: 字典 - 提取结果，固定包含2个字段，格式：
                {
                    "item_names": ["商品名1", "商品名2", ...],  # 提取的商品名列表，无则空列表
                    "rewritten_query": "改写后的完整问题"       # 包含商品名的独立问题，无则返回原始query
                }
    """
    try:
        # 1. 构造历史对话文本，拼接为"角色: 内容"的格式，供LLM做上下文理解
        history_text = ""
        for msg in reversed(history):
            role = msg.get("role")
            content = msg.get("text")
            history_text += f"{role}: {content}\n"

        # 2. 处理和动态拼接提示词
        # 为了把大括号当作 “普通字符” 保留下来，用双大括号 {{ 表示普通的左大括号 {，双大括号 }} 表示普通的右大括号 }。
        user_prompt = ITEM_NAME_EXTRACT_TEMPLATE.format(
            history_text=history_text,
            query=query
        )
        logging.getLogger().info(f"商品名称识别用户提示词：{user_prompt}")

        # 3. 构造LLM调用的消息列表，包含系统角色（定义助手身份）和用户角色（传入提示词）
        messages = [
            SystemMessage(content=ITEM_NAME_EXTRACT_SYSTEM_PROMPT),
            HumanMessage(content=user_prompt)
        ]

        # 4. 调用LLM客户端，发起请求获取结果
        chat_model = get_llm_client(model=get_lm_config().item_model, json_mode=True)
        response = chat_model.invoke(messages)
        content = response.content
        logging.getLogger().info(f"LLM商品名称识别响应：{response}")

        # 5. 数据清洗：处理LLM可能返回的代码块格式（如```json ... ```），去除包裹符
        if content.startswith("```json"):
            content = content.replace("```json", "").replace("```", "")

        # 6. 数据解析：将JSON字符串转为字典
        result = json.loads(content)

        # 7. 健壮性处理：确保字段存在
        # 确保返回结果包含item_names字段，无则设为空列表
        item_names = result.get("item_names", [])
        rewritten_query = result.get("rewritten_query", query)

        # 8. 给item_names 去除空格
        item_names = [
            name.replace(" ", "").replace("\n", "").replace("\t", "").replace("\r", "")
            for name in item_names
        ]
        # 9、返回解析后的提取结果
        return item_names, rewritten_query

    except Exception as e:
        # 捕获所有异常（如LLM调用失败、JSON解析失败等），记录错误日志
        logging.getLogger().error(f"大模型调用异常：{e}")
        # 异常时返回默认结果：空商品名列表+原始查询
        return [], query

if __name__ == '__main__':
    llm = get_llm_client()
    print(llm.invoke("你是谁"))