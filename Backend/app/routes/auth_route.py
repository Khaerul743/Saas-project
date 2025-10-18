from fastapi import APIRouter, Depends, Response, status

from app.controllers.auth_controller import AuthController
from app.dependencies.factory import controller_factory
from app.middlewares.auth_middleware import role_based_access_control
from app.schema.auth_schema import AuthOut, LoginIn, RegisterIn
from app.utils.response import success_response

router = APIRouter(prefix="/api", tags=["auth"])

get_auth_controller = controller_factory(AuthController)


@router.post("/register", response_model=AuthOut, status_code=status.HTTP_201_CREATED)
async def register(
    response: Response,
    payload: RegisterIn,
    controller: AuthController = Depends(get_auth_controller),
):
    user = await controller.registerHandler(payload)
    return success_response(
        "Register is successfully",
        user,
    )


@router.post("/login", response_model=AuthOut, status_code=status.HTTP_200_OK)
async def login(
    response: Response,
    payload: LoginIn,
    controller: AuthController = Depends(get_auth_controller),
):
    user = await controller.loginHandler(response, payload)
    return success_response(
        "Login is successfully",
        user,
    )


@router.post("/logout", status_code=status.HTTP_200_OK)
def logout(
    response: Response,
    current_user: dict = Depends(role_based_access_control.get_current_user),
    controller: AuthController = Depends(get_auth_controller),
):
    user = controller.logoutHandler(response, current_user)
    return success_response("Logout successfully", {"email": user.get("email")})
