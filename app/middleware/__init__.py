"""
Middleware Module - Global middleware
"""

from .auth_middleware import AuthMiddleware

__all__ = ["AuthMiddleware"]
