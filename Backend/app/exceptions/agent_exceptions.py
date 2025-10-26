from fastapi import status

from app.exceptions import BaseCustomeException


class AgentNotFoundException(BaseCustomeException):
    def __init__(self, id):
        super().__init__(
            status_code=status.HTTP_404_NOT_FOUND,
            detail={
                "error": "AGENT_NOT_FOUND",
                "message": "Agent not found, please enter the correct id",
                "field": "id",
                "value": id,
            },
        )
