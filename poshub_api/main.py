"""The main entry point for the poshub API."""

import logging
from contextlib import asynccontextmanager

import httpx
import structlog
from fastapi import FastAPI

from poshub_api.api.routers import external, orders
from poshub_api.shared.exception_handler import (
    auth_exception_handler,
    scope_exception_handler,
)
from poshub_api.shared.exceptions import AuthError, ScopeError
from poshub_api.shared.middleware import correlation_id_middleware


def configure_logging():
    logging.basicConfig(
        format="%(message)s", level=logging.DEBUG, handlers=[logging.StreamHandler()]
    )

    structlog.configure(
        processors=[structlog.processors.JSONRenderer()],
        logger_factory=structlog.PrintLoggerFactory(),
        cache_logger_on_first_use=False,
    )


def create_app() -> FastAPI:
    """Create and configure the FastAPI application."""
    configure_logging()
    app = FastAPI(lifespan=lifespan)
    app.add_exception_handler(AuthError, auth_exception_handler)
    app.add_exception_handler(ScopeError, scope_exception_handler)
    # Middleware
    app.middleware("http")(correlation_id_middleware)

    return app


@asynccontextmanager
async def lifespan(app: FastAPI):
    """Async context manager for application lifespan events."""
    app.state.http = httpx.AsyncClient()
    yield
    await app.state.http.aclose()


# Create application
app: FastAPI = create_app()


# Basic routes
@app.get("/")
async def root():
    return {"message": "Hello, World!"}


@app.get("/health")
async def health():
    return {"status": "ok"}


# Include routers
app.include_router(orders.router)
app.include_router(external.router)
