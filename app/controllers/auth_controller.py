# auth_controller.py
from fastapi import HTTPException, Response, status
from sqlalchemy.orm import Session

from app.models.auth_model import AuthIn
from app.models.user_entity import User
from app.utils.hash import verify_password
from app.utils.logger import get_logger
from app.utils.security import create_access_token

logger = get_logger(__name__)


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
        return user

    except Exception as e:
        logger.exception(f"Unexpected error while creating access token: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Internal server error, please try again later",
        )
