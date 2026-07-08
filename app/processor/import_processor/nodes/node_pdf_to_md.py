import json
import logging
import shutil
import time
import zipfile
from pathlib import Path

import requests

from app.config.mineru_config import mineru_config
from app.processor.import_processor.base import BaseNode, setup_logging
from app.processor.import_processor.exceptions import StateFieldError, FileProcessingError, ConfigurationError, \
    PdfConversionError
from app.processor.import_processor.state import ImportGraphState


class NodePDFToMD(BaseNode):
    """
    PDF 转 Markdown 节点：PDF结构化解析
    """

    name = "node_pdf_to_md"
    
    def _step_1_validate_paths(self, state: ImportGraphState) -> tuple[Path, Path]:
        """
        步骤1：校验PDF文件路径和输出目录
        核心职责：参数非空校验 | 路径转换 | PDF文件有效性校验 | 输出目录自动创建
        返回：合法的PDF文件Path对象、输出目录Path对象
        异常：StateFieldError(参数缺失)、FileProcessingError(文件无效)
        """
        # 1、参数非空校验
        pdf_path = state.get("pdf_path")
        if not pdf_path:
            raise StateFieldError(field_name='pdf_path', expected_type=str)

        output_file_dir = state.get("output_file_dir")
        if not output_file_dir:
            raise StateFieldError(field_name='output_file_dir', expected_type=str)

        # 2、转换为Path对象统一处理路径
        pdf_path_obj = Path(pdf_path)
        output_dir_obj = Path(output_file_dir)

        # 3、PDF文件有效性校验
        if not pdf_path_obj.exists():
            raise FileProcessingError(message=f"PDF文件{pdf_path_obj.name}不存在")

        # 4、确保输出目录存在，不存在则递归创建
        if not output_dir_obj.exists():
            self.logger.info(f"输出目录不存在，自动创建：{output_dir_obj.absolute()}")
            output_dir_obj.mkdir(parents=True, exist_ok=True)

        return pdf_path_obj, output_dir_obj

    def _step_2_upload_and_poll(self, pdf_path_obj: Path) -> str:
        return "full.zip"

    def _step_3_download_and_extract(self, zip_url: str, output_dir_obj: Path, pdf_stem: str) -> str:
        return "./README.md"

    def process(self, state: ImportGraphState):
        """
        :param state: `pdf_path`、`file_dir`
        :return: `md_path`、`md_content`
        """

        update_state = {}
        # 步骤1：校验PDF路径和输出目录
        pdf_path_obj, output_dir_obj = self._step_1_validate_paths(state)

        # 步骤2：上传PDF至MinerU并轮询解析结果
        zip_url = self._step_2_upload_and_poll(pdf_path_obj)

        # 步骤3：下载ZIP包并提取MD文件
        md_path = self._step_3_download_and_extract(zip_url, output_dir_obj, pdf_path_obj.stem)

        # 步骤4：读取md的内容
        with open(md_path, "r", encoding="utf-8") as f:
            md_content = f.read()

        # 步骤5：更新state状态
        update_state["md_path"] = md_path
        update_state["md_content"] = md_content

        return update_state

    
if __name__ == "__main__":
    setup_logging()

    init_state = {
        "pdf_path": "./README.md",
        "output_file_dir": "/output"
    }
    node_pdf_to_md = NodePDFToMD()
    result = node_pdf_to_md(init_state)
    logging.getLogger().info(json.dumps(result, ensure_ascii=False, indent=4))