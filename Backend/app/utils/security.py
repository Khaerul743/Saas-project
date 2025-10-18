# app/utils/security.py
from datetime import datetime, timedelta
from typing import Any, Dict, Optional

import jwt

from app.configs.config import settings
from app.dependencies.logger import get_logger

logger = get_logger(__name__)


def create_access_token(data: dict, expires_delta: Optional[timedelta] = None):
    """
    Generate JWT token dengan payload dan expiry.
    """
    to_encode = data.copy()
    expire = datetime.utcnow() + (
        expires_delta or timedelta(minutes=settings.ACCESS_TOKEN_EXPIRE_MINUTES)
    )
    to_encode.update({"exp": expire})
    token = jwt.encode(to_encode, settings.SECRET_KEY, algorithm=settings.ALGORITHM)
    return token


def decode_access_token(token: str):
    """
    Decode dan verifikasi JWT token.
    """
    try:
        payload = jwt.decode(
            token, settings.SECRET_KEY, algorithms=[settings.ALGORITHM]
        )
        return payload
    except jwt.ExpiredSignatureError:
        logger.warning("Token expired")
        raise
    except jwt.PyJWTError as e:
        logger.warning(f"Invalid token: {str(e)}")
        raise


class JWTHandler:
    def __init__(self):
        self.logger = get_logger(__name__)

    def create_access_token(
        self, data: Dict[str, Any], expires_delta: Optional[timedelta] = None
    ):
        """
        Generate JWT token dengan payload dan expiry.
        """
        to_encode = data.copy()
        expire = datetime.utcnow() + (
            expires_delta or timedelta(minutes=settings.ACCESS_TOKEN_EXPIRE_MINUTES)
        )
        to_encode.update({"exp": expire})
        token = jwt.encode(to_encode, settings.SECRET_KEY, algorithm=settings.ALGORITHM)
        return token

    def decode_access_token(self, token: str):
        """
        Decode dan verifikasi JWT token.
        """
        try:
            payload = jwt.decode(
                token, settings.SECRET_KEY, algorithms=[settings.ALGORITHM]
            )
            return payload
        except jwt.ExpiredSignatureError:
            self.logger.warning("Token expired")
            raise
        except jwt.PyJWTError as e:
            self.logger.warning(f"Invalid token: {str(e)}")
            raise
