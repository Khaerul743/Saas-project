from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import Session

from app.controllers import BaseController
from app.core.logger import get_logger
from app.models.user.user_entity import User
from app.models.user.user_model import (
    UpdateDetail,
    UpdateUserPlan,
    UserCreate,
    UserOut,
    UserUpdate,
)
from app.schema.user_schema import UserPaginate
from app.services.user_service import UserService

logger = get_logger(__name__)


class UserController(BaseController):
    def __init__(self, db: AsyncSession, request=None):
        super().__init__()
        self.user_service = UserService(db, request)

    async def get_all_users(self, page: int, limit: int) -> UserPaginate:
        try:
            data_users = await self.user_service.get_all_users(page, limit)
            return data_users
        except Exception as e:
            self.handle_unexpected_error(e)
            raise  # Re-raise exception


# def get_all_users(limit, page, db: Session, current_user: dict):
#     try:
#         offset = (page - 1) * limit
#         users = (
#             db.query(
#                 User.name.label("username"),
#                 User.email,
#                 User.role,
#                 User.job_role,
#                 User.company_name,
#                 User.plan,
#                 User.status,
#                 User.created_at,
#                 User.updated_at,
#                 User.last_login,
#             )
#             .offset(offset)
#             .limit(limit)
#             .all()
#         )

#         total_users = db.query(User).count()
#         logger.info(
#             f"Admin {current_user.get('email')} retrieved {len(users)} users (page {page})."
#         )

#         return (
#             {
#                 "page": page,
#                 "limit": limit,
#                 "total_users": total_users,
#                 "data": users,
#             },
#         )

#     except Exception as e:
#         logger.error(f"Error while retrieving users: {str(e)}")
#         raise HTTPException(
#             status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
#             detail="Internal server error, please try again later.",
#         )


# def get_user(db: Session, current_user: dict):
#     user = db.query(User).filter(User.email == current_user.get("email")).first()
#     if not user:
#         logger.warning(f"User not found: id {current_user.get('id')}")
#         raise HTTPException(
#             status_code=status.HTTP_404_NOT_FOUND, detail="User not found"
#         )

#     try:
#         logger.info(f"{current_user.get('email')} Get user profile is successfully")
#         return user
#     except Exception as e:
#         logger.warning(f"Unexpected error while getting user profile: {str(e)}")
#         raise HTTPException(
#             status_code=status.HTTP_200_OK,
#             detail="Internal server error, please try again later.",
#         )


# def create_user(db: Session, user: UserCreate) -> UserOut:
#     # Cek apakah email sudah terdaftar
#     existing_user = db.query(User).filter(User.email == user.email).first()
#     if existing_user:
#         logger.warning(f"Register attempt with existing email: {user.email}")
#         raise HTTPException(
#             status_code=status.HTTP_400_BAD_REQUEST,
#             detail="Email is already registered.",
#         )

#     # Hash password sebelum simpan
#     hashed_password = hash_password(user.password)

#     db_user = User(
#         name=user.name,
#         email=user.email,
#         password=hashed_password,
#         plan=user.plan,
#         company_name=user.company_name,
#         job_role=user.job_role,
#     )

#     try:
#         db.add(db_user)
#         db.commit()
#         db.refresh(db_user)  # ambil data terbaru dengan ID
#         logger.info(f"New user created: {db_user.email}")
#         return db_user
#     except IntegrityError as e:
#         db.rollback()
#         logger.error(f"IntegrityError while creating user: {str(e)}")
#         raise HTTPException(
#             status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
#             detail="Internal server error. Please try again later.",
#         )
#     except Exception as e:
#         db.rollback()
#         logger.exception(
#             f"Unexpected error while creating user: {str(e)}"
#         )  # log lengkap + stacktrace
#         raise HTTPException(
#             status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
#             detail="Internal server error. Please try again later.",
#         )


# def updateDetailHandler(db: Session, payload: UpdateDetail, user: dict):
#     get_user = db.query(User).filter(User.id == user.get("id")).first()
#     if not get_user:
#         logger.warning(f"User not found: {user.get('email')}")
#         raise HTTPException(
#             status_code=status.HTTP_404_NOT_FOUND, detail="User not found"
#         )
#     try:
#         get_user.company_name = payload.company_name
#         get_user.job_role = payload.job_role

#         db.commit()
#         db.refresh(get_user)
#         logger.info(f"{get_user.email} update detail information is successfully")
#         return get_user
#     except IntegrityError as e:
#         db.rollback()
#         logger.error(f"IntegrityError while update information user: {str(e)}")
#         raise HTTPException(
#             status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
#             detail="Internal server error. Please try again later.",
#         )
#     except Exception as e:
#         db.rollback()
#         logger.error(f"Unexpected error while update detail information {str(e)}")
#         raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR)


# def updateUserHandler(db: Session, payload: UserUpdate, user: dict):
#     get_user = db.query(User).filter(User.email == user.get("email")).first()
#     if not get_user:
#         logger.warning(f"User not found: {user.get('email')}")
#         raise HTTPException(
#             status_code=status.HTTP_400_BAD_REQUEST, detail="User not found"
#         )

#     try:
#         get_user.name = payload.username
#         get_user.company_name = payload.company_name
#         get_user.job_role = payload.job_role

#         db.commit()
#         db.refresh(get_user)
#         logger.info(f"{get_user.email} update profile is successfully")
#         return get_user
#     except IntegrityError as e:
#         db.rollback()
#         logger.error(f"IntegrityError while updating user: {str(e)}")
#         raise HTTPException(
#             status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
#             detail="Internal server error. Please try again later.",
#         )
#     except Exception as e:
#         db.rollback()
#         logger.error(f"Unexpected error while updating user: {str(e)}")
#         raise HTTPException(
#             status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
#             detail="Internal server error, please try again later.",
#         )


# def update_user_plan(
#     user_id: int, payload: UpdateUserPlan, current_user: dict, db: Session
# ):
#     user = db.query(User).filter(User.id == user_id).first()
#     if not user:
#         logger.warning(f"Update user plan failed. User not found. ID: {user_id}")
#         raise HTTPException(
#             status_code=status.HTTP_404_NOT_FOUND, detail="User not found"
#         )

#     try:
#         user.plan = payload.plan
#         db.commit()
#         db.refresh(user)
#         logger.info(
#             f"Update user plan is successfully. user email {user.email}, plan {user.plan}"
#         )
#         return user
#     except IntegrityError as e:
#         db.rollback()
#         logger.error(f"IntegrityError while updating user plan: {str(e)}")
#         raise HTTPException(
#             status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
#             detail="Internal server error. Please try again later.",
#         )
#     except Exception as e:
#         db.rollback()
#         logger.error(f"Unexpected error while updating user plan: {str(e)}")
#         raise HTTPException(
#             status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
#             detail="Internal server error, please try again later.",
#         )


# def delete_user_handler(user_id: int, current_user: dict, db: Session):
#     user = db.query(User).filter(User.id == user_id).first()
#     if not user:
#         logger.warning(f"Delete failed. User not found. ID: {user_id}")
#         raise HTTPException(
#             status_code=status.HTTP_404_NOT_FOUND, detail="User not found."
#         )

#     try:
#         user_email = user.email
#         db.delete(user)
#         db.commit()

#         logger.info(f"User deleted successfully. ID: {user_id}, Email: {user_email}")
#         return {"message": f"User deleted successfully: {user_email}"}

#     except IntegrityError as e:
#         db.rollback()
#         logger.error(f"IntegrityError while deleting user {user_id}: {str(e)}")
#         raise HTTPException(
#             status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
#             detail="User could not be deleted due to related records.",
#         )

#     except Exception as e:
#         db.rollback()
#         logger.error(f"Unexpected error while deleting user {user_id}: {str(e)}")
#         raise HTTPException(
#             status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
#             detail="An unexpected error occurred. Please try again later.",
#         )
