from poshub_api.services.order_service import OrderService

order_service = OrderService()


def get_order_service() -> OrderService:
    return order_service
