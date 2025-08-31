from fastapi import APIRouter, Depends, Request, status
from sqlalchemy.orm import Session

from app.configs.database import get_db
from app.configs.limiter import limiter
from app.controllers import user_controller
from app.dependencies.auth import get_current_user
from app.middlewares.RBAC import role_required
from app.models.user_model import UpdateDetail, UserCreate, UserResponseAPI
from app.utils.response import success_response

router = APIRouter(prefix="/api/users", tags=["users"])


@router.post("/", response_model=UserResponseAPI, status_code=201)
@limiter.limit("3/minute")
def create_user(request: Request, user: UserCreate, db: Session = Depends(get_db)):
    """
    Create a new user.
    """
    new_user = user_controller.create_user(db, user)
    return success_response("User created successfully", new_user)


@router.put("/updateDetail", status_code=status.HTTP_200_OK)
def updateDetail(
    detail: UpdateDetail,
    current_user: dict = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    """
    Update detail information about the user
    """
    user = user_controller.updateDetailHandler(db, detail, current_user)
    return success_response(
        "Update detail information is successfully",
        {
            "email": user.email,
            "job_role": detail.job_role,
            "company_name": detail.company_name,
        },
    )


@router.get("/me", status_code=200)
@limiter.limit("100/minute")
def get_user(
    request: Request, current_user: dict = Depends(role_required(["admin"]))
):  # -> dict[str, dict[Any, Any]]:
    return {"response": current_user}
