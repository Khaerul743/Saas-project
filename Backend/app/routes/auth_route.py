from fastapi import APIRouter, Depends, Response, status
from sqlalchemy.orm import Session

from app.configs.database import get_db
from app.controllers.auth_controller import loginHandler, logoutHandler, registerHandler
from app.dependencies.auth import get_current_user
from app.models.auth.auth_model import AuthIn, AuthOut, RegisterModel
from app.utils.response import success_response

router = APIRouter(prefix="/api", tags=["auth"])


@router.post("/register", response_model=AuthOut, status_code=status.HTTP_201_CREATED)
def register(response: Response, payload: RegisterModel, db: Session = Depends(get_db)):
    user = registerHandler(db, payload)
    return success_response(
        "Register is successfully",
        {"username": user.name, "email": user.email, "plan": user.plan},
    )


@router.post("/login", response_model=AuthOut, status_code=status.HTTP_200_OK)
def login(response: Response, payload: AuthIn, db: Session = Depends(get_db)):
    user = loginHandler(response, db, payload)
    return success_response(
        "Login is successfully",
        {"username": user.name, "email": user.email, "plan": user.plan},
    )


@router.post("/logout", status_code=status.HTTP_200_OK)
def logout(response: Response, current_user: dict = Depends(get_current_user)):
    user = logoutHandler(response, current_user)
    return success_response("Logout successfully", {"email": user.get("email")})
