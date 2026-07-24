from collections import defaultdict
from typing import dict, list

# init with [] if key not exist
_tasks_running_list: dict[str, list[str]] = defaultdict(list)
_tasks_done_list: dict[str, list[str]] = defaultdict(list)

# init with {} if key not exist
_tasks_result: dict[str, dict[str, str]] = defaultdict(dict)

_tasks_status: dict[str, str] = {}

TASK_STATUS_PROCESSING = "processing"
TASK_STATUS_COMPLETED = "completed"
TASK_STATUS_FAILED = "failed"

_NODE_NAME_TO_CN: dict[str, str] = {
    "upload_file": "上传文件",
    "entry": "检查文件",
    "pdf_to_md_node": "PDF转Markdown",
    "md_img_node": "Markdown图片处理",
    "document_split_node": "文档切分",
    "item_name_recognition": "主体名称识别",
    "bge_embedding_chunks_node": "向量生成",
    "import_milvus_node": "导入向量数据库",
    # "knowledge_graph_node": "导入知识图谱",
    "__end__": "处理完成",

    "item_name_confirm_node": "确认问题产品",
    "answer_output_node": "生成答案",
    "rerank_node": "重排序",
    "rrf_node": "倒排融合",
    "mcp_search_node": "网络搜索",
    "vector_search_node": "切片搜索",
    "hyde_search_node": "切片搜索(假设性文档)",
    # "kg_search_node": "查询知识图谱"
}


def _to_cn(node_name: str) -> str:
    return _NODE_NAME_TO_CN.get(node_name, node_name)


def add_running_task(task_id: str, node_name: str) -> None:
    # if task_id not in _tasks_running_list, running list will be initialized to [] and returned
    running = _tasks_running_list[task_id]
    if node_name not in running:
        running.append(node_name)

def add_done_task(task_id: str, node_name: str) -> None:
    # remove existing node from running list then add to done list
    if node_name in _tasks_running_list[task_id]:
        _tasks_running_list[task_id].remove(node_name)

    done = _tasks_done_list[task_id]
    if node_name not in done:
        done.append(node_name)


def get_running_task_list(task_id: str) -> list[str]:
    return [_to_cn(n) for n in _tasks_running_list.get(task_id, [])]

def get_done_task_list(task_id: str) -> list[str]:
    return [_to_cn(n) for n in _tasks_done_list.get(task_id, [])]


def get_task_status(task_id: str) -> str:
    return _tasks_status.get(task_id, "")

def update_task_status(task_id: str, status_name: str) -> None:
    _tasks_status[task_id] = status_name


def set_task_result(task_id: str, key: str, value: str) -> None:
    _tasks_result[task_id][key] = value

def get_task_result(task_id: str, key: str, default: str = "") -> str:
    return _tasks_result.get(task_id, {}).get(key, default)


def clear_task(task_id: str):
    _tasks_running_list.pop(task_id, None)
    _tasks_done_list.pop(task_id, None)
    _tasks_status.pop(task_id, None)
    # _tasks_result.pop(task_id, None)