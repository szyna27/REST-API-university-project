from sqlalchemy.orm import Session

from app.cart.data.cart_repository import get_order_by_id_and_operator_id, get_orders_by_operator_id
from app.cart.model.cart_schema import OrderListItemResponse, OrderResponse
from app.cart.service.cart_exceptions import OrderNotFoundError

def list_orders(
    db: Session,
    operator_id: int,
) -> list[OrderListItemResponse]:
    orders = get_orders_by_operator_id(db, operator_id)

    return [OrderListItemResponse.model_validate(order) for order in orders]

def get_order_details(
    db: Session,
    operator_id: int,
    order_id: int,
) -> OrderResponse:
    order = get_order_by_id_and_operator_id(db, order_id, operator_id)

    if order is None:
        raise OrderNotFoundError(f"Zamówienie o id {order_id} nie zostało znalezione.")