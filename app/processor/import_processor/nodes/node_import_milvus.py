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

        file_title = state.get("file_title")
        if not file_title:
            raise StateFieldError(field_name="file_title", message="Missing field: file_title")
        
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
        return file_title, chunks, vector_dimension
    

    def process(self, state: ImportGraphState) -> ImportGraphState:
        
        file_title, chunks_json_data, vector_dimension = self._validate_input_state(state)

        vector_db = self._chunks_vector_db
        vector_db.create_chunks_collection(vector_dimension)

        vector_db.delete_from_chunks_collection(file_title)

        data_to_insert = [
            {**chunk, "part": chunk.get("part", 0)}
            for chunk in chunks_json_data
        ]
        insert_result = vector_db.insert_into_chunks_collection(data_to_insert)

        # backfill chunks data with generated ids
        updated_chunks = [
            {"chunk_id": id, **chunks_json_data[i]}
            for i, id in enumerate(insert_result.get('ids', []))
        ]
        self.backup_json(state, updated_chunks, "chunks_with_id.json")

        return {
            "chunks": updated_chunks
        }