from typing import Any, Dict, List

from fastapi import WebSocket

from src.core.utils.logger import get_logger

logger = get_logger(__name__)


class WSManager:
    def __init__(self):
        self._connections: Dict[str, List[WebSocket]] = {}

    async def connect(self, user_id: str, websocket: WebSocket):
        await websocket.accept()
        logger.info(f"User id {user_id} connection to websocket.")
        user_id = str(user_id)
        if user_id not in self._connections:
            self._connections[user_id] = []

        self._connections[user_id].append(websocket)

    def disconnect(self, user_id: str, websocket: WebSocket):
        user_id = str(user_id)
        if user_id not in self._connections:
            logger.warning(
                f"User with id {user_id} not found in the websocket connections"
            )
            return
        self._connections[user_id].remove(websocket)
        logger.info(f"User with id {user_id} diconnect from websocket")
        if not self._connections[user_id]:
            del self._connections[user_id]
            logger.info(f"User with id {user_id} has been deleted from connections")

    async def send_to_user(self, user_id: str, message: Dict[str, Any]):
        user_id = str(user_id)
        if user_id in self._connections:
            logger.info(
                f"Sending message to user with id {user_id}: the message is {message}"
            )
            for ws in self._connections[user_id]:
                await ws.send_json(message)

    async def broadcast(self, message: str):
        # kalau memang ada event global untuk semua user
        for user_id, websockets in self._connections.items():
            for ws in websockets:
                await ws.send_text(message)


ws_manager = WSManager()
