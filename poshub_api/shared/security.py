import logging
import os
from typing import List, Optional

import boto3
import jwt
from fastapi import Depends
from fastapi.security import HTTPAuthorizationCredentials, HTTPBearer
from jwt import DecodeError
from pydantic.v1 import BaseSettings

from poshub_api.shared.exceptions import AuthError, ScopeError

# Setup logging
logger = logging.getLogger(__name__)
logger.setLevel(logging.INFO)


class JWTSettings(BaseSettings):
    """JWT settings."""

    jwt_secret: str = os.getenv("JWT_SECRET", "")
    jwt_algorithm: str = "HS256"
    jwt_issuer: str = "poshub-api"
    jwt_audience: str = os.getenv("JWT_AUDIENCE", "")

    class Config:
        env_file = ".env"


def get_jwt_settings() -> JWTSettings:
    """Get JWT settings from SSM."""
    try:
        param_name = os.environ["JWT_SECRET_PARAM"]
        logger.info(f"Fetching JWT secret from SSM: {param_name}")
        ssm = boto3.client("ssm")
        secret = ssm.get_parameter(Name=param_name, WithDecryption=True)["Parameter"][
            "Value"
        ]
        logger.info("Successfully retrieved JWT secret from SSM")
        return JWTSettings(jwt_secret=secret)
    except Exception:
        logger.exception("Failed to load JWT settings from SSM")
        raise AuthError("Server error while fetching JWT config")


security_scheme = HTTPBearer()


def validate_token(
    credentials: HTTPAuthorizationCredentials = Depends(security_scheme),
) -> dict:
    """Base token validation."""
    jwt_settings = get_jwt_settings()

    try:
        token = credentials.credentials
        logger.info(f"Validating JWT token for issuer {jwt_settings.jwt_issuer}")
        payload = jwt.decode(
            token,
            jwt_settings.jwt_secret,
            algorithms=[jwt_settings.jwt_algorithm],
            iss=jwt_settings.jwt_issuer,
            options={"verify_exp": True},
        )
        logger.info(f"Token validated. Subject: {payload.get('sub')}")
        return payload
    except DecodeError as e:
        logger.warning(f"Invalid token: {e}")
        raise AuthError(f"Invalid token: {str(e)}")
    except Exception:
        logger.exception("Unexpected error during token validation")
        raise AuthError("Authorization failed")


def check_scopes(
    required_scope: Optional[str] = None, required_scopes: Optional[List[str]] = None
):
    """Factory for scope checking."""

    def dependency(payload: dict = Depends(validate_token)):
        scopes = payload.get("scopes", [])
        logger.info(f"Checking scopes: {scopes}")

        if required_scope and required_scope not in scopes:
            logger.warning(f"Missing required scope: {required_scope}")
            raise ScopeError(required_scope)

        if required_scopes and not any(scope in scopes for scope in required_scopes):
            logger.warning(f"Missing one of required scopes: {required_scopes}")
            raise ScopeError(", ".join(required_scopes))

        return payload

    return dependency
