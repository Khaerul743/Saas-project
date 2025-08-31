from fastapi import APIRouter, Depends, HTTPException, Response, status
from fastapi.security import OAuth2PasswordRequestForm
from sqlalchemy.orm import Session

from app.configs.database import get_db
from app.controllers.auth_controller import loginHandler
from app.models.auth_model import AuthIn, AuthOut
from app.utils.response import success_response

router = APIRouter(prefix="/api", tags=["auth"])


@router.post("/login", response_model=AuthOut, status_code=status.HTTP_200_OK)
def login(response: Response, payload: AuthIn, db: Session = Depends(get_db)):
    user = loginHandler(response, db, payload)
    return success_response(
        "Login is successfully",
        {"username": user.name, "email": user.email, "plan": user.plan},
    )
