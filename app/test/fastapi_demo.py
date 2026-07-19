from fastapi import FastAPI

# 创建一个 FastAPI 应用实例
app = FastAPI()

@app.get("/", summary="第一个测试")
async def read_root():
    return {"Hello": "World"}

"""
(knowledge-base) PS D:\knowledge-base> uv run uvicorn app.test.fastapi_demo:app --reload
INFO:     Will watch for changes in these directories: ['D:\\knowledge-base']
INFO:     Uvicorn running on http://127.0.0.1:8000 (Press CTRL+C to quit)
INFO:     Started reloader process [23396] using WatchFiles
INFO:     Started server process [34472]
INFO:     Waiting for application startup.
INFO:     Application startup complete.
INFO:     127.0.0.1:8591 - "GET / HTTP/1.1" 200 OK
INFO:     127.0.0.1:8591 - "GET /favicon.ico HTTP/1.1" 404 Not Found
INFO:     Shutting down
INFO:     Waiting for application shutdown.
INFO:     Application shutdown complete.
INFO:     Finished server process [34472]
INFO:     Stopping reloader process [23396]
"""