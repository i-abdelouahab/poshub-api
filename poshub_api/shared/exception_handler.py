from fastapi import Request
from fastapi.responses import JSONResponse

from poshub_api.shared.exceptions import AuthError, ScopeError


async def auth_exception_handler(request: Request, exc: AuthError):
    return JSONResponse(
        status_code=401,
        content={"detail": str(exc.detail)},
        headers={"WWW-Authenticate": "Bearer"},
    )


async def scope_exception_handler(request: Request, exc: ScopeError):
    return JSONResponse(status_code=403, content={"detail": str(exc.detail)})
