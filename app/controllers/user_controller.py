from fastapi import HTTPException, status
from sqlalchemy.exc import IntegrityError
from sqlalchemy.orm import Session

from app.models.user_entity import User
from app.models.user_model import UserCreate, UserOut
from app.utils.hash import hash_password
from app.utils.logger import get_logger

logger = get_logger(__name__)


def create_user(db: Session, user: UserCreate) -> UserOut:
    # Cek apakah email sudah terdaftar
    existing_user = db.query(User).filter(User.email == user.email).first()
    if existing_user:
        logger.warning(f"Register attempt with existing email: {user.email}")
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Email is already registered.",
        )

    # Hash password sebelum simpan
    hashed_password = hash_password(user.password)

    db_user = User(
        name=user.name,
        email=user.email,
        password=hashed_password,
        plan=user.plan,
        company_name=user.company_name,
        role=user.role,
    )

    try:
        db.add(db_user)
        db.commit()
        db.refresh(db_user)  # ambil data terbaru dengan ID
        logger.info(f"New user created: {db_user.email}")
        return db_user
    except IntegrityError as e:
        db.rollback()
        logger.error(f"IntegrityError while creating user: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Internal server error. Please try again later.",
        )
    except Exception as e:
        db.rollback()
        logger.exception(
            f"Unexpected error while creating user: {str(e)}"
        )  # log lengkap + stacktrace
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Internal server error. Please try again later.",
        )
