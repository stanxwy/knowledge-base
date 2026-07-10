import time
from datetime import datetime
from collections import deque
from typing import Deque

def timestamp():
    return datetime.now().strftime('%Y-%m-%d %H:%M:%S')

def limit(request_deque: Deque[float],
        max_requests: int,
        window_seconds: int = 60
    ):

    def remove_expired(request_deque: Deque[float], current_time: float, window_seconds: int):
        while request_deque and current_time - request_deque[0] >= window_seconds:
            request_deque.popleft()


    # 1. 清理滑动窗口外的过期请求时间戳，保证队列仅存窗口内的请求
    current_time = time.time()
    remove_expired(request_deque, current_time, window_seconds)

    # 2. 窗口内请求数达上限，计算并阻塞等待剩余时间
    if len(request_deque) >= max_requests:
        # 计算需要等待的时长（窗口总时长 - 最早请求已存在的时长）
        sleep_duration = window_seconds - (current_time - request_deque[0])
        if sleep_duration > 0:
            print(f"{timestamp()} 触发API速率限制，窗口{window_seconds}秒内最多{max_requests}次，需等待：{sleep_duration:.2f} 秒")
            time.sleep(sleep_duration)
            # 等待后更新当前时间，重新清理过期请求（避免等待期间有请求过期）
            current_time = time.time()
            remove_expired(request_deque, current_time, window_seconds)

    # 3. 记录当前请求时间戳，加入滑动窗口队列
    request_deque.append(time.time())
    global index
    print(f"{timestamp()} 新增API请求{index}时间戳，当前{window_seconds}秒窗口内请求数：{len(request_deque)}")

timestamps = deque()

# 2、循环处理图片
index = 0
for i in range(20):
    index += 1
    print(f"{timestamp()} 请求{index}，当前队列长度：", len(timestamps))
    limit(timestamps, max_requests=5, window_seconds=10)
    time.sleep(1)

"""
2026-07-10 08:54:59 请求1，当前队列长度： 0
2026-07-10 08:54:59 新增API请求1时间戳，当前10秒窗口内请求数：1
2026-07-10 08:55:00 请求2，当前队列长度： 1
2026-07-10 08:55:00 新增API请求2时间戳，当前10秒窗口内请求数：2
2026-07-10 08:55:01 请求3，当前队列长度： 2
2026-07-10 08:55:01 新增API请求3时间戳，当前10秒窗口内请求数：3
2026-07-10 08:55:02 请求4，当前队列长度： 3
2026-07-10 08:55:02 新增API请求4时间戳，当前10秒窗口内请求数：4
2026-07-10 08:55:03 请求5，当前队列长度： 4
2026-07-10 08:55:03 新增API请求5时间戳，当前10秒窗口内请求数：5
2026-07-10 08:55:04 请求6，当前队列长度： 5
2026-07-10 08:55:04 触发API速率限制，窗口10秒内最多5次，需等待：5.00 秒
2026-07-10 08:55:09 新增API请求6时间戳，当前10秒窗口内请求数：5
2026-07-10 08:55:10 请求7，当前队列长度： 5
2026-07-10 08:55:10 新增API请求7时间戳，当前10秒窗口内请求数：5
2026-07-10 08:55:11 请求8，当前队列长度： 5
2026-07-10 08:55:11 新增API请求8时间戳，当前10秒窗口内请求数：5
2026-07-10 08:55:12 请求9，当前队列长度： 5
2026-07-10 08:55:12 新增API请求9时间戳，当前10秒窗口内请求数：5
2026-07-10 08:55:13 请求10，当前队列长度： 5
2026-07-10 08:55:13 新增API请求10时间戳，当前10秒窗口内请求数：5
2026-07-10 08:55:14 请求11，当前队列长度： 5
2026-07-10 08:55:14 触发API速率限制，窗口10秒内最多5次，需等待：5.00 秒
2026-07-10 08:55:19 新增API请求11时间戳，当前10秒窗口内请求数：5
2026-07-10 08:55:20 请求12，当前队列长度： 5
2026-07-10 08:55:20 新增API请求12时间戳，当前10秒窗口内请求数：5
2026-07-10 08:55:21 请求13，当前队列长度： 5
2026-07-10 08:55:21 新增API请求13时间戳，当前10秒窗口内请求数：5
2026-07-10 08:55:22 请求14，当前队列长度： 5
2026-07-10 08:55:22 新增API请求14时间戳，当前10秒窗口内请求数：5
2026-07-10 08:55:23 请求15，当前队列长度： 5
2026-07-10 08:55:23 新增API请求15时间戳，当前10秒窗口内请求数：5
2026-07-10 08:55:24 请求16，当前队列长度： 5
2026-07-10 08:55:24 触发API速率限制，窗口10秒内最多5次，需等待：5.00 秒
2026-07-10 08:55:29 新增API请求16时间戳，当前10秒窗口内请求数：5
2026-07-10 08:55:30 请求17，当前队列长度： 5
2026-07-10 08:55:30 新增API请求17时间戳，当前10秒窗口内请求数：5
2026-07-10 08:55:31 请求18，当前队列长度： 5
2026-07-10 08:55:31 新增API请求18时间戳，当前10秒窗口内请求数：5
2026-07-10 08:55:32 请求19，当前队列长度： 5
2026-07-10 08:55:32 新增API请求19时间戳，当前10秒窗口内请求数：5
2026-07-10 08:55:33 请求20，当前队列长度： 5
2026-07-10 08:55:33 新增API请求20时间戳，当前10秒窗口内请求数：5
"""