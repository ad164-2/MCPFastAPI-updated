"""
Core Base Module - Base classes for entities and repositories
"""

from .entity import Base, BaseEntity
from .repository import BaseRepository

__all__ = ["Base", "BaseEntity", "BaseRepository"]
