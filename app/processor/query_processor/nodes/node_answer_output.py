import re
from typing import Dict, List, Tuple

from langchain_core.prompts import load_prompt

from app.processor.query_processor.base import NodeBase
from app.processor.query_processor.exceptions import StateFieldError
from app.processor.query_processor.prompt import ANSWER_PROMPT
from app.processor.query_processor.state import QueryGraphState
from app.services.llm_service import LLMService, get_llm_service
from app.services.mongo_service import MongoService, get_mongo_service
from app.utils.sse_utils import SSEEvent, push_sse_event
from app.utils.task_utils import set_task_result

_MAX_CONTEXT_LENGTH = 12000
_EMPTY_CONTEXT = "无参考内容"
_NO_CHAT_HISTORY = "暂无历史对话"
_NO_ITEM_NAME = "无指定商品"

class NodeAnswerOutput(NodeBase):

    name: str = "node_answer_output"

    def __init__(self, mongo: MongoService = get_mongo_service(),
                 llm_service: LLMService = get_llm_service()):
        super().__init__()
        self._mongo = mongo
        self._llm_service = llm_service

    def _validate_input_state(self, state: QueryGraphState):
        if "session_id" not in state:
            raise StateFieldError(field_name="session_id", message="State field 'session_id' missing", expected_type=str)
        if "original_query" not in state:
            raise StateFieldError(field_name="original_query", message="State field 'original_query' missing", expected_type=str)

    def _step_1_check_answer(self, answer: str, is_stream: bool, session_id: str) -> bool:
      if answer:
        if is_stream:
          self.logger.info("---Step 1: 发现已有答案，执行流式推送---")
          push_sse_event(session_id, SSEEvent.DELTA, {"delta": answer})
        else:
          set_task_result(session_id, "answer", answer)
        return True
      else:
        return False
      
    def _construct_prompt(self, reranked_docs: List[Dict], history: List[Dict], item_names: List[str], original_query: str, rewritten_query: str) -> str:
        available_chars = _MAX_CONTEXT_LENGTH

        context_str, available_chars = self._format_reranked_docs(reranked_docs or [], available_chars)

        history_str = self._format_chat_history(history or [], available_chars)

        item_names_str = ", ".join(item_names) if item_names else _NO_ITEM_NAME

        question = rewritten_query or original_query

        prompt = ANSWER_PROMPT.format(
            context=context_str or _EMPTY_CONTEXT,
            history=history_str if history_str else _NO_CHAT_HISTORY,
            item_names=item_names_str,
            question=question,
        )
        self.logger.info(f"Prompt constructed: \n{prompt}")
        return prompt

    def _format_reranked_docs(self, reranked_docs: List[Dict], available_chars: int) -> Tuple[str, int]:
        formatted_lines = []
        used_chars = 0
        for idx, doc in enumerate(reranked_docs, start=1):
            
            meta_tags = [f"[{idx}]"]

            for field, template in [
                ("source", "[source={}]"),
                ("chunk_id", "[chunk_id={}]"),
                ("url", "[url={}]"),
                ("title", "[title={}]"),
            ]:
                field_value = str(doc.get(field)).strip()
                if field_value:
                    meta_tags.append(template.format(field_value))

            relevance_score = doc.get("score")
            if relevance_score is not None:
                meta_tags.append(f"[score={float(relevance_score):.4f}]")

            doc_entry = " ".join(meta_tags) + "\n" + doc.get("content")

            if used_chars + len(doc_entry) > available_chars:
                break

            formatted_lines.append(doc_entry)
            used_chars += len(doc_entry) + 2

        return "\n\n".join(formatted_lines), available_chars - used_chars

    def _format_chat_history(self, chat_history: List[Dict], available_chars: int) -> str:
        formatted_lines = []
        used_chars = 0
        for message in chat_history:
            role = message.get("role", "")
            text = message.get("text", "")
            if not text or not role:
                continue
            formatted_line = f"{role}: {text}"
            used_chars += len(formatted_line) + 1

            if used_chars > available_chars:
                return "\n".join(formatted_lines)

            formatted_lines.append(formatted_line)

        return "\n".join(formatted_lines)

    def _generate_response(self, state: QueryGraphState, prompt: str) -> QueryGraphState:
        self.logger.info("---Step 3: 开始生成回答 (LLM Generation)---")

        # 获取 LLM 客户端
        # 注意：这里我们使用统一的 get_llm_client 获取实例
        llm = self._llm_service.get_llm_client()

        # 判断是否需要流式输出
        # 通常 state 中会注入 stream_queue 用于 SSE 推送
        session_id = state.get("session_id")
        is_stream = state.get("is_stream")

        if is_stream:
            self.logger.info(f"模式: 流式输出 (Streaming), Session: {session_id}")
            final_text = ""
            try:
                # 使用 stream 方法进行流式生成
                for chunk in llm.stream(prompt):
                    delta = getattr(chunk, "content", "") or ""
                    if delta:
                        final_text += delta
                        # 将增量内容放入队列
                        push_sse_event(session_id, SSEEvent.DELTA, {"delta": delta})

                self.logger.info(f"流式输出完成，总长度: {len(final_text)}")

            except Exception as e:
                self.logger.error(f"流式生成出错: {e}", exc_info=True)
                push_sse_event(session_id, SSEEvent.ERROR, {"error": str(e)})

            state["answer"] = final_text
        else:
            self.logger.info(f"模式: 非流式输出 (Blocking), Session: {session_id}")
            try:
                response = llm.invoke(prompt)
                content = response.content
                state["answer"] = content
                set_task_result(session_id, "answer", content)
                self.logger.info(f"生成回答完成，长度: {len(content)}")
            except Exception as e:
                self.logger.error(f"生成回答出错: {e}", exc_info=True)
                state["answer"] = "抱歉，生成回答时出现错误。"
        return state

    def _extract_images_from_docs(self, docs):
        """
        辅助方法：从文档列表中提取图片URL

        核心逻辑：
        1. 遍历所有相关文档（包括本地知识库切片和联网搜索结果）。
        2. 策略一：直接检查文档的 'url' 字段（常见于联网搜索结果）。
           - 验证后缀名是否为图片格式 (.jpg, .png 等)。
        3. 策略二：使用正则表达式扫描文档 'text' 正文内容（常见于本地 Markdown 文档）。
           - 匹配 Markdown 图片语法: ![alt text](image_url)。
        4. 对提取到的 URL 进行去重处理，返回唯一图片列表。

        :param docs: 文档列表，每个文档为字典格式
        :return: 图片 URL 字符串列表
        """
        images = []
        seen = set() # 用于去重，避免同一张图片重复出现
        if not docs:
            return []
        # ---------------------------------------------------------
        # 正则表达式解释：r'!\[.*?\]\((.*?)\)'
        # 1. !\[   -> 匹配 Markdown 图片语法的开头 "![" (注意 [ 需要转义)
        # 2. .*?   -> 非贪婪匹配图片描述文本 (Alt Text)，即 [] 中间的内容
        # 3. \]    -> 匹配描述文本的结束符 "]"
        # 4. \(    -> 匹配 URL 部分的开始符 "("
        # 5. (.*?) -> 捕获组 (Group 1)：非贪婪匹配括号内的实际 URL 内容
        # 6. \)    -> 匹配 URL 部分的结束符 ")"
        # ( ... ) （不带反斜杠）：这就是 捕获组 。
        # 它的作用是告诉程序：“虽然我匹配了整个 ![...](...) 结构，但我 只要 这括号里的内容”。
        # ---------------------------------------------------------
        md_img_pattern = re.compile(r'!\[.*?\]\((.*?)\)')

        self.logger.info(f"开始提取图片，待处理文档数: {len(docs)}")

        for i, doc in enumerate(docs):
            # 1. 优先检查 url 字段 (主要针对 Web Search 结果)
            url = (doc.get("url") or "").strip()
            if url:
                # 简单后缀判断：确保是静态图片资源
                if url.lower().endswith(('.png', '.jpg', '.jpeg', '.gif', '.webp', '.bmp', '.svg')):
                    if url not in seen:
                        self.logger.debug(f"文档[{i}] 发现图片 URL (字段): {url}")
                        seen.add(url)
                        images.append(url)

            # 2. 检查 text 字段中的 Markdown 图片 (主要针对 Local Chunk)
            text = (doc.get("content") or "").strip()
            if text:
                # findall 机制解释：
                # 正则表达式 r'!\[.*?\]\((.*?)\)' 中包含一个捕获组 (.*?)
                # 当存在捕获组时，findall 只返回括号内匹配到的内容（即 URL），而不是整个 ![...](...) 字符串
                # 示例：
                # 输入 text: "参考图片 ![面板图](http://img.com/1.jpg) 如下"
                # 返回 matches: ['http://img.com/1.jpg']
                matches = md_img_pattern.findall(text)
                for img_url in matches:
                    img_url = img_url.strip()
                    if img_url and img_url not in seen:
                        self.logger.debug(f"文档[{i}] 正文发现 Markdown 图片: {img_url}")
                        seen.add(img_url)
                        images.append(img_url)

        self.logger.info(f"图片提取完成，共找到 {len(images)} 张唯一图片: {images}")
        return images
    
    def _step_4_write_history(self, state: QueryGraphState, image_urls = None) -> QueryGraphState:
        """
        阶段四：把本轮答案写入 MongoDB history。
        利用 utils/mongo_history_utils.py 中的 save_chat_messages 方法。
        """
        session_id = state.get("session_id", "default")
        answer = (state.get("answer") or "").strip()
        item_names = state.get("item_names") or []

        try:
            if answer:
                self._mongo.save_chat_message(
                    session_id=session_id,
                    role="assistant",
                    text=answer,
                    rewritten_query="",
                    item_names=item_names,
                    image_urls=image_urls,
                    message_id=None
                )
        except Exception as e:
            # 写历史失败不应影响主链路
            self.logger.error(f"写入Mongo历史记录失败: {e}")
        return state
    
    def process(self, state: QueryGraphState) -> QueryGraphState:
        self._validate_input_state(state)
        session_id = state.get("session_id")
        original_query = state.get("original_query")
        rewritten_query = state.get("rewritten_query")
        item_names = state.get("item_names")
        history = state.get("history")
        reranked_docs = state.get("reranked_docs")
        is_stream = state.get("is_stream")

        answer_exists = self._step_1_check_answer(answer, is_stream, session_id)

        if not answer_exists:
            prompt = self._construct_prompt(reranked_docs, item_names, history, original_query, rewritten_query)
            state["prompt"] = prompt

            self._generate_response(state, prompt)

            # 提取图片URL（用于历史记录和前端展示）
            image_urls = self._extract_images_from_docs(state.get("reranked_docs") or [])

        # 阶段四：把答案写入到mongodb的history中
        if state.get("answer"):
            self._step_4_write_history(state, image_urls=image_urls)

        # 阶段五: 流式输出结束，发送 final 事件 [最后兜底，确保图片都能争取渲染和结束]
        self.logger.info(f"---发送 final 事件---图片为：{image_urls}")
        if state.get("is_stream"):
            push_sse_event(
                state['session_id'],
                SSEEvent.FINAL,
                {
                    "answer": state["answer"],
                    "status": "completed",
                    "image_urls": image_urls  # 发送图片URL给前端
                }
            )
        self.logger.info("---node_answer_output 节点处理结束---")
        return state

if __name__ == "__main__":
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
        # print(f"Prompt 预览:\n{result['prompt'][:200]}...")
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