"""This module implements the HTTP client configuration."""

import httpx
import structlog
from fastapi import HTTPException
from tenacity import retry, retry_if_exception_type, stop_after_attempt, wait_fixed

logger = structlog.getLogger()


@retry(
    reraise=True,
    stop=stop_after_attempt(2),
    wait=wait_fixed(1),
    retry=retry_if_exception_type(httpx.RequestError),
)
async def safe_get(client: httpx.AsyncClient, url: str):
    try:
        response = await client.get(url, timeout=10)
        response.raise_for_status()
        return response.json()
    except httpx.HTTPStatusError as e:
        logger.error(
            "External API responded with error", status=e.response.status_code, url=url
        )
        raise HTTPException(status_code=400, detail="External API returned an error")
    except httpx.RequestError as e:
        logger.error("External API request failed", error=str(e))
        raise HTTPException(status_code=408, detail="Failed to reach external API")
