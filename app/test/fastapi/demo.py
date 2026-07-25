import time

import uvicorn
from fastapi import FastAPI
from loguru import logger
from pydantic import BaseModel

"""
可以通过2种方式运行：
uv run uvicorn app.test.fastapi.demo:app --reload

python -m app.test.fastapi.demo
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
    time.sleep(5)
    return {"name": item.name, "price": item.price, "is_offer": item.is_offer, "success": True}


# 1、路由处理函数返回一个 Pydantic 模型实例，FastAPI 将自动将其转换为 JSON 格式，并作为响应发送给客户端：
@app.post("/items/return", summary="返回 Pydantic 模型实例")
async def create_and_return_item(item: Item):
    return item


# 2、使用 HTTPException 抛出异常，返回自定义的状态码和详细信息。
# 以下实例在 item_id 为 42 会返回 404 状态码：
@app.delete("/items/{item_id}", summary="抛出异常")
async def read_item_exception(item_id: int):
    from fastapi import HTTPException
    if item_id == 42:
        raise HTTPException(status_code=404, detail="Item 找不到")
    return {"item_id": item_id}



@app.get("/api/user")
async def get_user():
    from fastapi.responses import JSONResponse
    # 等价于直接 return {"name": "张三", "age": 20}（FastAPI 自动转 JSONResponse）
    return JSONResponse(
        content={"name": "张三", "age": 20},
        status_code=200,  # 可选，默认 200
        headers={"X-Custom-Header": "custom-value"}  # 可选，自定义响应头
    )



@app.get("/download/pdf")
async def download_pdf():
    from fastapi.responses import FileResponse
    pdf_path = "./test_data/kb/B530.pdf"
    # 返回文件并指定下载文件名
    return FileResponse(
        path=pdf_path,
        filename="file.pdf",
        # media_type="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet"
        media_type="application/pdf"
    )



@app.get("/hello")
async def hello(name: str = "游客"):
    from fastapi.responses import HTMLResponse
    html_content = f"""
    <html>
        <body>
            <h1>你好，{name}！</h1>
        </body>
    </html>
    """
    return HTMLResponse(content=html_content, status_code=200)



@app.get("/text")
async def get_text():
    from fastapi.responses import PlainTextResponse
    return PlainTextResponse(content="这是纯文本响应", status_code=200)




@app.get("/old-path")
async def redirect_old_path():
    from fastapi.responses import RedirectResponse
    # 重定向到 /new-path，状态码 307 表示临时重定向
    return RedirectResponse(url="/new-path", status_code=307)

@app.get("/new-path")
async def new_path():
    return {"message": "这是新接口"}



async def generate_stream():
    import asyncio
    # 模拟流式输出（逐字返回）
    words = ["你", "好", "，", "这", "是", "流", "式", "响", "应"]
    for word in words:
        await asyncio.sleep(0.5)
        yield word.encode("utf-8")  # 流式输出需返回字节流

@app.get("/stream")
async def stream_response():
    from fastapi.responses import StreamingResponse
    return StreamingResponse(generate_stream(), media_type="text/event-stream")



@app.get("/custom")
async def custom_response():
    from fastapi.responses import Response
    # 返回二进制数据，指定自定义 MIME 类型
    return Response(
        content="<h1>纯文本</h1>",
        # media_type="text/text",
        media_type="text/html",
        status_code=200)


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
(knowledge-base) PS D:\knowledge-base> uv run uvicorn app.test.fastapi.demo:app --reload
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
(knowledge-base) PS D:\knowledge-base> python -m app.test.fastapi.demo
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