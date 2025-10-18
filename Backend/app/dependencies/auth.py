# from typing import Optional

# from fastapi import Cookie, HTTPException, status

# from app.dependencies.logger import get_logger
# from app.utils.security import decode_access_token

# logger = get_logger(__name__)


# def get_current_user(access_token: Optional[str] = Cookie(None)):
#     if not access_token:
#         logger.warning("Access attempt without token")
#         raise HTTPException(
#             status_code=status.HTTP_401_UNAUTHORIZED, detail="Not authenticated"
#         )

#     try:
#         payload = decode_access_token(access_token)
#         user_id = payload.get("id")
#         if not user_id:
#             raise HTTPException(
#                 status_code=status.HTTP_401_UNAUTHORIZED, detail="Invalid token payload"
#             )
#         return payload
#     except Exception as e:
#         logger.error(f"Unexpected error while decode token: {e}")
#         raise HTTPException(
#             status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
#             detail="Internal server error, please try again later.",
#         )
