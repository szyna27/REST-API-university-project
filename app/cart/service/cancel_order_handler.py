from sqlalchemy.orm import Session

from app.cart.data.cart_repository import (
    get_order_by_id_and_operator_id,
    save_order,
)
from app.cart.model.cart_schema import OrderResponse
from app.cart.model.order_status import OrderStatus
from app.cart.service.cart_exceptions import (
    OrderNotFoundError,
    CartValidationError,
)
from app.cart.service.order_state_machine import validate_status_transition
from app.cart.service.cancel_order_command import CancelOrderCommand


def handle_cancel_order(
    db: Session,
    command: CancelOrderCommand,
) -> OrderResponse:
    order = get_order_by_id_and_operator_id(
        db=db,
        order_id=command.order_id,
        operator_id=command.operator_id,
    )

    if order is None:
        raise OrderNotFoundError("Zamówienie nie istnieje.")

    validate_status_transition(
        current_status=order.status,
        new_status=OrderStatus.CANCELLED,
    )
    
    order.status = OrderStatus.CANCELLED
    order = save_order(db, order)

    return OrderResponse.model_validate(order)
