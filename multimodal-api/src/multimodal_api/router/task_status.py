from fastapi import APIRouter
from fastapi import Request

from loguru import logger

from multimodal_api.config.config import get_settings
from multimodal_api.models import TaskStatus

settings = get_settings()

logger = logger.bind(name="TaskStatusAPI")

router_task_status = APIRouter()


@router_task_status.get("/task-status/{task_id}")
async def get_task_status(task_id: str, fastapi_request: Request):
    status = fastapi_request.app.state.bg_task_states.get(task_id, TaskStatus.NOT_FOUND)
    return {"task_id": task_id, "status": status}
