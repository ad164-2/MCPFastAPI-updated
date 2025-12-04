"""
FastAPI Application Factory with Vertical Feature Architecture
"""

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from contextlib import asynccontextmanager
from app.core.config import settings
from app.core.database import init_db, close_db
from app.core.config.observability_config import initialize_observability, shutdown_observability
from app.middleware import AuthMiddleware
from app.features import (
    auth_router,
    users_router,
    chat_router,
    documents_router,
)
from app.core.utils import get_logger

logger = get_logger(__name__)


@asynccontextmanager
async def lifespan(app: FastAPI):
    """Application lifespan context manager."""
    # Startup
    logger.info(f"Starting {settings.app_name}")
    
    # Initialize database
    init_db()
    
    # Initialize observability (Phoenix + OpenTelemetry)
    initialize_observability()

    yield

    # Shutdown
    logger.info(f"Shutting down {settings.app_name}")
    
    # Shutdown observability
    shutdown_observability()
    
    # Close database
    close_db()


def create_app() -> FastAPI:
    """
    Create and configure FastAPI application.

    Returns:
        Configured FastAPI instance
    """
    app = FastAPI(
        title=settings.api_title,
        description=settings.api_description,
        version=settings.app_version,
        debug=settings.debug,
        lifespan=lifespan,
    )

    # Add CORS middleware
    app.add_middleware(
        CORSMiddleware,
        allow_origins=["*"],
        allow_credentials=True,
        allow_methods=["*"],
        allow_headers=["*"],
        expose_headers=["*"]
    )

    # Add authentication middleware
    app.add_middleware(AuthMiddleware)

    # Include routers
    app.include_router(auth_router, prefix=settings.api_prefix)
    app.include_router(users_router, prefix=settings.api_prefix)
    app.include_router(chat_router, prefix=settings.api_prefix)
    app.include_router(documents_router, prefix=settings.api_prefix)

    logger.info("FastAPI application created successfully")
    return app
