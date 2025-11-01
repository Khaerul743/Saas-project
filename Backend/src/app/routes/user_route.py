from fastapi import APIRouter, Depends, Query, Request, status
from sqlalchemy.ext.asyncio import AsyncSession

from app.utils.response import success_response
from src.app.controllers.user_controller import UserController
from src.app.middlewares.auth_middleware import role_based_access_control
from src.app.validators.user_schema import (
    ShowUserProfileOut,
    UpdateUserPlan,
    UpdateUserPlanResponse,
    UserOutPaginate,
    UserUpdate,
    UserUpdateOut,
)
from src.config.database import get_db
from src.config.limiter import limiter
from src.core.utils.context import CurrentContext
from src.core.utils.factory import controller_factory

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


@router.get(
    "/profile", response_model=ShowUserProfileOut, status_code=status.HTTP_200_OK
)
async def getProfile(
    request: Request,
    current_user: dict = Depends(
        role_based_access_control.role_required(["admin", "user"])
    ),
    db: AsyncSession = Depends(get_db),
):
    controller = UserController(db, request)
    user_profile = await controller.get_user_profile()
    return success_response("Getting user profile is successfully", user_profile)


@router.put("/{user_id}", response_model=UserUpdateOut, status_code=status.HTTP_200_OK)
async def updateUser(
    user_id: int,
    request: Request,
    user_update: UserUpdate,
    current_user: dict = Depends(
        role_based_access_control.role_required(["admin", "user"])
    ),
    db: AsyncSession = Depends(get_db),
):
    controller = UserController(db, request)
    updated_user = await controller.update_user(
        user_id=user_id,
        name=user_update.name,
        company_name=user_update.company_name,
        job_role=user_update.job_role,
    )
    return success_response("User updated successfully", updated_user)


@router.put(
    "/plan/{user_id}",
    response_model=UpdateUserPlanResponse,
    status_code=status.HTTP_200_OK,
)
async def updateUserPlan(
    user_id: int,
    request: Request,
    plan_update: UpdateUserPlan,
    current_user: dict = Depends(
        role_based_access_control.role_required(["admin", "user"])
    ),
    db: AsyncSession = Depends(get_db),
):
    controller = UserController(db, request)
    updated_user = await controller.update_user_plan(user_id, plan_update.plan)
    return success_response("User plan updated successfully", updated_user)


@router.delete("/{user_id}", status_code=status.HTTP_200_OK)
async def deleteUser(
    user_id: int,
    request: Request,
    current_user: dict = Depends(
        role_based_access_control.role_required(["admin", "user"])
    ),
    db: AsyncSession = Depends(get_db),
):
    controller = UserController(db, request)
    deleted_user = await controller.delete_user(user_id)
    return success_response(
        f"User {deleted_user.email} deleted successfully",
        {"email": deleted_user.email, "id": deleted_user.id},
    )
