import logging
import os

import boto3
import jwt  # Make sure this is PyJWT

# Configure logging
logger = logging.getLogger()
logger.setLevel(logging.INFO)


def lambda_handler(event, context):
    logger.info("=== Lambda invoked ===")
    logger.info(f"Event received: {event}")

    ssm = boto3.client("ssm")
    param_name = os.environ.get("JWT_SECRET_PARAM", "/pos/jwt-secret")
    logger.info(f"Fetching JWT secret from SSM: {param_name}")

    try:
        response = ssm.get_parameter(Name=param_name, WithDecryption=True)
        secret = response["Parameter"]["Value"]
        logger.info("Successfully retrieved JWT secret.")
    except Exception as e:
        logger.error(f"Failed to get secret from SSM: {e}")
        raise Exception("Unauthorized")

    try:
        auth_header = event["authorizationToken"]
        token = auth_header.split(" ")[1]
        logger.info("Extracted JWT token from Authorization header.")
    except Exception as e:
        logger.error(f"Malformed or missing Authorization token: {e}")
        raise Exception("Unauthorized")

    try:
        decoded = jwt.decode(token, secret, algorithms=["HS256"])
    except Exception as e:
        logger.error(f"JWT decoding failed: {e}")
        raise Exception("Unauthorized")

    if "orders:write" in decoded.get("scopes", ""):
        logger.info("Scope validated: 'orders:write' found.")
        return {
            "principalId": decoded.get("sub", "user"),
            "policyDocument": {
                "Version": "2012-10-17",
                "Statement": [
                    {
                        "Action": "execute-api:Invoke",
                        "Effect": "Allow",
                        "Resource": event["methodArn"],
                    }
                ],
            },
            "context": {
                "user": decoded.get("sub", "user"),
                "scope": decoded.get("scopes", ""),
            },
        }
    else:
        logger.warning("Token scope missing 'orders:write'.")
        raise Exception("Unauthorized")
