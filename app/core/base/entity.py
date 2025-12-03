"""
Base Entity - All database entities inherit from this
"""

from sqlalchemy import Column, DateTime
from sqlalchemy.orm import declarative_base
from datetime import datetime

Base = declarative_base()


class BaseEntity(Base):
    """Base entity class for all database models."""

    __abstract__ = True

    created_at = Column(DateTime, default=datetime.utcnow, nullable=False)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow, nullable=False)
