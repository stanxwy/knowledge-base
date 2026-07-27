import logging
import os
import shutil
import uuid
from datetime import datetime
from typing import Any

from fastapi import (
    APIRouter,
    BackgroundTasks,
    Depends,
    File,
    HTTPException,
    UploadFile,
)

from app.api.v1.deps import ObjectStore, get_object_store
from app.utils.task_utils import (
    TASK_STATUS_COMPLETED,
    TASK_STATUS_FAILED,
    TASK_STATUS_PROCESSING,
    add_done_task,
    add_running_task,
    clear_task,
    get_done_task_list,
    get_running_task_list,
    get_task_status,
    update_task_status,
)
from app.workflows.ingestion.main_graph import KBImportWorkflow

logger = logging.getLogger(__name__)

router = APIRouter(tags=["ingest"])


def run_graph_task(task_id: str, output_file_dir: str, import_file_path: str):
    try:
        update_task_status(task_id, TASK_STATUS_PROCESSING)

        init_state = {
            "task_id": task_id,
            "import_file_path": import_file_path,
            "output_file_dir": output_file_dir,
        }

        workflow = KBImportWorkflow()
        for event in workflow.run(init_state, stream=True):
            for node_name, node_result in event.items():
                logger.info(f"[{task_id}] {node_name}\n{node_result}")
                add_done_task(task_id, node_name)

        update_task_status(task_id, TASK_STATUS_COMPLETED)

    except Exception as e:
        logger.exception(f"[{task_id}] error running ImportWorkflow: {e!s}", stack_info=True)
        update_task_status(task_id, TASK_STATUS_FAILED)


@router.post("/upload", summary="file upload API", description="multiple files upload supported, triggers import workflow")
async def upload_files(background_tasks: BackgroundTasks, files: list[UploadFile] = File(...), object_store: ObjectStore = Depends(get_object_store)):
    try:
        data_based_root_dir = os.getenv("DATA_BASED_ROOT_DIR")
        date_str = datetime.now().strftime("%Y%m%d")
        date_dir = os.path.join(data_based_root_dir, date_str)
        task_ids = []
    
        for file in files:
            task_id = str(uuid.uuid4())
            clear_task(task_id)
            task_ids.append(task_id)
            add_running_task(task_id, "upload_file")
            logger.info(f"[{task_id}] start processing upload file: {file.filename}, file type: {file.content_type}")
    
            task_dir = os.path.join(date_dir, task_id)
            os.makedirs(task_dir, exist_ok=True)
            import_file_path = os.path.join(task_dir, file.filename)
    
            with open(import_file_path, "wb") as file_buffer:
                shutil.copyfileobj(file.file, file_buffer)
            logger.info(f"[{task_id}] file saved to local, path: {import_file_path}")
    
            object_name = f"doc/{date_str}/{file.filename}"
            try:
                url = object_store.upload(import_file_path, object_name, file.content_type)
                
                logger.info(f"[{task_id}] file uploaded, url: {url}")
            except Exception as e:
                logger.warning(f"[{task_id}] error uploading file: {e!s}", stack_info=True)
    
            add_done_task(task_id, "upload_file")
    
            background_tasks.add_task(run_graph_task, task_id, task_dir, import_file_path)
            logger.info(f"[{task_id}] Import Workflow task submitted to background executor")
    
        logger.info(f"File upload complete, total: {len(files)} files, tasks: {task_ids}")
        return {
            "code": 200,
            "message": f"{len(files)} files uploaded successfully",
            "task_ids": task_ids
        }
    except Exception as e:
        logger.exception(f"Error uploading files: {e!s}", stack_info=True)
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/status/{task_id}", summary="query task status", description="query task status with steps running/done by task_id")
async def get_task_progress(task_id: str):
    task_status_info: dict[str, Any] = {
        "code": 200,
        "task_id": task_id,
        "status": get_task_status(task_id),             # pending/processing/completed/failed
        "done_list": get_done_task_list(task_id),  
        "running_list": get_running_task_list(task_id)
    }
    logger.info(
        f"[{task_id}] task status {task_status_info['status']}, steps done: {task_status_info['done_list']}")
    return task_status_info