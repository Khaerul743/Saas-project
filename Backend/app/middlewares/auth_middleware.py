from typing import Optional

from fastapi import Cookie, Depends, HTTPException, status

# ambil user dari cookie (JWT)
from app.dependencies.logger import get_logger
from app.utils.security import JWTHandler


class RBAC:
    def __init__(self):
        self.jwt = JWTHandler()
        self.logger = get_logger(__name__)

    def get_current_user(self, access_token: Optional[str] = Cookie(None)):
        if not access_token:
            self.logger.warning("Access attempt without token")
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED, detail="Not authenticated"
            )

        try:
            payload = self.jwt.decode_access_token(access_token)
            user_id = payload.get("id")
            if not user_id:
                raise HTTPException(
                    status_code=status.HTTP_401_UNAUTHORIZED,
                    detail="Invalid token payload",
                )
            return payload
        except Exception as e:
            self.logger.error(f"Unexpected error while decode token: {e}")
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail="Internal server error, please try again later.",
            )

    def role_required(self, allowed_roles: list[str]):
        """
        Dependency untuk validasi role user.
        - allowed_roles: daftar role yang boleh akses route

        Contoh:
        @router.get("/admin", dependencies=[Depends(role_required(["admin"]))])
        """

        def wrapper(user: dict = Depends(self.get_current_user)):
            user_role = user.get("role")
            if not user_role:
                self.logger.warning(
                    f"hit this endpoint with role not assigned: {user.get('email')}"
                )
                raise HTTPException(
                    status_code=status.HTTP_403_FORBIDDEN, detail="Role not assigned"
                )

            if user_role not in allowed_roles:
                self.logger.warning(
                    f"Permission denied for role {user_role}: {user.get('email')}"
                )
                raise HTTPException(
                    status_code=status.HTTP_403_FORBIDDEN,
                    detail=f"Permission denied for role '{user_role}'",
                )
            return user  # kembalikan user agar handler bisa pakai datanya

        return wrapper


role_based_access_control = RBAC()
