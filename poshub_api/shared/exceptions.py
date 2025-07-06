from typing import Optional

from fastapi import HTTPException, status


class NotFoundError(Exception):
    def __init__(self, message: str):
        self.message = message


class ScopeError(HTTPException):
    def __init__(self, required_scope: Optional[str] = None):
        detail = "Insufficient permissions"
        if required_scope:
            detail = f"Required scope: {required_scope}"
        super().__init__(
            status_code=status.HTTP_403_FORBIDDEN,
            detail=detail,
        )
