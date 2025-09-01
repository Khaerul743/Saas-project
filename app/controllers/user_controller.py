from fastapi import HTTPException, status
from sqlalchemy.exc import IntegrityError
from sqlalchemy.orm import Session

from app.models.user.user_entity import User
from app.models.user.user_model import UpdateDetail, UserCreate, UserOut, UserUpdate
from app.utils.hash import hash_password
from app.utils.logger import get_logger

logger = get_logger(__name__)


def get_user(db: Session, current_user: dict):
    user = db.query(User).filter(User.email == current_user.get("email")).first()
    if not user:
        logger.warning(f"User not found: id {current_user.get('id')}")
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail="User not found"
        )

    try:
        logger.info(f"{current_user.get('email')} Get user profile is successfully")
        return user
    except Exception as e:
        logger.warning(f"Unexpected error while getting user profile: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_200_OK,
            detail="Internal server error, please try again later.",
        )


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
        job_role=user.job_role,
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


def updateDetailHandler(db: Session, payload: UpdateDetail, user: dict):
    get_user = db.query(User).filter(User.id == user.get("id")).first()
    if not get_user:
        logger.warning(f"User not found: {user.get('email')}")
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail="User not found"
        )
    try:
        get_user.company_name = payload.company_name
        get_user.job_role = payload.job_role

        db.commit()
        db.refresh(get_user)
        logger.info(f"{get_user.email} update detail information is successfully")
        return get_user
    except Exception as e:
        logger.error(f"Unexpected error while update detail information {str(e)}")
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR)


def updateUserHandler(db: Session, payload: UserUpdate, user: dict):
    get_user = db.query(User).filter(User.email == user.get("email")).first()
    if not get_user:
        logger.warning(f"User not found: {user.get('email')}")
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST, detail="User not found"
        )

    try:
        get_user.name = payload.username
        get_user.company_name = payload.company_name
        get_user.job_role = payload.job_role

        db.commit()
        db.refresh(get_user)
        logger.info(f"{get_user.email} update profile is successfully")
        return get_user
    except Exception as e:
        logger.error(f"Unexpected error while updating user: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Internal server error, please try again later.",
        )
