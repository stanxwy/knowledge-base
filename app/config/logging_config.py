import logging
import os
from logging.handlers import TimedRotatingFileHandler
from datetime import datetime

def setup_logging(level: int = logging.INFO, log_dir: str = "./logs"):
    """
    配置项目日志，按天轮转，保留30天
    """
    os.makedirs(log_dir, exist_ok=True)
    
    log_filepath = os.path.join(log_dir, "knowledge_base.log")
    
    logger = logging.getLogger()
    logger.setLevel(level)
    logger.handlers.clear()
    
    formatter = logging.Formatter(
        fmt='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
        datefmt='%Y-%m-%d %H:%M:%S'
    )
    
    # 按天轮转，保留30天
    file_handler = TimedRotatingFileHandler(
        log_filepath,
        when="midnight",
        interval=1,
        backupCount=30,
        encoding='utf-8'
    )
    file_handler.suffix = "%Y%m%d"  # 备份文件命名格式
    file_handler.setLevel(level)
    file_handler.setFormatter(formatter)
    logger.addHandler(file_handler)
    
    # 控制台输出（开发环境保留，生产环境可以去掉）
    console_handler = logging.StreamHandler()
    console_handler.setLevel(level)
    console_handler.setFormatter(formatter)
    logger.addHandler(console_handler)
    
    logger.info(f"日志系统初始化完成，日志文件: {log_filepath}")