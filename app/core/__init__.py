"""
Core Module - Shared infrastructure (config, database, logging, utilities)
"""

from .config import settings
from .database import init_db, close_db, get_db
from .base.entity import Base
from .utils import get_logger

__all__ = ["settings", "init_db", "close_db", "get_db", "Base", "get_logger"]
