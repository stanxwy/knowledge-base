import json
from loguru import logger
from pathlib import Path
from typing import Dict, List

def backup_json(file_path: Path, json_data: Dict | List ) -> None:
    try:
        # 拼接备份文件路径：固定文件名，便于查找
        # 写入JSON文件：保留中文/格式化缩进，便于人工查看
        with open(file_path, "w", encoding="utf-8") as f:
            """
            json 是Python 嵌套数据结构（List[Dict[str, str]]，列表里装字典，字典里可能嵌套字符串 / 数字等），而普通文件写入
            （如f.write(sections)）仅支持写入字符串，直接写 Python 数据结构会报错。
            json.dump的核心作用就是：将 Python 原生数据结构（列表、字典、字符串、数字等）直接序列化并写入 JSON 文件，无需手动转换为字符串，
            同时保证数据格式规范、可跨语言 / 跨场景读取，完美适配「Chunk 列表备份」的需求。
            """
            json.dump(
                json_data,
                f,
                # 开启 True："title": "\u4e00\u7ea7\u6807\u9898"（乱码，无法直接看）；
                # 开启 False："title": "一级标题"（正常中文，人工可直接阅读）。
                ensure_ascii=False,  # 保留中文，不转义为\u编码
                indent=2             # 格式化缩进，便于阅读
            )
        logger.info(f"步骤6：json结果备份成功，备份文件路径：{file_path}")
    except Exception as e:
        # 备份失败仅记录日志，不终止主流程
        logger.error(f"步骤6：json结果备份失败，错误信息：{str(e)}", exc_info=False)