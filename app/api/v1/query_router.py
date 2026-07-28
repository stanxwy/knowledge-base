import logging
import uuid

from fastapi import APIRouter, BackgroundTasks, Depends, HTTPException, Request
from fastapi.responses import StreamingResponse

from app.api.v1.deps import DocumentStore, get_doc_store
from app.schema.query_schema import QueryRequest
from app.utils.sse_utils import (
    SSEEvent,
    create_sse_queue,
    push_sse_event,
    sse_generator,
)
from app.utils.task_utils import (
    TASK_STATUS_COMPLETED,
    TASK_STATUS_FAILED,
    TASK_STATUS_PROCESSING,
    clear_task,
    get_done_task_list,
    get_running_task_list,
    get_task_result,
    get_task_status,
    update_task_status,
)
from app.workflows.query.main_graph import KBQueryWorkflow

logger = logging.getLogger(__name__)

router = APIRouter(tags=["query"])


@router.post("/query")
async def query(background_tasks: BackgroundTasks, request: QueryRequest):
    try:
        user_query = request.query
        session_id = request.session_id if request.session_id else str(uuid.uuid4())
        clear_task(session_id)
    
        is_stream = request.is_stream
        if is_stream:
            create_sse_queue(session_id)
    
        update_task_status(session_id, TASK_STATUS_PROCESSING, is_stream)
        logger.info(f"Starting Query Workflow task {session_id}, query: {user_query}, is_stream: {is_stream}")
    
        if is_stream:
            # 如果是流式，则返回一个流式响应，过程不断地推送
            background_tasks.add_task(run_query_graph, session_id, user_query, is_stream)
            logger.info(f"[{session_id}] Query Workflow task submitted to background executor")
            return {
                "message": "Task started",
                "session_id": session_id
            }
        else:
            run_query_graph(session_id, user_query, is_stream)
            answer = get_task_result(session_id, "answer", "")
            return {
                "message": "Task completed",
                "session_id": session_id,
                "answer": answer,
                "done_list": get_done_task_list(session_id)
            }
    except Exception as e:
        logger.exception(f"Error running Query Workflow task: {e!s}", stack_info=True)
        raise HTTPException(status_code=500, detail=f"Error running Query Workflow task: {e}")


def run_query_graph(session_id: str, user_query: str, is_stream: bool = True):
    logger.info(f"Query Workflow started... {session_id} {user_query} {is_stream}")

    init_state = {
        "original_query": user_query,
        "session_id": session_id,
        "is_stream": is_stream
    }

    try:
        workflow = KBQueryWorkflow()
        workflow.run(init_state) #, stream=is_stream)
        if is_stream:
            push_sse_event(session_id, SSEEvent.PROGRESS, {
                "status": get_task_status(session_id),
                "done_list": get_done_task_list(session_id),
                "running_list": get_running_task_list(session_id),
            })
        logger.info(f"[{session_id}] Query Workflow task completed")
        update_task_status(session_id, TASK_STATUS_COMPLETED, is_stream)
    except Exception as e:
        logger.exception(f"[{session_id}] error running Query Workflow task: {e!s}", stack_info=True)
        update_task_status(session_id, TASK_STATUS_FAILED, is_stream)
        if is_stream:
            push_sse_event(session_id, SSEEvent.ERROR, {"error": str(e)})
        

@router.get("/stream/{session_id}")
async def stream(session_id: str, request: Request):
    logger.info(f"{session_id} started streaming...")
    logger.info(request)
    return StreamingResponse(
        sse_generator(session_id, request),
        media_type="text/event-stream",
        headers={
            "Cache-Control": "no-cache",
            "Connection": "keep-alive",
            "X-Accel-Buffering": "no"
        }
    )

@router.delete("/history/{session_id}")
async def clear_chat_history(session_id: str, docStore: DocumentStore = Depends(get_doc_store)):
    count = docStore.clear_history(session_id)
    return {"message": "Message history cleared", "deleted_count": count}

@router.get("/history/{session_id}")
async def history(session_id: str, limit: int = 50, docStore: DocumentStore = Depends(get_doc_store)):
    try:
        records = docStore.get_recent_messages(session_id, limit=limit)
        items = []
        for r in records:
            items.append({
                "_id": str(r.get("_id")) if r.get("_id") is not None else "",
                "session_id": r.get("session_id", ""),
                "role": r.get("role", ""),
                "text": r.get("text", ""),
                "rewritten_query": r.get("rewritten_query", ""),
                "item_names": r.get("item_names", []),
                "ts": r.get("ts")
            })
        return {"session_id": session_id, "items": items}
    except Exception as e:
        logger.exception(f"history error: {e!s}", stack_info=True)
        raise HTTPException(status_code=500, detail=f"history error: {e}")
