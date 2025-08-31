# auth_controller.py
from fastapi import HTTPException, Response, status
from sqlalchemy.orm import Session

from app.models.auth.auth_model import AuthIn
from app.models.user_entity import User
from app.utils.hash import hash_password, verify_password
from app.utils.logger import get_logger
from app.utils.security import create_access_token

logger = get_logger(__name__)


def registerHandler(db, payload):
    """
    Register and create new user.
    """
    user = db.query(User).filter(User.email == payload.email).first()
    if user:
        logger.warning(f"Email is already in use: {user.email}")
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST, detail="Email is already in use."
        )

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


def loginHandler(response: Response, db: Session, payload: AuthIn) -> User:
    """
    Login user: cek kredensial, buat JWT, simpan di cookie.
    """
    user = db.query(User).filter(User.email == payload.email).first()
    if not user or not verify_password(payload.password, user.password):
        user_email = payload.email
        logger.warning(f"Invalid login attempt for email: {user_email}")
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED, detail="Invalid credentials"
        )

    try:
        access_token = create_access_token(
            {"id": user.id, "email": user.email, "role": user.role}
        )
        response.set_cookie(
            key="access_token",
            value=access_token,
            httponly=True,
            secure=False,  # True jika production HTTPS
            samesite="lax",
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
            "access_token", httponly=True, secure=False, samesite="lax"
        )

        logger.info(f"User {current_user.get('email')} logout successfully")
        return current_user
    except Exception as e:
        logger.error(f"Unexpected error while user logout: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Internal server error, please try again later.",
        )
