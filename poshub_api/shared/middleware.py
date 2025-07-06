import uuid

from fastapi import Request, Response
from structlog.contextvars import bind_contextvars, clear_contextvars


async def correlation_id_middleware(request: Request, call_next):
    clear_contextvars()

    # Get or generate correlation ID
    correlation_id = request.headers.get("X-Correlation-ID", str(uuid.uuid4()))
    bind_contextvars(correlation_id=correlation_id)

    response: Response = await call_next(request)
    response.headers["X-Correlation-ID"] = correlation_id
    return response
