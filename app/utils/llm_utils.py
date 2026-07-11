from langchain.chat_models import ChatOpenAI
from app.config.lm_config import lm_config

_llm_client_cache = {}

def get_llm_client(model: str | None = None, json_mode: bool = False):
    m = model or lm_config.llm_model

    key = (m, json_mode)
    if key in _llm_client_cache:
        return _llm_client_cache[key]

    extra_body = {"enable_thinking": False}

    model_kwargs: dict = {}
    if json_mode:
        model_kwargs["response_format"] = {"type": "json_object"}

    llm = ChatOpenAI(
        model=m,
        api_key=lm_config.api_key,
        base_url=lm_config.base_url,
        temperature=lm_config.llm_temperature,
        extra_body=extra_body,
        model_kwargs=model_kwargs
    )

    _llm_client_cache[key] = llm
    return llm

if __name__ == '__main__':
    llm = get_llm_client()
    print(llm.invoke("你是谁"))