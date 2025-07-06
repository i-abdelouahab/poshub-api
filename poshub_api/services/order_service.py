"""This class represents the Order service."""

from datetime import datetime
from uuid import UUID, uuid4

from poshub_api.domain.models import OrderIn, OrderOut
from poshub_api.shared.exceptions import NotFoundError


class OrderService:
    """This class represents the Order service."""

    def __init__(self):
        """Initialize the Order service."""
        self.orders = {}

    def create_order(self, order_in: OrderIn) -> OrderOut:
        """Create a new order."""
        order = OrderOut(
            order=uuid4(),
            created_at=datetime.utcnow(),
            nom_client=order_in.customer_name,
            montant=order_in.total_amount,
            devise=order_in.currency,
        )
        self.orders[order.order_id] = order
        return order

    def get_order_by_id(self, order_id: UUID) -> OrderOut:
        """Return the order by id."""
        order = self.orders.get(order_id)
        if not order:
            raise NotFoundError(f"Order {order_id} not found")
        else:
            return order
