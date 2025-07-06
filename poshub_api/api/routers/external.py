import httpx
from fastapi import APIRouter, Depends

from poshub_api.infrastructure.http.client import safe_get
from poshub_api.shared.dependencies import get_http_client

router = APIRouter(tags=["external"])
url = "https://jsonplaceholder.typicode.com/posts"


@router.get("/external-demo")
async def call_external(http: httpx.AsyncClient = Depends(get_http_client)):
    return await safe_get(http, url)
