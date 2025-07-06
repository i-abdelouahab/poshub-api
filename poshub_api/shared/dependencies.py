import httpx
from fastapi import Request

from poshub_api.services.order_service import OrderService

order_service = OrderService()


def get_order_service() -> OrderService:
    return order_service


def get_http_client(request: Request) -> httpx.AsyncClient:
    return request.app.state.http
