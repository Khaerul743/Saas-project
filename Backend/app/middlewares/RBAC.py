from fastapi import Depends, HTTPException, status

from app.dependencies.auth import get_current_user  # ambil user dari cookie (JWT)
from app.utils.logger import get_logger

logger = get_logger(__name__)


def role_required(allowed_roles: list[str]):
    """
    Dependency untuk validasi role user.
    - allowed_roles: daftar role yang boleh akses route

    Contoh:
    @router.get("/admin", dependencies=[Depends(role_required(["admin"]))])
    """

    def wrapper(user: dict = Depends(get_current_user)):
        user_role = user.get("role")
        if not user_role:
            logger.warning(
                f"hit this endpoint with role not assigned: {user.get('email')}"
            )
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN, detail="Role not assigned"
            )

        if user_role not in allowed_roles:
            logger.warning(
                f"Permission denied for role {user_role}: {user.get('email')}"
            )
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail=f"Permission denied for role '{user_role}'",
            )
        return user  # kembalikan user agar handler bisa pakai datanya

    return wrapper
