from fastapi import APIRouter, Depends, Request
from sqlalchemy.orm import Session

from app.configs.database import get_db
from app.configs.limiter import limiter
from app.controllers import user_controller
from app.dependencies.auth import get_current_user
from app.models.user_model import UserCreate, UserOut
from app.utils.response import success_response

router = APIRouter(prefix="/api/users", tags=["users"])


@router.post("/", response_model=UserOut, status_code=201)
@limiter.limit("3/minute")
def create_user(request: Request, user: UserCreate, db: Session = Depends(get_db)):
    """
    Create a new user.
    """
    new_user = user_controller.create_user(db, user)
    return success_response("User created successfully", new_user)


@router.get("/me", status_code=200)
@limiter.limit("100/minute")
def get_user(request: Request, current_user: dict = Depends(get_current_user)):
    return {"response": current_user}
