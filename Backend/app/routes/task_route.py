from fastapi import APIRouter, Depends, HTTPException, status
from app.tasks import celery_app
from app.middlewares.RBAC import role_required
from app.utils.logger import get_logger

logger = get_logger(__name__)
router = APIRouter(prefix="/api/tasks", tags=["tasks"])

@router.get("/status/{task_id}")
def get_task_status(
    task_id: str,
    current_user: dict = Depends(role_required(["admin", "user"])),
):
    """Get the status of a Celery task"""
    logger.info(f"Getting task status for task_id: {task_id}")
    try:
        task_result = celery_app.AsyncResult(task_id)
        
        if task_result.state == "PENDING":
            response = {
                "task_id": task_id,
                "state": task_result.state,
                "current": 0,
                "total": 100,
                "status": "Task is waiting to be processed..."
            }
        elif task_result.state == "PROGRESS":
            response = {
                "task_id": task_id,
                "state": task_result.state,
                "current": task_result.info.get("current", 0),
                "total": task_result.info.get("total", 100),
                "status": task_result.info.get("status", "")
            }
        elif task_result.state == "SUCCESS":
            response = {
                "task_id": task_id,
                "state": task_result.state,
                "result": task_result.result
            }
        else:  # FAILURE
            response = {
                "task_id": task_id,
                "state": task_result.state,
                "status": task_result.info.get("status", "")
            }
        
        return response

    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error getting task status: {str(e)}"
        )