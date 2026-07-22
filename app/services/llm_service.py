import base64
import json
import logging
from typing import Any, Dict, List, Tuple

from langchain_core.messages import SystemMessage, HumanMessage
from langchain_openai import ChatOpenAI
from app.config.lm_config import get_lm_config
from app.processor.import_processor.prompt import ITEM_NAME_SYSTEM_PROMPT, ITEM_NAME_USER_PROMPT_TEMPLATE
from app.processor.query_processor.prompt import ITEM_NAME_EXTRACT_SYSTEM_PROMPT, ITEM_NAME_EXTRACT_TEMPLATE, HYDE_PROMPT

_llm_client_cache = {}

logger = logging.getLogger(__name__)

DEFAULT_IMAGE_CAPTION = "alt text"

def get_llm_client(model: str | None = None, json_mode: bool = False) -> ChatOpenAI:
    logger.debug(f"Gettting LangChain ChatOpenAI {model} client instance...")
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
    logger.info(f"LangChain ChatOpenAI {key} client instance created...")
    return llm

def generate_image_caption(image_path: str, doc_stem: str, image_context: Tuple[str, str]) -> str:

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
        logger.debug(f"Requesting VLM to generate image caption {image_path}")
        response = chat_model.invoke(messages)
        logger.info(f"Image caption generated: {response.content}")
        # logger.verbose(json.dumps(response, ensure_ascii=False, indent=2)) # Object of type AIMessage is not JSON serializable
        return response.content.strip().replace("\n", "")

    except Exception as e:
        logger.error(f"Error generating image caption for {image_path}: {e}")
        return DEFAULT_IMAGE_CAPTION
    
def identify_main_product(filename: str, context: str) -> str:
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
        logger.info(f"Item name identified: {product_name}")

        # data cleanup
        product_name = (product_name.replace(" ", "")
                        .replace("\n", "")
                        .replace("\t", "")
                        .replace("\r", ""))

        if not product_name:
            return filename
        return product_name

    except Exception as e:
        logger.error(f"Error identifying item name for {filename}: {e}")
        return filename
    
def resolve_item_name_and_rewrite_query(query: str, history: List[Dict[str, Any]]) -> Tuple[List[str], str]:
    try:
        history_text = ""
        for msg in reversed(history):
            role = msg.get("role")
            content = msg.get("text")
            history_text += f"{role}: {content}\n"

        user_prompt = ITEM_NAME_EXTRACT_TEMPLATE.format(
            history_text=history_text,
            query=query
        )
        logger.info(f"User prompt for LLM: {user_prompt}")

        messages = [
            SystemMessage(content=ITEM_NAME_EXTRACT_SYSTEM_PROMPT),
            HumanMessage(content=user_prompt)
        ]

        chat_model = get_llm_client(model=get_lm_config().item_model, json_mode=True)
        response = chat_model.invoke(messages)
        content = response.content
        logger.info(f"LLM response: {response}")

        if content.startswith("```json"):
            content = content.replace("```json", "").replace("```", "")
        result = json.loads(content)

        item_names = result.get("item_names", [])
        item_names = [
            name.replace(" ", "").replace("\n", "").replace("\t", "").replace("\r", "")
            for name in item_names
        ]
        rewritten_query = result.get("rewritten_query", query)

        return item_names, rewritten_query

    except Exception as e:
        logger.error(f"Error calling LLM: {e}")
        return [], query

def generate_hyde_doc(rewritten_query: str) -> str:
    try:
        llm = get_llm_client()
        hyde_prompt = HYDE_PROMPT.format(rewritten_query=rewritten_query)
        response = llm.invoke(hyde_prompt)
        logger.info(f"Hyde document generated: \n{response}")
        return response.content
    except Exception as e:
        logger.exception(f"Error generating Hyde document: {e}")
        raise e

if __name__ == '__main__':
    llm = get_llm_client()
    print(llm.invoke("introduce yourself"))