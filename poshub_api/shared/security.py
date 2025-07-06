from multiprocessing.context import AuthenticationError
from typing import Optional

import jwt
from fastapi import Depends
from fastapi.security import HTTPAuthorizationCredentials, HTTPBearer
from pydantic.v1 import BaseSettings

from poshub_api.shared.exceptions import ScopeError


class JWTSettings(BaseSettings):
    """JWT settings."""

    jwt_secret: str
    jwt_algorithm: str = "HS256"
    jwt_issuer: str = "poshub-api"

    class Config:
        env_file = ".env"


security_scheme = HTTPBearer(auto_error=False)


def get_jwt_settings() -> JWTSettings:
    """Get JWT settings."""
    return JWTSettings()


def validate_token(
    credentials: Optional[HTTPAuthorizationCredentials] = Depends(security_scheme),
    required_scope: Optional[str] = None,
    required_scopes: Optional[str] = None,
) -> dict:
    """Validate token."""
    if credentials is None:
        raise AuthenticationError("No credentials provided")

    jwt_settings = get_jwt_settings()

    try:
        token = credentials.credentials
        payload = jwt.decode(
            token,
            jwt_settings.jwt_secret,
            algorithms=[jwt_settings.jwt_algorithm],
            issuers=jwt_settings.jwt_issuer,
            options={"verify_exp": True},
        )

        # handle both single and multiple scopes
        if required_scope and required_scope not in payload.get("scopes", []):
            raise ScopeError(required_scope)

        if required_scopes and not any(
            scope in payload.get("scopes", []) for scope in required_scopes
        ):
            raise ScopeError(", ".join(required_scopes))

        return payload

    except jwt.ExpiredSignatureError:
        raise AuthenticationError("Token has expired")
    except jwt.InvalidTokenError as e:
        raise AuthenticationError(f"Invalid token: {str(e)}") from e
