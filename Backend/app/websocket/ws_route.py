import json
from typing import Optional

from fastapi import APIRouter, Query, WebSocket, WebSocketDisconnect

from app.utils.logger import get_logger
from app.websocket.manager import ws_manager

logger = get_logger(__name__)
router = APIRouter(prefix="/ws", tags=["websocket"])


@router.websocket("/agent-progress/{user_id}")
async def agent_progress(user_id: str, websocket: WebSocket):
    try:
        await ws_manager.connect(user_id, websocket)
        logger.info(f"WebSocket connected for agent progress - User: {user_id}")
        while True:
            try:
                data = await websocket.receive_text()
                message = json.loads(data)
                print(f"Message from user id {user_id}, data {message}")
            except WebSocketDisconnect:
                break
    except WebSocketDisconnect:
        logger.info(f"WebSocket disconnected for user {user_id}")
    except Exception as e:
        logger.error(f"WebSocket error for user {user_id}: {e}")
    finally:
        ws_manager.disconnect(user_id, websocket)
