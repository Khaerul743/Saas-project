from pydantic import BaseModel

from src.app.validators.base import BasePaginateOut, BaseSchemaOut


class TelegramSendMessage(BaseModel):
    agent_id: str
    username: str
    chat_id: str | int
    text: str
