from http.client import HTTPException
from uuid import UUID

from fastapi import APIRouter, Depends

from poshub_api.domain.models import OrderIn, OrderOut
from poshub_api.services.order_service import OrderService
from poshub_api.shared.dependencies import get_order_service

router = APIRouter(prefix="/orders", tags=["orders"])


@router.post("/order", response_model=OrderOut)
async def create_order(
    order: OrderIn, service: OrderService = Depends(get_order_service)
):
    return service.create(order)


@router.get("/{id}", response_model=OrderOut)
async def get_order(
    order_id: UUID, service: OrderService = Depends(get_order_service)
) -> OrderOut:
    try:
        service.get_order_by_id(order_id)
    except OrderOut.DoesNotExist as e:
        raise HTTPException(status_code=404, detail=e.message)
