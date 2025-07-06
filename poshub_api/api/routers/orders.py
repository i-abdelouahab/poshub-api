from typing import List
from uuid import UUID

from fastapi import APIRouter, Depends, HTTPException

from poshub_api.domain.models import OrderIn, OrderOut
from poshub_api.services.order_service import OrderService
from poshub_api.shared.dependencies import get_order_service
from poshub_api.shared.exceptions import NotFoundError
from poshub_api.shared.security import validate_token

router = APIRouter(prefix="/orders", tags=["orders"])


@router.post("/", response_model=OrderOut, status_code=201)
async def create_order(
    order: OrderIn,
    service: OrderService = Depends(get_order_service),
    token_payload: dict = Depends(
        lambda: validate_token(required_scope="orders:write")
    ),
) -> OrderOut:
    """
    Create a new order.
    Requires 'orders:write' scope in the JWT token.
    """
    return await service.create_order(order, user_context=token_payload)


@router.get("/all", response_model=List[OrderOut])
async def get_orders(
    service: OrderService = Depends(get_order_service),
) -> List[OrderOut]:
    try:
        return list(service.orders.values())
    except NotFoundError as e:
        raise HTTPException(status_code=404, detail=e.message)


@router.get("/{id}", response_model=OrderOut)
async def get_order(
    id: UUID, service: OrderService = Depends(get_order_service)
) -> OrderOut:
    try:
        return service.get_order_by_id(id)
    except NotFoundError as e:
        raise HTTPException(status_code=404, detail=e.message)
