import logging
import os

import boto3


def log_api_key() -> str:
    """Log API key and return it as string"""
    ssm = boto3.client("ssm")
    param_path = os.getenv("API_KEY_PARAM", "/pos/api-key")

    response = ssm.get_parameter(Name=param_path, WithDecryption=False)
    api_key_value = response["Parameter"]["Value"]
    logging.info(f"API KEY from SSM: {api_key_value}")

    return {"name": response["Parameter"]["Name"], "ARN": response["Parameter"]["ARN"]}
