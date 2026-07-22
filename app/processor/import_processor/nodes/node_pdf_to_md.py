import json
from pathlib import Path

from app.processor.import_processor.base import BaseNode
from app.processor.import_processor.exceptions import StateFieldError, FileProcessingError
from app.processor.import_processor.state import ImportGraphState
from app.services.mineru_service import MineruService, get_mineru_service

class NodePDFToMD(BaseNode):
    """
    PDF 转 Markdown 节点：PDF结构化解析
    """
    name: str = "node_pdf_to_md"

    def __init__(self, mineru: MineruService = get_mineru_service()):
        super().__init__()
        self._mineru = mineru
    
    def _validate_input_state(self, state: ImportGraphState) -> tuple[Path, Path]:
        pdf_path = state.get("pdf_path")
        if not pdf_path:
            raise StateFieldError(field_name='pdf_path', expected_type=str)

        output_file_dir = state.get("output_file_dir")
        if not output_file_dir:
            raise StateFieldError(field_name='output_file_dir', expected_type=str)

        pdf_path_obj = Path(pdf_path)
        output_dir_obj = Path(output_file_dir)

        if not pdf_path_obj.exists():
            raise FileProcessingError(message=f"PDF file {pdf_path_obj.name} does not exist")

        if not output_dir_obj.exists():
            self.logger.info(f"Output directory does not exist. Creating: {output_dir_obj.absolute()}")
            output_dir_obj.mkdir(parents=True, exist_ok=True)

        return pdf_path_obj, output_dir_obj

    def _upload_and_poll(self, pdf_path_obj: Path) -> str:

        signed_url, batch_id = self._mineru.get_upload_url(pdf_path_obj)

        self._mineru.upload_doc(pdf_path_obj, signed_url)

        return self._mineru.poll_task_status(batch_id)


    def _download_and_extract(self, zip_url: str, output_dir_obj: Path, pdf_stem: str) -> str:
        
        zip_file_path = self._mineru.download_zip(zip_url, output_dir_obj, pdf_stem)

        return self._mineru.extract_processed_doc(zip_file_path, output_dir_obj, pdf_stem)


    def process(self, state: ImportGraphState) -> ImportGraphState:

        pdf_path_obj, output_dir_obj = self._validate_input_state(state)

        zip_url = self._upload_and_poll(pdf_path_obj)

        md_path = self._download_and_extract(zip_url, output_dir_obj, pdf_path_obj.stem)

        with open(md_path, "r", encoding="utf-8") as f:
            md_content = f.read()

        return {
            "md_path": md_path,
            "md_content": md_content
        }

    
if __name__ == "__main__":
    from dotenv import load_dotenv
    load_dotenv()
    from app.utils.logger import setup_logging
    logger = setup_logging("DEBUG")
    init_state = {
        "pdf_path": "./test_data/kb/B3-211H.pdf",
        "output_file_dir": "./test_data/output"
    }
    node_pdf_to_md = NodePDFToMD()
    result = node_pdf_to_md(init_state)
    logger.info(json.dumps(result, ensure_ascii=False, indent=4))

"""
(knowledge-base) PS D:\knowledge-base> python -m app.processor.import_processor.nodes.node_pdf_to_md                                          
config loaded True...      
ImportConfig instance not found...
creating ImportConfig instance...
2026-07-13 20:03:59 - import.node_pdf_to_md - INFO - --- node_pdf_to_md 开始 ---
2026-07-13 20:03:59 - import.node_pdf_to_md - INFO - 开始[获取上传链接]请求，url：https://mineru.net/api/v4/file-urls/batch，参数：{'files': [{'name': 'hak180.pdf'}], 'model_version': 'vlm'}
2026-07-13 20:03:59 - import.node_pdf_to_md - INFO - [获取上传链接]响应结果：{'code': 0, 'msg': 'ok', 'trace_id': '4c7c3b69e810e2e9fc1ccbcea3f19907', 'data': {'batch_id': '951b5188-36c3-405c-84fa-2201e078f374', 'file_urls': ['https://mineru.oss-cn-shanghai.aliyuncs.com/api-upload/extract/2026-07-13/951b5188-36c3-405c-84fa-2201e078f374/4dd5a4bd-cecb-4011-872e-90d26a5b9d01.pdf?Expires=1784030639&OSSAccessKeyId=LTAI5t8fSGMgiRhQn4mpp926&Signature=N6U283OHfjstDnkua43k1oKXsmo%3D']}}
2026-07-13 20:03:59 - import.node_pdf_to_md - INFO - [获取上传链接]成功！batch_id：951b5188-36c3-405c-84fa-2201e078f374，signed_url：https://mineru.oss-cn-shanghai.aliyuncs.com/api-upload/extract/2026-07-13/951b5188-36c3-405c-84fa-2201e078f374/4dd5a4bd-cecb-4011-872e-90d26a5b9d01.pdf?Expires=1784030639&OSSAccessKeyId=LTAI5t8fSGMgiRhQn4mpp926&Signature=N6U283OHfjstDnkua43k1oKXsmo%3D
2026-07-13 20:03:59 - import.node_pdf_to_md - INFO - 开始[文件上传]请求，signed_url：https://mineru.oss-cn-shanghai.aliyuncs.com/api-upload/extract/2026-07-13/951b5188-36c3-405c-84fa-2201e078f374/4dd5a4bd-cecb-4011-872e-90d26a5b9d01.pdf?Expires=1784030639&OSSAccessKeyId=LTAI5t8fSGMgiRhQn4mpp926&Signature=N6U283OHfjstDnkua43k1oKXsmo%3D
2026-07-13 20:04:00 - import.node_pdf_to_md - INFO - [文件上传]成功！
2026-07-13 20:04:00 - import.node_pdf_to_md - INFO - 【任务轮询】最大超时：600s，batch_id：951b5188-36c3-405c-84fa-2201e078f374
2026-07-13 20:04:00 - import.node_pdf_to_md - INFO - 开始[任务轮询]，url：https://mineru.net/api/v4/extract-results/batch/951b5188-36c3-405c-84fa-2201e078f374
2026-07-13 20:04:00 - import.node_pdf_to_md - INFO - 【任务轮询】轮询结果：{'code': 0, 'msg': 'ok', 'trace_id': '6b163975398a61ee0062e2e3222dff3e', 'data': {'batch_id': '951b5188-36c3-405c-84fa-2201e078f374', 'extract_result': [{'file_name': 'hak180.pdf', 'state': 'done', 'err_msg': '', 'full_zip_url': 'https://cdn-mineru.openxlab.org.cn/pdf/2026-06-22/c2b3ff46-c6a0-49bf-babd-3b107d5bcb6b.zip'}]}}
2026-07-13 20:04:00 - import.node_pdf_to_md - INFO - 【任务轮询】解析任务完成！总耗时0s，batch_id：951b5188-36c3-405c-84fa-2201e078f374
2026-07-13 20:04:00 - import.node_pdf_to_md - INFO - 【任务轮询】返回ZIP包下载链接：https://cdn-mineru.openxlab.org.cn/pdf/2026-06-22/c2b3ff46-c6a0-49bf-babd-3b107d5bcb6b.zip，batch_id：951b5188-36c3-405c-84fa-2201e078f374
2026-07-13 20:04:00 - import.node_pdf_to_md - INFO - 【ZIP下载】开始下载ZIP包：https://cdn-mineru.openxlab.org.cn/pdf/2026-06-22/c2b3ff46-c6a0-49bf-babd-3b107d5bcb6b.zip ...
2026-07-13 20:04:01 - import.node_pdf_to_md - INFO - 【ZIP下载】ZIP包下载成功：保存路径：test_data\output\hak180_result.zip
2026-07-13 20:04:01 - import.node_pdf_to_md - INFO - 【ZIP解压】已清空旧的解压目录：test_data\output\hak180
2026-07-13 20:04:01 - import.node_pdf_to_md - INFO - 【ZIP解压】开始解压ZIP包：test_data\output ...
2026-07-13 20:04:01 - import.node_pdf_to_md - INFO - 【ZIP解压】ZIP解压完成，解压目录：test_data\output\hak180
2026-07-13 20:04:01 - import.node_pdf_to_md - INFO - 【MD重命名】开始将full.md文件重命名为hak180.md
2026-07-13 20:04:01 - import.node_pdf_to_md - INFO - 【MD重命名】重命名成功，文件名：hak180.md
2026-07-13 20:04:01 - import.node_pdf_to_md - INFO - --- node_pdf_to_md 完成 ---
2026-07-13 20:04:01 - root - INFO - {
    "md_path": "D:\\knowledge-base\\test_data\\output\\hak180\\hak180.md",
    "md_content": "![](images/677a08ee041965bbbdb6b483d6c17d5aaa36a26b6dc96870a2019f0307b8616f.jpg)  \nD01WD7001-00\n\nSCHN\n\n## HAK 180 烫金机...）"
}
"""