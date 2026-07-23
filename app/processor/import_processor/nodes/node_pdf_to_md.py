from pathlib import Path

from app.processor.import_processor.base import BaseNode
from app.processor.import_processor.exceptions import StateFieldError, FileProcessingError
from app.processor.import_processor.state import ImportGraphState
from app.services.mineru_service import MineruService, get_mineru_service

class NodePDFToMD(BaseNode):
    
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

        if not pdf_path_obj.exists():
            raise FileProcessingError(message=f"PDF file {pdf_path_obj.name} does not exist")

        return pdf_path, output_file_dir

    def _upload_and_poll(self, pdf_path: str) -> str:

        upload_url, batch_id = self._mineru.get_upload_url(Path(pdf_path).name)

        self._mineru.upload_file(pdf_path, upload_url)

        return self._mineru.poll_task_status(batch_id)


    def _download_and_extract(self, zip_url: str, output_dir: str, pdf_path: str) -> str:

        pdf_stem = Path(pdf_path).stem
        
        zip_file_path = self._mineru.download_zip(zip_url, output_dir, pdf_stem)

        return self._mineru.extract_processed_doc(zip_file_path, output_dir, pdf_stem)


    def process(self, state: ImportGraphState) -> ImportGraphState:

        pdf_path, output_dir = self._validate_input_state(state)

        zip_url = self._upload_and_poll(pdf_path)

        md_path = self._download_and_extract(zip_url, output_dir, pdf_path)

        with open(md_path, "r", encoding="utf-8") as f:
            md_content = f.read()

        return {
            "md_path": md_path,
            "md_content": md_content
        }