"""
Authentication middleware
"""

from fastapi import Request, status
from fastapi.responses import JSONResponse
from starlette.middleware.base import BaseHTTPMiddleware
from app.features.auth.jwt import get_user_id_from_token, create_access_token
from app.core.config import settings
from app.core.utils import get_logger
from app.features.users.user_repository import UserRepository


logger = get_logger(__name__)


class AuthMiddleware(BaseHTTPMiddleware):
    """Middleware to validate authentication tokens."""

    async def dispatch(self, request: Request, call_next):
        """
        Process request and validate token if needed.

        Args:
            request: HTTP request
            call_next: Next middleware/route

        Returns:
            Response
        """
        # Allow OPTIONS requests (CORS preflight) to pass through without authentication
        if request.method == "OPTIONS":
            return await call_next(request)
        
        # Check if route is excluded from authentication
        path = request.url.path
        if self._is_excluded_route(path):
            logger.debug(f"Public route accessed: {path}")
            return await call_next(request)

        # Get token from header
        auth_header = request.headers.get("Authorization")
        if not auth_header:
            logger.warning(f"No authorization header for route: {path}")
            return JSONResponse(
                status_code=status.HTTP_401_UNAUTHORIZED,
                content={"detail": "Missing authorization header"},
                headers={"WWW-Authenticate": "Bearer"},
            )

        # Extract token
        try:
            scheme, token = auth_header.split()
            if scheme.lower() != "bearer":
                raise ValueError("Invalid scheme")
        except ValueError:
            logger.warning(f"Invalid authorization header format: {auth_header}")
            return JSONResponse(
                status_code=status.HTTP_401_UNAUTHORIZED,
                content={"detail": "Invalid authorization header format"},
                headers={"WWW-Authenticate": "Bearer"},
            )

        # Verify token
        user_id = get_user_id_from_token(token)
        if not user_id:
            logger.warning(f"Invalid token provided for route: {path}")
            return JSONResponse(
                status_code=status.HTTP_401_UNAUTHORIZED,
                content={"detail": "Invalid or expired token"},
                headers={"WWW-Authenticate": "Bearer"},
            )

        # Add user to request state
        repo = UserRepository()
        user = repo.get_by_id(user_id)
        if not user or not user.is_active:
            logger.warning(f"Inactive or missing user for token: {user_id}")
            return JSONResponse(
                status_code=status.HTTP_401_UNAUTHORIZED,
                content={"detail": "Inactive or missing user"},
                headers={"WWW-Authenticate": "Bearer"},
            )
        request.state.user = user
        logger.debug(f"Authenticated user {user.username} accessing {path}")

        response = await call_next(request)

        # Check if user is authenticated and response is successful
        if hasattr(request.state, "user") and 200 <= response.status_code < 300:
            try:
                # Create new token for the user
                new_token = create_access_token(data={"sub": request.state.user.id,"username": user.username,"role": user.role})
                # Add token to response headers
                response.headers["X-Access-Token"] = new_token
            except Exception as e:
                logger.error(f"Failed to add refresh token: {str(e)}")

        return response

    @staticmethod
    def _is_excluded_route(path: str) -> bool:
        """
        Check if route is excluded from authentication.

        Args:
            path: Request path

        Returns:
            True if route is excluded
        """
        excluded = settings.auth_excluded_routes
        for excluded_route in excluded:
            if path == excluded_route or path.startswith(excluded_route):
                return True
        return False
