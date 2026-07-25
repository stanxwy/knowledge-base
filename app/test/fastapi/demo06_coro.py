import asyncio
import time


# 1. 定义【异步函数】
async def my_task():
    await asyncio.sleep(1)
    return "完成"

# 2. 调用异步函数时，返回的是【协程对象】
coroutine = my_task()  # 这是一个协程（还没执行）
print(type(coroutine))

# 3. 用 asyncio 来【运行协程】
print(f"{time.time()}: 开始...")
result = asyncio.run(coroutine)  # 启动协程，得到结果
print(f"{time.time()}: {result}")