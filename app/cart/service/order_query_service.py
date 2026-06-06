from sqlalchemy.orm import Session

from app.cart.data.cart_repository import get_order_by_id_and_operator_id, get_orders_by_operator_id
from app.cart.model.cart_schema import OrderListItemResponse, OrderResponse, OrderListItemResponse
from app.cart.model.order_status import OrderStatus
from app.cart.service.cart_exceptions import OrderNotFoundError

def get_dashboard_summary(
    db: Session,
    operator_id: int,
) -> dict:
    orders = get_orders_by_operator_id(db, operator_id)

    total_orders = len(orders)
    pending_orders = len([o for o in orders if o.status == OrderStatus.PENDING])
    completed_orders = len([o for o in orders if o.status == OrderStatus.COMPLETED])
    cancelled_orders = len([o for o in orders if o.status == OrderStatus.CANCELLED])
    
    # Sort orders by creation date descending to get the last order, or assume they are returned in order.
    # We will just take the first if it's sorted, or sort it to be sure.
    sorted_orders = sorted(orders, key=lambda o: o.created_at, reverse=True)
    last_order = OrderListItemResponse.model_validate(sorted_orders[0]).model_dump() if sorted_orders else None
    recent_orders = [OrderListItemResponse.model_validate(o).model_dump() for o in sorted_orders[:5]]

    return {
        "total_orders": total_orders,
        "pending_orders": pending_orders,
        "completed_orders": completed_orders,
        "cancelled_orders": cancelled_orders,
        "last_order": last_order,
        "recent_orders": recent_orders,
    }

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
        
    return OrderResponse.model_validate(order)