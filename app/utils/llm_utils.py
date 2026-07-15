import base64
import logging
from typing import Tuple

from langchain_core.messages import SystemMessage, HumanMessage
from langchain_openai import ChatOpenAI
from app.config.lm_config import get_lm_config
from app.processor.query_processor.nodes.prompt.item_name_recognition import ITEM_NAME_SYSTEM_PROMPT, ITEM_NAME_USER_PROMPT_TEMPLATE

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
    logging.getLogger().debug("LangChain ChatOpenAI 客户端实例获取成功...")
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
        logging.getLogger().info(f"VLM生成图片 {image_path} 总结结果: {response.content}")
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

if __name__ == '__main__':
    llm = get_llm_client()
    print(llm.invoke("你是谁"))