from fastapi import APIRouter, Depends, Query, Request, status
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import Session

from app.configs.database import get_db
from app.configs.limiter import limiter
from app.controllers.user_controller import UserController
from app.core.context import CurrentContext
from app.core.factory import controller_factory
from app.middlewares.auth_middleware import role_based_access_control
from app.schema.user_schema import UserOutPaginate
from app.utils.response import success_response

get_user_controller = controller_factory(UserController)
router = APIRouter(prefix="/api/users", tags=["users"])


@router.get("", response_model=UserOutPaginate, status_code=status.HTTP_200_OK)
async def getAllUsers(
    request: Request,
    page: int = Query(1, ge=1),
    limit: int = Query(50, le=100),
    current_user: dict = Depends(
        role_based_access_control.role_required(["admin", "user"])
    ),
    db: AsyncSession = Depends(get_db),
):
    print(f"Route - Context: {CurrentContext.get_current_user()}")
    print(f"Route - Current user param: {current_user}")
    print(f"Route - Request state: {getattr(request.state, 'current_user', 'Not set')}")
    # Buat controller setelah auth dependency dijalankan
    controller = UserController(db, request)
    users = await controller.get_all_users(page, limit)
    return success_response("Get all users is successfully", users)


# @router.get("/profile", status_code=status.HTTP_200_OK)
# def getProfile(
#     current_user: dict = Depends(role_required(["admin", "user"])),
#     db: Session = Depends(get_db),
# ):
#     user = user_controller.get_user(db, current_user)
#     return success_response(
#         "Getting user profile is successfully",
#         {
#             "username": user.name,
#             "email": user.email,
#             "job_role": user.job_role,
#             "company_name": user.company_name,
#             "plan": user.plan,
#             "created_at": user.created_at,
#         },
#     )


# @router.post("/", response_model=UserResponseAPI, status_code=201)
# @limiter.limit("3/minute")
# def create_user(request: Request, user: UserCreate, db: Session = Depends(get_db)):
#     """
#     Create a new user.
#     """
#     new_user = user_controller.create_user(db, user)
#     return success_response("User created successfully", new_user)


# @router.put("/profile", status_code=status.HTTP_200_OK)
# def updateUser(
#     payload: UserUpdate,
#     current_user: dict = Depends(role_required(["admin", "user"])),
#     db: Session = Depends(get_db),
# ):
#     user = user_controller.updateUserHandler(db, payload, current_user)
#     return success_response(
#         "Update profile is successfully",
#         {
#             "email": user.email,
#             "job_role": user.job_role,
#             "company_name": user.company_name,
#             "plan": user.plan,
#         },
#     )


# @router.put("/profile/plan/{user_id}", status_code=status.HTTP_200_OK)
# def updateUserPlan(
#     user_id: int,
#     payload: UpdateUserPlan,
#     current_user: dict = Depends(role_required(["admin"])),
#     db: Session = Depends(get_db),
# ):
#     user = user_controller.update_user_plan(user_id, payload, current_user, db)
#     return success_response(
#         "user plan has been updated", {"email": user.email, "plan": user.plan}
#     )


# @router.put("/profile/updateDetail", status_code=status.HTTP_200_OK)
# def updateDetail(
#     detail: UpdateDetail,
#     current_user: dict = Depends(get_current_user),
#     db: Session = Depends(get_db),
# ):
#     """
#     Update detail information about the user
#     """
#     user = user_controller.updateDetailHandler(db, detail, current_user)
#     return success_response(
#         "Update detail information is successfully",
#         {
#             "email": user.email,
#             "job_role": detail.job_role,
#             "company_name": detail.company_name,
#         },
#     )


# @router.delete("/{user_id}")
# def delete_user(
#     user_id: int,
#     current_user: dict = Depends(role_required(["admin"])),
#     db: Session = Depends(get_db),
# ):
#     response = user_controller.delete_user_handler(user_id, current_user, db)
#     return success_response(response.get("message"), None)


# @router.get("/me", status_code=200)
# @limiter.limit("100/minute")
# def get_user(
#     request: Request, current_user: dict = Depends(role_required(["admin"]))
# ):  # -> dict[str, dict[Any, Any]]:
#     return {"response": current_user}
