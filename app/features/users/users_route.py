"""
User management API endpoints - CRUD operations
"""

from fastapi import APIRouter, status, Request
from fastapi.responses import JSONResponse
from app.features.users.user_repository import UserRepository
from app.features.auth.auth_schemas import UserResponse, UserUpdate
from app.core.utils import get_logger

logger = get_logger(__name__)

router = APIRouter(prefix="/users", tags=["users"])

@router.get("/")
def get_users():
    """Get all active users (requires authentication via middleware)."""
    try:
        repo = UserRepository()
        users = repo.get_active_users()
        users_data = [UserResponse.model_validate(user).model_dump(mode="json") for user in users]
        return JSONResponse(
            status_code=status.HTTP_200_OK,
            content=users_data
        )
    except Exception as e:
        logger.error(f"Error fetching users: {str(e)}", exc_info=True)
        return JSONResponse(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            content={"detail": "Error fetching users"}
        )

@router.get("/{user_id}")
def get_user(user_id: int):
    """Get user by ID (requires authentication via middleware)."""
    try:
        repo = UserRepository()
        user = repo.get_by_id(user_id)
        if not user:
            return JSONResponse(
                status_code=status.HTTP_404_NOT_FOUND,
                content={"detail": "User not found"}
            )
        user_response = UserResponse.model_validate(user)
        return JSONResponse(
            status_code=status.HTTP_200_OK,
            content=user_response.model_dump(mode="json")
        )
    except Exception as e:
        logger.error(f"Error fetching user: {str(e)}", exc_info=True)
        return JSONResponse(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            content={"detail": "Error fetching user"}
        )

@router.put("/{user_id}")
def update_user(user_id: int, user: UserUpdate, request: Request = None):
    """Update user profile (requires authentication via middleware)."""
    try:
        repo = UserRepository()
        updated_user = repo.update_user(user_id, user)
        user_response = UserResponse.model_validate(updated_user)
        return JSONResponse(
            status_code=status.HTTP_200_OK,
            content=user_response.model_dump(mode="json")
        )
    except Exception as e:
        logger.error(f"Error updating user: {str(e)}", exc_info=True)
        return JSONResponse(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            content={"detail": "Error updating user"}
        )

@router.delete("/{user_id}")
def delete_user(user_id: int):
    """Delete user account (requires authentication via middleware)."""
    try:
        repo = UserRepository()
        repo.delete_user(user_id)
        return JSONResponse(
            status_code=status.HTTP_204_NO_CONTENT,
            content={}
        )
    except Exception as e:
        logger.error(f"Error deleting user: {str(e)}", exc_info=True)
        return JSONResponse(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            content={"detail": "Error deleting user"}
        )
