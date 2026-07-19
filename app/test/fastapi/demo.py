import uvicorn
from fastapi import FastAPI
from loguru import logger
from pydantic import BaseModel

"""
可以通过2种方式运行：
uv run uvicorn app.test.fastapi_demo:app --reload

python -m app.test.fastapi_demo
"""

# 创建一个 FastAPI 应用实例
app = FastAPI()

@app.get("/", summary="第一个测试")
async def read_root():
    return {"Hello": "World"}

# 访问 http://127.0.0.1:8000/items/5?q=somequery
# item_id: 路径参数 (自动转为 int)
# q: 查询参数 (可选，默认 None)
@app.get("/items/{item_id}", summary="获取指定参数")
async def read_item(item_id: int, q: str | None = None):
    return {"item_id": item_id, "q": q}


# 接收? skip=? & limit = ?
@app.get("/items", summary="分页")
async def read_items(skip: int = 0, limit: int = 10):
    return {"skip": skip, "limit": limit}



# 定义数据模型
class Item(BaseModel):
    name: str
    price: float
    is_offer: bool = None

# POST 请求接收 JSON 数据
@app.post("/items/", summary="类型检查")
async def create_item(item: Item):
    # item 已经是验证过的 Item 对象
    # 如果客户端传来的 price 是字符串 "abc"，FastAPI 会自动报错
    return {"name": item.name, "price": item.price, "is_offer": item.is_offer}

if __name__ == "__main__":
    """服务启动入口：本地开发环境直接运行"""
    logger.info("File Import Service 服务启动中...")
    # 启动uvicorn服务，绑定本地IP和8000端口，关闭自动重载（生产环境建议用workers多进程）
    uvicorn.run(
        app=app,
        host="127.0.0.1",  # 仅本地访问，生产环境改为0.0.0.0（允许所有IP访问）
        port=8000  # 服务端口
    )

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

"""
(knowledge-base) PS D:\knowledge-base> python -m app.test.fastapi_demo
2026-07-19 12:42:53.657 | INFO     | __main__:<module>:27 - File Import Service 服务启动中...
INFO:     Started server process [14364]
INFO:     Waiting for application startup.
INFO:     Application startup complete.
INFO:     Uvicorn running on http://127.0.0.1:8000 (Press CTRL+C to quit)
INFO:     127.0.0.1:4838 - "GET / HTTP/1.1" 200 OK
INFO:     127.0.0.1:32348 - "GET /items HTTP/1.1" 200 OK
INFO:     127.0.0.1:54190 - "GET /items/123 HTTP/1.1" 200 OK
INFO:     127.0.0.1:52305 - "GET /items/123?q=abc HTTP/1.1" 200 OK
INFO:     127.0.0.1:30004 - "GET /items/?skip=10&limit=20 HTTP/1.1" 307 Temporary Redirect
INFO:     127.0.0.1:30004 - "GET /items?skip=10&limit=20 HTTP/1.1" 200 OK
INFO:     Shutting down
INFO:     Waiting for application shutdown.
INFO:     Application shutdown complete.
INFO:     Finished server process [14364]
"""