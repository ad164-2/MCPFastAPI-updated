"""
User repository implementation
"""

from typing import Optional
from app.core.base import BaseRepository
from app.features.users.user_entity import User
from app.core.utils import get_logger, NotFoundException

logger = get_logger(__name__)


class UserRepository(BaseRepository[User]):
    """Repository for User entity with custom queries."""

    def __init__(self):
        super().__init__(User)

    def get_by_username(self, username: str) -> Optional[User]:
        """Get user by username."""
        logger.info(f"Fetching user by username: {username}")
        db = self._get_db()
        return db.query(User).filter(User.username == username).first()

    def get_active_users(self, skip: int = 0, limit: int = 100) -> list[User]:
        """Get all active users."""
        logger.info(f"Fetching active users (skip={skip}, limit={limit})")
        db = self._get_db()
        return db.query(User).filter(User.is_active == True).offset(skip).limit(limit).all()

    def create_user(self, username: str, password_hash: str, role: str = "user") -> User:
        """Create a new user."""
        logger.info(f"Creating user: {username}")
        db = self._get_db()
        user = User(username=username, password_hash=password_hash, role=role)
        db.add(user)
        db.commit()
        db.refresh(user)
        logger.info(f"User created: {username} (id={user.id})")
        return user

    def update_user(self, user_id: int, user_data) -> User:
        """Update user profile."""
        user = self.get_by_id(user_id)
        if not user:
            raise NotFoundException("User not found")
        
        update_data = user_data.model_dump(exclude_unset=True, exclude_none=True)
        for key, value in update_data.items():
            if hasattr(user, key) and key != "id":
                setattr(user, key, value)
        
        db = self._get_db()
        db.commit()
        db.refresh(user)
        return user

    def delete_user(self, user_id: int):
        """Delete user account."""
        user = self.get_by_id(user_id)
        if not user:
            raise NotFoundException("User not found")
        return self.delete(user_id)

    def deactivate_user(self, user_id: int) -> Optional[User]:
        """Deactivate user account."""
        user = self.get_by_id(user_id)
        if user:
            db = self._get_db()
            user.is_active = False
            db.commit()
            db.refresh(user)
            logger.info(f"User deactivated: {user_id}")
        return user

    def activate_user(self, user_id: int) -> Optional[User]:
        """Activate user account."""
        user = self.get_by_id(user_id)
        if user:
            db = self._get_db()
            user.is_active = True
            db.commit()
            db.refresh(user)
            logger.info(f"User activated: {user_id}")
        return user

    def update_last_login(self, user_id: int):
        """Update user's last login timestamp."""
        from datetime import datetime
        user = self.get_by_id(user_id)
        if user:
            db = self._get_db()
            user.last_login = datetime.utcnow()
            db.commit()
            logger.info(f"Updated last login for user: {user_id}")
