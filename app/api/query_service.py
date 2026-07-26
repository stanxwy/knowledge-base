import logging
import os
import uuid
from pathlib import Path

import uvicorn
from dotenv import load_dotenv
from fastapi import BackgroundTasks, FastAPI, HTTPException, Request
from fastapi.responses import FileResponse, StreamingResponse
from pydantic import BaseModel, Field

from app.core.config import settings
from app.middleware.cors import setup_cors
from app.middleware.request_logger import request_logger_middleware
from app.processor.query_processor.main_graph import KBQueryWorkflow
from app.services.mongo_service import get_mongo_service
from app.utils.logger import setup_logging
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
    get_done_task_list,
    get_task_result,
    update_task_status,
)

load_dotenv(override=True)
setup_logging(os.getenv("LOG_LEVEL", logging.INFO))
logger = logging.getLogger(__name__)

app = FastAPI(
    title="Knowledge Base Query API",
    description="This document describes the API of the Knowledge Base Query Workflow",
)
app.middleware("http")(request_logger_middleware)
setup_cors(app, settings.BACKEND_CORS_ORIGINS)

class QueryRequest(BaseModel):
    query: str = Field(..., description="user query")
    session_id: str = Field(None, description="session id for query")
    is_stream: bool = Field(False, description="whether use stream mode")

@app.get("/chat.html")
async def chat():
    current_dir_parent_path = Path(__file__).absolute().parent.parent
    html_path = current_dir_parent_path / "pages" / "chat.html"
    if not html_path.exists():
        raise HTTPException(status_code=404, detail=f"Page not found: {html_path}")
    return FileResponse(html_path)

@app.post("/query")
async def query(background_tasks: BackgroundTasks, request: QueryRequest):
    user_query = request.query
    session_id = request.session_id if request.session_id else str(uuid.uuid4())

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


def run_query_graph(session_id: str, user_query: str, is_stream: bool = True):
    logger.info(f"Query Workflow started... {session_id} {user_query} {is_stream}")

    init_state = {
        "original_query": user_query,
        "session_id": session_id,
        "is_stream": is_stream
    }

    try:
        workflow = KBQueryWorkflow()
        workflow.run(init_state, stream=is_stream)
        logger.info(f"[{session_id}] Query Workflow task completed")
        update_task_status(session_id, TASK_STATUS_COMPLETED, is_stream)
    except Exception as e:
        logger.exception(f"[{session_id}] error running Query Workflow task: {e!s}", stack_info=True)
        update_task_status(session_id, TASK_STATUS_FAILED, is_stream)
        if is_stream:
            push_sse_event(session_id, SSEEvent.ERROR, {"error": str(e)})

@app.get("/stream/{session_id}")
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

@app.delete("/history/{session_id}")
async def clear_chat_history(session_id: str):
    count = get_mongo_service().clear_history(session_id)
    return {"message": "Message history cleared", "deleted_count": count}

@app.get("/history/{session_id}")
async def history(session_id: str, limit: int = 50):
    try:
        records = get_mongo_service().get_recent_messages(session_id, limit=limit)
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
        raise HTTPException(status_code=500, detail=f"history error: {e}")
    

@app.get("/health")
async def health():
    return {"ok": True}

if __name__ == "__main__":
    uvicorn.run(app, host="127.0.0.1", port=8001)