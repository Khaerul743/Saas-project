from fastapi import APIRouter, Depends, Request, status
from sqlalchemy.ext.asyncio import AsyncSession

from src.app.controllers.webhook_controller import WebhookController
from src.config.database import get_db
from src.config.limiter import limiter
from src.core.utils.response import success_response

router = APIRouter(prefix="/api", tags=["integrations"])


@router.post("/webhook/telegram/{agent_id}", status_code=status.HTTP_200_OK)
async def telegram_webhook(
    agent_id: str, request: Request, db: AsyncSession = Depends(get_db)
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
            "agent_id": agent_id,
            "username": username,
            "chat_id": chat_id,
            "text": text,
        }
        controller = WebhookController(db, request)
        await controller.invoke_telegram_agent(data)
        return success_response("Successfully sent the message")
    except Exception as e:
        # Log the error if you have a logger
        raise
