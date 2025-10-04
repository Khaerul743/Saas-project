import json
from typing import Optional

from fastapi import APIRouter, Query, WebSocket, WebSocketDisconnect

from app.utils.logger import get_logger
from app.websocket.manager import ws_manager
from app.configs.database import SessionLocal
from app.models.user_agent.user_agent_entity import UserAgent
from app.models.agent.agent_entity import Agent
from app.models.history_message.history_entity import HistoryMessage
from app.models.history_message.metadata_entity import Metadata
from app.utils.agent_utils import invoke_agent_logic


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


# app/websocket/ws_route.py

@router.websocket("/agent-invoke/{user_id}")
async def agent_invoke_websocket(user_id: str, websocket: WebSocket):
    """
    WebSocket endpoint untuk invoke agent dengan database operations
    """
    db = SessionLocal()  # Database session untuk WebSocket
    try:
        await ws_manager.connect(f"agent_invoke_{user_id}", websocket)
        logger.info(f"WebSocket connected for agent invoke - User: {user_id}")
        
        while True:
            try:
                # Terima message dari client
                data = await websocket.receive_text()
                message = json.loads(data)
                
                agent_id = message["agent_id"]
                user_message = message["message"]
                
                # Kirim progress update
                await websocket.send_text(json.dumps({
                    "type": "progress",
                    "message": "Starting agent processing...",
                    "agent_id": agent_id
                }))
                
                # Query database untuk validasi agent
                agent = db.query(Agent).filter(Agent.id == agent_id).first()
                if not agent:
                    await websocket.send_text(json.dumps({
                        "type": "error",
                        "message": "Agent not found"
                    }))
                    continue
                
                # Query/Insert UserAgent
                get_user_agent = db.query(UserAgent).filter(UserAgent.agent_id == agent_id).first()
                if not get_user_agent:
                    user_agent = UserAgent(
                        id=str(agent_id),
                        agent_id=agent_id,
                        username="WebSocket User",
                        user_platform="api",
                    )
                    db.add(user_agent)
                    db.flush()
                    user_agent_id = user_agent.id
                else:
                    user_agent_id = get_user_agent.id
                
                # Kirim progress update
                
                # Invoke agent (gunakan logic yang sudah ada)
                agent_response = await invoke_agent_logic(agent_id, user_message, db, websocket)
                
                # Simpan HistoryMessage ke database
                new_history_message = HistoryMessage(
                    user_agent_id=user_agent_id,
                    user_message=user_message,
                    response=agent_response.get("response", ""),
                )
                db.add(new_history_message)
                db.flush()
                history_message_id = new_history_message.id
                
                # Simpan Metadata ke database
                new_metadata = Metadata(
                    history_message_id=history_message_id,
                    total_tokens=agent_response.get("token_usage", 0),
                    response_time=agent_response.get("response_time", 0),
                    model=agent_response.get("model", "unknown"),
                )
                db.add(new_metadata)
                db.commit()  # Commit semua perubahan ke database
                
                # Kirim response ke client
                await websocket.send_text(json.dumps({
                    "type": "response",
                    "agent_id": agent_id,
                    "user_message": user_message,
                    "response": agent_response.get("response", ""),
                    "status": "completed"
                }))
                
            except Exception as e:
                db.rollback()  # Rollback jika ada error
                logger.error(f"Error in agent invoke: {e}")
                await websocket.send_text(json.dumps({
                    "type": "error",
                    "message": f"Agent invoke failed: {str(e)}"
                }))
                
    except WebSocketDisconnect:
        logger.info(f"WebSocket disconnected for agent invoke - User: {user_id}")
    except Exception as e:
        logger.error(f"WebSocket error for agent invoke - User: {user_id}: {e}")
    finally:
        db.close()  # Tutup database connection
        ws_manager.disconnect(f"agent_invoke_{user_id}", websocket)