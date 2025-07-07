from typing import List, Optional

import jwt
from fastapi import Depends
from fastapi.security import HTTPAuthorizationCredentials, HTTPBearer
from jwt import PyJWTError
from pydantic.v1 import BaseSettings

from poshub_api.shared.exceptions import AuthError, ScopeError


class JWTSettings(BaseSettings):
    """JWT settings."""

    jwt_secret: str
    jwt_algorithm: str = "HS256"
    jwt_issuer: str = "poshub-api"
    jwt_audience: str

    class Config:
        env_file = ".env"


def get_jwt_settings() -> JWTSettings:
    """Get JWT settings."""
    return JWTSettings()


security_scheme = HTTPBearer()


def validate_token(
    credentials: HTTPAuthorizationCredentials = Depends(security_scheme),
) -> dict:
    """Base token validation"""
    jwt_settings = get_jwt_settings()

    try:
        token = credentials.credentials
        payload = jwt.decode(
            token,
            jwt_settings.jwt_secret,
            algorithms=[jwt_settings.jwt_algorithm],
            iss=jwt_settings.jwt_issuer,
            options={"verify_exp": True},
        )
        return payload
    except PyJWTError as e:
        raise AuthError(f"Invalid token: {str(e)}")


def check_scopes(
    required_scope: Optional[str] = None, required_scopes: Optional[List[str]] = None
):
    """Factory for scope checking"""

    def dependency(payload: dict = Depends(validate_token)):
        if required_scope and required_scope not in payload.get("scopes", []):
            raise ScopeError(required_scope)
        if required_scopes and not any(
            s in payload.get("scopes", []) for s in required_scopes
        ):
            raise ScopeError(", ".join(required_scopes))
        return payload

    return dependency
