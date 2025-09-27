"""
WebSocket module for real-time communication
"""
from app.websocket.connection_manager import manager
from app.websocket.websocket_handler import websocket_handler

__all__ = ["manager", "websocket_handler"]


