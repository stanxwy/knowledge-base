from typing import Dict, Any, List

from app.processor.import_processor.base import BaseNode
from app.processor.import_processor.exceptions import StateFieldError
from app.processor.import_processor.state import ImportGraphState
from app.services.vectordb_service import ChunksVectorDBService, get_chunks_vector_db

class NodeImportMilvus(BaseNode):

    name: str = "node_import_milvus"
    
    def __init__(self, chunks_vector_db: ChunksVectorDBService = get_chunks_vector_db()):
        super().__init__()
        self._chunks_vector_db = chunks_vector_db

    def _validate_input_state(self, state: ImportGraphState) -> tuple[List[Dict[str, Any]], int]:

        chunks = state.get("chunks")
        if not chunks:
            raise StateFieldError(field_name="chunks", message="Chunks cannot be empty", expected_type=list)

        if not isinstance(chunks, list):
            raise StateFieldError(field_name="chunks", message="Invalid data type for chunks", expected_type=list)

        first_chunk = chunks[0]
        if 'dense_vector' not in first_chunk:
            raise StateFieldError(field_name="chunks", message="Missing field: dense_vector")

        if 'sparse_vector' not in first_chunk:
            raise StateFieldError(field_name="chunks", message="Missing field: sparse_vector")

        vector_dimension = len(first_chunk['dense_vector'])
        return chunks, vector_dimension
    

    def _step_4_insert_data(self, chunks_json_data: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
        data_to_insert = []
        for chunk in chunks_json_data:
            chunk_copy = chunk.copy()
            if "part" not in chunk_copy:
                chunk_copy["part"] = 0
            data_to_insert.append(chunk_copy)

        insert_result = self._chunks_vector_db.insert_into_chunks_collection(data_to_insert)
     
        inserted_ids = insert_result.get('ids', [])
        if inserted_ids:
            for idx, chunk in enumerate(chunks_json_data):
                chunk['chunk_id'] = str(inserted_ids[idx])
        return chunks_json_data

    def process(self, state: ImportGraphState) -> ImportGraphState:

        chunks_json_data, vector_dimension = self._validate_input_state(state)

        self._chunks_vector_db.create_chunks_collection(vector_dimension)

        file_title = chunks_json_data[0].get("file_title")
        self._chunks_vector_db.delete_from_chunks_collection(file_title)

        updated_chunks = self._step_4_insert_data(chunks_json_data)
        self.backup_json(state, updated_chunks, "chunks_with_id.json")

        return {
            "chunks": updated_chunks
        }