from pathlib import Path

from app.processor.import_processor.base import BaseNode
from app.processor.import_processor.exceptions import ValidationError, StateFieldError, FileProcessingError
from app.processor.import_processor.state import ImportGraphState

class NodeEntry(BaseNode):

    name: str = "node_entry"

    def _validate_input_state(self, state):

        update_state: ImportGraphState = {}
        import_file_path = state.get("import_file_path")
        # import_file_path = state["import_file_path"] # throw error if key does not exist

        if not import_file_path:
            raise StateFieldError(field_name='import_file_path', expected_type=str)

        import_file_path_obj = Path(import_file_path)
        if not import_file_path_obj.exists():
            raise FileProcessingError(message=f"File {import_file_path_obj.name} does not exist")

        if import_file_path_obj.suffix == ".pdf":
            update_state["is_pdf_read_enabled"] = True
            update_state["pdf_path"] = import_file_path
        elif import_file_path_obj.suffix == ".md":
            update_state["is_md_read_enabled"] = True
            update_state["md_path"] = import_file_path
        else:
            raise ValidationError(message=f"File extension {import_file_path_obj.suffix} not supported")

        update_state["file_title"] = import_file_path_obj.stem
        return update_state

    def process(self, state: ImportGraphState) -> ImportGraphState:
        return self._validate_input_state(state)