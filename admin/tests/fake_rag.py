"""Tiny fake RAG server for Phase-5 SSE integration tests.

Exposes the three endpoints admin actually calls:
  POST /api/v1/recall  → returns hard-coded hits whose file_titles can be
                         overridden by setting the env var FAKE_RAG_UNIT_CODES
                         (comma-separated) before launch. Defaults to two
                         "fake" codes that admin doesn't actually have — so
                         admin falls into the no-KB-hit branch.
  POST /api/v1/embed   → returns dummy vectors
  POST /api/v1/query   → returns {session_id, task_id}
  GET  /api/v1/stream/{sid} → emits a fixed SSE answer sequence, then DONE

Run: python admin/tests/fake_rag.py  (listens on 127.0.0.1:8001)
"""
import asyncio
import os
import uuid

from fastapi import FastAPI
from fastapi.responses import StreamingResponse

app = FastAPI(title="fake-rag")

# Configurable per run: which unit_codes to advertise from recall?
_DEFAULT_CODES = ["KU-FAKE-0001", "KU-FAKE-0002"]
_CODES = os.environ.get("FAKE_RAG_UNIT_CODES", ",".join(_DEFAULT_CODES)).split(",")
_FAKE_ANSWER = "根据知识库,冰箱不制冷一般是压缩机问题或制冷剂泄漏。"


@app.post("/api/v1/recall")
async def recall(payload: dict):
    query = payload.get("query", "")
    return {
        "hits": [
            {"file_title": code, "item_name": "冰箱维修", "score": score}
            for code, score in zip(_CODES, [0.91, 0.73])
        ]
    }


@app.post("/api/v1/embed")
async def embed(payload: dict):
    return {"dense": [[0.0] * 1024], "sparse": [{}]}


@app.post("/api/v1/query")
async def query(payload: dict):
    sid = uuid.uuid4().hex
    return {"message": "Task submitted", "session_id": sid, "task_id": sid}


@app.get("/api/v1/stream/{session_id}")
async def stream(session_id: str):
    async def gen():
        import json
        # emit two token events, then done
        for tok in ["根据知识库,", "冰箱不制冷一般是压缩机问题。"]:
            yield f"event: PROGRESS\ndata: {json.dumps({'type': 'progress', 'data': {'token': tok}})}\n\n"
            await asyncio.sleep(0.05)
        yield (
            f"event: DONE\ndata: {json.dumps({'type': 'done', 'data': {'answer': _FAKE_ANSWER, 'prompt_tokens': 120, 'completion_tokens': 36}})}\n\n"
        )

    return StreamingResponse(gen(), media_type="text/event-stream")


if __name__ == "__main__":
    import uvicorn

    uvicorn.run(app, host="127.0.0.1", port=8001)