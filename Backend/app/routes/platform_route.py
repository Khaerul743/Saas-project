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
    HTTPException,
)
from sqlalchemy.orm import Session

from src.config.database import get_db
from src.config.limiter import limiter
from app.controllers import platform_controller as pc
from app.middlewares.auth_dependencies import role_required
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
            return success_response("Invalid payload")

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


@router.post("/agent/webhook/{agent_id}", status_code=200)
async def agent_webhook(
    agent_id: str, api_key: str, request: Request, db: Session = Depends(get_db)
):
    try:
        payload = await request.json()
        username = payload.get("username")
        unique_id = payload.get("unique_id")
        user_message = payload.get("user_message")

        if not all([username, unique_id, user_message]):
            return HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST, detail="Invalid payload"
            )

        data = {
            "username": username,
            "unique_id": unique_id,
            "user_message": user_message,
        }
        response = await pc.api_handler(api_key, agent_id, data, db)
        return success_response("Successfully sent the message", response)

    except Exception as e:
        raise
