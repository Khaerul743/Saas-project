# auth_controller.py
from fastapi import HTTPException, Response, status
from sqlalchemy.orm import Session

from app.models.auth.auth_model import AuthIn
from app.models.user.user_entity import User
from app.utils.hash import hash_password, verify_password
from app.utils.logger import get_logger
from app.utils.security import create_access_token
from app.utils.auth_utils import (
    email_exists_handler,
    email_not_found_handler,
    invalid_credentials_handler,
)
from app.events.redis_event import EventType, event_bus, Event
from datetime import datetime
logger = get_logger(__name__)


def registerHandler(db, payload):
    """
    Register and create new user.
    """
    user = db.query(User).filter(User.email == payload.email).first()
    if user:
        email_exists_handler(logger, payload.email)

    hashed_password = hash_password(payload.password)
    db_user = User(
        name=payload.username,
        email=payload.email,
        password=hashed_password,
    )
    try:
        db.add(db_user)
        db.commit()
        db.refresh(db_user)
        logger.info(f"New user registered with email: {payload.email}")
        return db_user
    except Exception as e:
        logger.error(f"Unexpected error while registering user {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Internal server error, Please try again later.",
        )


async def loginHandler(response: Response, db: Session, payload: AuthIn) -> User:
    """
    Login user: cek kredensial, buat JWT, simpan di cookie.
    """
    user = db.query(User).filter(User.email == payload.email).first()
    
    #Test event
    await event_bus.publish(Event(
        event_type=EventType.DOCUMENT_UPLOADED,
        timestamp=datetime.now(),
        data={"user_id": "2", "agent_id": "2"},
        user_id=2,
        agent_id=1,
    ))
    # Check if email exists
    if not user:
        email_not_found_handler(logger, payload.email)
    
    # Check if password is correct
    if not verify_password(payload.password, user.password):
        invalid_credentials_handler(logger, payload.email)

    try:
        access_token = create_access_token(
            {"id": user.id, "email": user.email, "role": user.role}
        )
        response.set_cookie(
            key="access_token",
            value=access_token,
            httponly=True,
            secure=False,  # True for HTTPS (ngrok)
            samesite="lax",  # Allow cross-site cookies for ngrok
            max_age=3600,  # 1 jam sesuai token expire
        )
        logger.info(f"User {payload.email} login is successfully.")
        return user

    except Exception as e:
        logger.exception(f"Unexpected error while creating access token: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Internal server error, please try again later",
        )


def logoutHandler(response: Response, current_user: dict):
    """
    Handler untuk proses logout user.
    Menghapus cookie access_token dan mengembalikan data user.
    """
    try:
        response.delete_cookie(
            "access_token", httponly=True, secure=True, samesite="none"
        )

        logger.info(f"User {current_user.get('email')} logout successfully")
        return current_user
    except Exception as e:
        logger.error(f"Unexpected error while user logout: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Internal server error, please try again later.",
        )
