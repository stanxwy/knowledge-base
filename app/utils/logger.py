import colorlog 
import logging
import os
from logging.handlers import TimedRotatingFileHandler

def setup_logging(level: int = logging.INFO, log_dir: str = "./logs"):
    """
    配置日志：同时输出到控制台和指定目录的日志文件

    Args:
        level: 日志级别
        log_dir: 日志文件存储目录（默认 ./logs）
    """
    # 1. 创建日志目录（如果不存在）
    os.makedirs(log_dir, exist_ok=True)
    
    # 2. 生成日志文件名（按日期命名，避免单个文件过大）
    # log_filename = f"app_{datetime.now().strftime('%Y%m%d')}.log"
    # log_filepath = os.path.join(log_dir, log_filename)
    log_filepath = os.path.join(log_dir, "knowledge_base.log")

    # 3. 创建根 logger
    logger = logging.getLogger()
    logger.setLevel(level)
    
    # 4. 清除已有的 handler（避免重复添加，影响性能）
    if logger.hasHandlers():
        logger.handlers.clear()
    
    # 5. 定义统一的日志格式
    file_formatter = logging.Formatter(
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
    file_handler.setFormatter(file_formatter)
    logger.addHandler(file_handler)
    
    # 控制台输出（开发环境保留，生产环境可以去掉）
    console_formatter = colorlog.ColoredFormatter(
        '%(log_color)s%(asctime)s - %(name)s - %(levelname)s - %(message)s',
        datefmt='%Y-%m-%d %H:%M:%S',
        log_colors={
            'DEBUG': 'cyan',
            # 'INFO': 'green',  # INFO 显示为绿色
            'WARNING': 'yellow',
            'ERROR': 'red',
            'CRITICAL': 'bold_red',
        }
    )
    console_handler = logging.StreamHandler()
    console_handler.setLevel(level)
    console_handler.setFormatter(console_formatter)
    logger.addHandler(console_handler)
    
    logger.info(f"日志系统初始化完成，日志文件: {log_filepath}")
    return logger