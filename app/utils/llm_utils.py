import base64
from loguru import logger
from typing import Tuple
from langchain_openai import ChatOpenAI
from app.config.lm_config import get_lm_config

_llm_client_cache = {}

def get_llm_client(model: str | None = None, json_mode: bool = False) -> ChatOpenAI:
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
        logger.debug(f"请求VLM生成图片总结 {image_path}")
        response = chat_model.invoke(messages)
        logger.info(f"VLM生成图片 {image_path} 总结结果: {response.content}")
        # logger.verbose(json.dumps(response, ensure_ascii=False, indent=2)) # Object of type AIMessage is not JSON serializable
        return response.content.strip().replace("\n", "")

    except Exception as e:
        logger.error(f"图像总结失败：{image_path}, 错误{e}")
        return "图片描述"

if __name__ == '__main__':
    llm = get_llm_client()
    print(llm.invoke("你是谁"))