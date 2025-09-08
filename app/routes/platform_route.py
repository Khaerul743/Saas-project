import os

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

from app.configs.database import get_db
from app.configs.limiter import limiter
from app.controllers import platform_controller as pc
from app.middlewares.RBAC import role_required
from app.utils.response import success_response

router = APIRouter(prefix="/api", tags=["integrations"])


@router.post("/telegram/webhook/{telegram_id}", status_code=200)
async def telegram_webhook(
    telegram_id: int, request: Request, db: Session = Depends(get_db)
):
    try:
        payload = await request.json()
        message = payload.get("message", {})
        chat = message.get("chat", {})
        user = message.get("from", {})

        chat_id = chat.get("id")
        text = message.get("text")
        username = user.get("first_name")

        if not all([chat_id, text, username]):
            return success_response(
                "Invalid payload", status_code=status.HTTP_400_BAD_REQUEST
            )

        data = {
            "telegram_id": telegram_id,
            "username": username,
            "chat_id": chat_id,
            "text": text,
        }

        await pc.telegram_handler(data, db)
        return success_response("Successfully sent the message")
    except Exception as e:
        # Log the error if you have a logger
        raise
