import logging
from typing import Deque
import time

logger = logging.getLogger(__name__)

def apply_api_rate_limit(
    request_times: Deque[float],
    max_requests: int,
    window_seconds: int = 60
) -> None:
    """
    通用滑动窗口API速率限制器（抽离为公共工具）
    核心逻辑：维护请求时间戳双端队列，窗口内请求数超上限则自动等待，防止触发第三方API限流
    :param request_times: 存储请求时间戳的双端队列，需外部初始化（全局/单例），跨调用复用
    :param max_requests: 速率限制窗口内的最大允许请求次数
    :param window_seconds: 速率限制滑动窗口时长，默认60秒（1分钟）
    :return: None，超出限制时会阻塞等待
    """
    current_time = time.time()

    # clean up the sliding window of expired requests
    while request_times and current_time - request_times[0] >= window_seconds:
        request_times.popleft()

    if len(request_times) >= max_requests:
        # calculate the time to wait (window total time - elapsed time of the earliest request)
        sleep_duration = window_seconds - (current_time - request_times[0])
        if sleep_duration > 0:
            logger.info(f"Triggered API rate limit, window {window_seconds}s has a maximum of {max_requests} requests, need to wait: {sleep_duration:.2f}s")
            time.sleep(sleep_duration)
            # clear expired requests on wakeup
            current_time = time.time()
            while request_times and current_time - request_times[0] >= window_seconds:
                request_times.popleft()

    request_times.append(current_time)
    logger.info(f"API request time stamp has been recorded, current {window_seconds}s window request count: {len(request_times)}")