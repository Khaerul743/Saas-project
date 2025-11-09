import os

from app.middlewares.auth_dependencies import role_required
from fastapi import (
    APIRouter,
    BackgroundTasks,
    Depends,
    File,
    Form,
    Request,
    UploadFile,
    status,
)
from sqlalchemy.orm import Session

from app.controllers.base import history_controllers as hc
from core.utils.response import success_response
from src.config.database import get_db
from src.config.limiter import limiter

router = APIRouter(prefix="/api/history", tags=["history"])


@router.get("/messages/{user_agent_id}")
def getAllMessageByThreadId(
    user_agent_id: str,
    current_user: dict = Depends(role_required(["admin", "user"])),
    db: Session = Depends(get_db),
):
    try:
        get_history_messages = hc.get_all_messages_by_threadId(
            user_agent_id, current_user, db
        )
        return success_response(
            "Get all history messages is successfully", get_history_messages
        )
    except:
        raise
