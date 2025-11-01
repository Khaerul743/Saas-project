from fastapi import Depends
from sqlalchemy.ext.asyncio import AsyncSession

from src.config.database import get_db


def controller_factory(ControllerClass):
    """
    Membuat dependency generator untuk controller apapun.
    Contoh:
        get_auth_controller = controller_factory(AuthController)
    """

    async def _get_controller(db: AsyncSession = Depends(get_db)):
        return ControllerClass(db)

    return _get_controller
