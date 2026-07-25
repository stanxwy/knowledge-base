import asyncio
import threading
import time

from fastapi import FastAPI

app = FastAPI()

# ✅ 正确：异步函数可以用 await
@app.get("/fetch-data-async")
async def fetch_data_async():
    """
    不同的请求，相同的线程编号
    """
    # 模拟耗时操作（如查数据库）
    print(threading.current_thread().ident, "开始")
    await asyncio.sleep(5) # 让出CPU
    print(threading.current_thread().ident, "完成")
    return {"data": "fetch-data完成"}

# ❌ 错误：同步函数不能用 await
@app.get("/fetch-data-sync")
def fetch_data_sync():  # 少了 async
    # await asyncio.sleep(1)  # SyntaxError!
    return {"data": "完成"}

# ⚠️ 勉强能用但不好：同步函数做耗时操作会阻塞
@app.get("/fetch-data-bad")
def fetch_data_bad():
    """
    不同的请求，不同的线程编号
    """
    print(threading.current_thread().ident, "开始")
    time.sleep(5)  # 阻塞整个线程
    print(threading.current_thread().ident, "完成")
    return {"data": "fetch-data-bad完成"}

# ✅ 推荐：即使现在不需要 await，以后可能需要
@app.get("/users/{user_id}")
async def get_user(user_id: int):
    # 现在很简单
    res = asyncio.sleep(3)
    print(threading.current_thread().ident)
    """
    untimeWarning: coroutine 'sleep' was never awaited
    return await dependant.call(**values)
    RuntimeWarning: Enable tracemalloc to get the object allocation traceback
    """
    print(res) # <coroutine object sleep at 0x000002BA81B5B340>
    return {"user_id": user_id}
    
    # 以后如果要查数据库，直接加 await 就行
    # user = await db.query(user_id)
    # return user

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="127.0.0.1", port=8000)

# uv run uvicorn app.test.fastapi.demo08_sync:app --reload