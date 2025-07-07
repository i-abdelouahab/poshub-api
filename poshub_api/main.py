"""The main entry point for the poshub API."""

from contextlib import asynccontextmanager
from typing import Dict, List

import httpx
import structlog
from fastapi import FastAPI, status
from fastapi.openapi.utils import get_openapi
from pydantic.v1 import BaseSettings
from starlette.responses import JSONResponse

from poshub_api.api.routers import basics, externals, orders
from poshub_api.shared.exception_handler import (
    auth_exception_handler,
    scope_exception_handler,
)
from poshub_api.shared.exceptions import AuthError, ScopeError
from poshub_api.shared.logging import configure_logging
from poshub_api.shared.middleware import correlation_id_middleware

# Configure logger early to catch all logs
logger = structlog.get_logger(__name__)


class AppConfig(BaseSettings):
    """Application configuration model."""

    title: str
    version: str
    description: str
    servers: List[Dict]
    contact: Dict
    debug: bool
    cors_origins: List[str] = []
    enable_docs: bool

    class Config:
        env_file = ".env"
        env_file_encoding = "utf-8"
        env_prefix = "POSHUB_"


def get_app_config() -> AppConfig:
    return AppConfig()


def custom_openapi(app: FastAPI) -> Dict:
    """Generate custom OpenAPI schema with security requirements.

    Returns:
        The OpenAPI schema as a dictionary.
    """
    if app.openapi_schema:
        return app.openapi_schema

    try:
        app_config = get_app_config()
        openapi_schema = get_openapi(
            title=app_config.title,
            version=app_config.version,
            description=app_config.description,
            routes=app.routes,
            servers=app_config.servers,
        )

        # Add security schemes
        openapi_schema["components"]["securitySchemes"] = {
            "bearerAuth": {
                "type": "http",
                "scheme": "bearer",
                "bearerFormat": "JWT",
                "description": "JWT token obtained from the authentication endpoint",
            }
        }

        # Secure all endpoints by default
        openapi_schema["security"] = [{"bearerAuth": []}]
        app.openapi_schema = openapi_schema
        return app.openapi_schema
    except Exception as e:
        logger.error("Failed to generate OpenAPI schema", error=str(e))
        raise


def configure_routes(app: FastAPI) -> None:
    app.include_router(basics.router)
    app.include_router(orders.router)
    app.include_router(externals.router)


def configure_exception_handlers(app: FastAPI) -> None:
    app.add_exception_handler(AuthError, auth_exception_handler)
    app.add_exception_handler(ScopeError, scope_exception_handler)

    # Add handler for unexpected errors
    @app.exception_handler(Exception)
    async def unexpected_error_handler(request, exc):
        logger.error(
            "Unexpected error occurred",
            exc_info=exc,
            path=request.url.path,
            method=request.method,
        )
        return JSONResponse(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            content={"detail": "Internal server error"},
        )


@asynccontextmanager
async def lifespan(app: FastAPI):
    """Async context manager for application lifespan events.

    Args:
        app: FastAPI application instance.
    """
    logger.info("Application startup - initializing resources")

    # Initialize HTTP client
    app.state.http = httpx.AsyncClient(timeout=30.0)
    logger.info("HTTP client initialized")

    try:
        yield
    finally:
        logger.info("Application shutdown - cleaning up resources")
        await app.state.http.aclose()
        logger.info("HTTP client closed")


def create_app() -> FastAPI:
    """Create and configure the FastAPI application."""
    app_config = get_app_config()
    configure_logging(app_config.debug)
    app = FastAPI(lifespan=lifespan)

    # Configure components
    app.middleware("http")(correlation_id_middleware)
    configure_routes(app)
    configure_exception_handlers(app)

    # Configure openapi
    custom_openapi(app)

    return app


# Create application
app: FastAPI = create_app()
