import logging
import os
from datetime import datetime

from fastapi import (
    APIRouter,
    BackgroundTasks,
    Depends,
    File,
    HTTPException,
    UploadFile,
)

from app.api.v1.deps import get_ingestion_service
from app.schema.ingestion_schema import IngestionResponse
from app.services.ingestion_service import IngestionService

logger = logging.getLogger(__name__)

router = APIRouter(tags=["ingest"])

@router.post("/upload", summary="file upload API", description="multiple files upload supported, triggers import workflow")
async def upload_files(background_tasks: BackgroundTasks, files: list[UploadFile] = File(...), service: IngestionService = Depends(get_ingestion_service)):
    try:
        data_based_root_dir = os.getenv("DATA_BASED_ROOT_DIR")
        date_str = datetime.now().strftime("%Y%m%d")
        date_dir = os.path.join(data_based_root_dir, date_str)
        task_ids = []
    
        for file in files:
            task_id, task_dir, import_file_path = service.upload_doc(date_str, date_dir, file)
            task_ids.append(task_id)

            background_tasks.add_task(service.run_graph_task, task_id, task_dir, import_file_path)
            logger.info(f"[{task_id}] Import Workflow task submitted to background executor")
    
        logger.info(f"File upload complete, total: {len(files)} files, tasks: {task_ids}")
        return IngestionResponse(code=200, message=f"{len(files)} files uploaded successfully", task_ids=task_ids)
    except Exception as e:
        logger.exception(f"Error uploading files: {e!s}", stack_info=True)
        raise HTTPException(status_code=500, detail=str(e))




@router.get("/ingest/tasks/{task_id}", summary="Get RAG ingestion task status")
async def get_ingest_task_status(
    task_id: str,
):
    """Query the status of a background ingestion task."""
    try:
        from app.utils.task_utils import (
            TASK_STATUS_COMPLETED,
            TASK_STATUS_FAILED,
            TASK_STATUS_PENDING,
            TASK_STATUS_PROCESSING,
            get_task_status,
        )

        status = get_task_status(task_id)

        # Map internal status to API response
        status_map = {
            TASK_STATUS_PENDING: "pending",
            TASK_STATUS_PROCESSING: "processing",
            TASK_STATUS_COMPLETED: "completed",
            TASK_STATUS_FAILED: "failed",
        }

        return {
            "task_id": task_id,
            "status": status_map.get(status, status),
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
