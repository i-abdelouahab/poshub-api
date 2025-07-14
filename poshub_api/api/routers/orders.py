import json
import logging
import os
from typing import List
from uuid import UUID

import boto3
from fastapi import APIRouter, Depends, HTTPException
from fastapi.encoders import jsonable_encoder

from poshub_api.domain.models import OrderIn, OrderOut
from poshub_api.services.order_service import OrderService
from poshub_api.shared.dependencies import get_order_service
from poshub_api.shared.exceptions import NotFoundError
from poshub_api.shared.security import check_scopes

router = APIRouter(prefix="/orders", tags=["orders"])

# Configure logging
logger = logging.getLogger(__name__)
logger.setLevel(logging.INFO)  # or os.getenv("LOG_LEVEL", "INFO")

sqs = boto3.client("sqs")
ssm = boto3.client("ssm")

# Cache the queue URL after first fetch
QUEUE_URL = None


def get_queue_url():
    global QUEUE_URL
    if not QUEUE_URL:
        try:
            param_name = os.environ["QUEUE_URL_PARAM"]
            QUEUE_URL = ssm.get_parameter(Name=param_name, WithDecryption=False)[
                "Parameter"
            ]["Value"]
            logger.info(f"✅ Loaded QUEUE_URL from SSM: {QUEUE_URL}")
        except Exception:
            logger.error("❌ Failed to retrieve QUEUE_URL from SSM", exc_info=True)
            raise RuntimeError("QUEUE_URL could not be loaded")
    return QUEUE_URL


@router.post("/", response_model=OrderOut, status_code=201)
async def create_order(
    order: OrderIn,
    service: OrderService = Depends(get_order_service),
    token_payload: dict = Depends(check_scopes(required_scope="orders:write")),
) -> OrderOut:
    """
    Create a new order.
    Requires 'orders:write' scope in the JWT token.
    """
    try:
        created_order = service.create_order(order, user_context=token_payload)
        message = json.dumps(jsonable_encoder(created_order))

        queue_url = get_queue_url()
        response = sqs.send_message(QueueUrl=queue_url, MessageBody=message)

        logger.info(f"✅ Order created: {created_order.order_id}")
        logger.info(f"📨 Message sent to SQS (ID: {response['MessageId']})")

        return created_order
    except Exception:
        logger.error("❌ Failed to create order or send to SQS", exc_info=True)
        raise HTTPException(status_code=500, detail="Internal server error")


@router.get("/all", response_model=List[OrderOut])
async def get_orders(
    service: OrderService = Depends(get_order_service),
) -> List[OrderOut]:
    try:
        return list(service.orders.values())
    except NotFoundError as e:
        logger.warning("❗ Orders not found")
        raise HTTPException(status_code=404, detail=e.message)


@router.get("/{id}", response_model=OrderOut)
async def get_order(
    id: UUID, service: OrderService = Depends(get_order_service)
) -> OrderOut:
    try:
        return service.get_order_by_id(id)
    except NotFoundError as e:
        logger.warning(f"❗ Order not found: {id}")
        raise HTTPException(status_code=404, detail=e.message)
