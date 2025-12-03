"""
Features Module - All application features (vertical modules)
"""

from .auth import router as auth_router
from .users.users_route import router as users_router
from .chat import chat_router

__all__ = [
    "auth_router",
    "users_router",
    "chat_router",
]


