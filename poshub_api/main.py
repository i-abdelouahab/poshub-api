"""The main entry point for the poshub API."""

from contextlib import asynccontextmanager

import httpx
from fastapi import FastAPI

from poshub_api.api.routers import external, orders


@asynccontextmanager
async def lifespan(app: FastAPI):
    app.state.http = httpx.AsyncClient()
    yield
    await app.state.http.aclose()


app = FastAPI(lifespan=lifespan)


@app.get("/")
async def root():
    return {"message": "Hello, World!"}


@app.get("/health")
async def health():
    return {"status": "ok"}


app.include_router(orders.router)
app.include_router(external.router)
