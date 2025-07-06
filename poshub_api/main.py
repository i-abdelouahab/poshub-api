"""The main entry point for the poshub API."""

from contextlib import asynccontextmanager

import httpx
from fastapi import FastAPI

from poshub_api.api.routers import external, orders
from poshub_api.shared.middleware import correlation_id_middleware


def create_app() -> FastAPI:
    """Create and configure the FastAPI application."""
    app = FastAPI(lifespan=lifespan)

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
