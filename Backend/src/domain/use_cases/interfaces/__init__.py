"""
Repository interfaces for use cases.
"""

from .agent_obj_interface import IStorageAgentObj
from .agent_repository_interface import IAgentRepository
from .document_repository_interface import DocumentRepositoryInterface
from .user_repository_interface import UserRepositoryInterface

__all__ = [
    "IAgentRepository",
    "UserRepositoryInterface",
    "DocumentRepositoryInterface",
    "IStorageAgentObj",
]
