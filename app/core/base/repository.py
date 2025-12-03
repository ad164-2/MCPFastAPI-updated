"""
Base Repository - Generic CRUD operations with session management
"""

from typing import TypeVar, Generic, List, Optional
from sqlalchemy.orm import Session
from app.core.database import SessionLocal

T = TypeVar("T")


class BaseRepository(Generic[T]):
    """Generic repository for basic CRUD operations with session management."""

    def __init__(self, model: type[T]):
        self.model = model
        self.db: Session = None

    def _get_db(self) -> Session:
        """Get or create database session."""
        if self.db is None:
            self.db = SessionLocal()
        return self.db

    def create(self, obj: T) -> T:
        """Create and commit a new object."""
        db = self._get_db()
        db.add(obj)
        db.commit()
        db.refresh(obj)
        return obj

    def get_by_id(self, obj_id: int) -> Optional[T]:
        """Get object by ID."""
        db = self._get_db()
        return db.query(self.model).filter(self.model.id == obj_id).first()

    def get_all(self, skip: int = 0, limit: int = 100) -> List[T]:
        """Get all objects with pagination."""
        db = self._get_db()
        return db.query(self.model).offset(skip).limit(limit).all()

    def update(self, obj: T) -> T:
        """Update and commit an object."""
        db = self._get_db()
        db.merge(obj)
        db.commit()
        return obj

    def delete(self, obj_id: int) -> bool:
        """Delete an object by ID."""
        db = self._get_db()
        obj = db.query(self.model).filter(self.model.id == obj_id).first()
        if obj:
            db.delete(obj)
            db.commit()
            return True
        return False

    def close(self):
        """Close database session."""
        if self.db:
            self.db.close()
            self.db = None

    def __del__(self):
        """Cleanup on deletion."""
        self.close()
