import uuid
from sqlalchemy.orm import Session
from app.cart.data.cart_repository import get_shopping_cart_by_operator
from app.cart.model.cart_schema import OrderItemResponse, OrderResponse
from app.cart.model.order_item_orm import OrderItemORM
from app.cart.model.order_orm import OrderORM
from app.cart.service.cart_exceptions import CartValidationError
from app.cart.service.confirm_order_command import ConfirmOrderCommand
from app.cart.service.cart_service import _calculate_total_price

def handle_confirm_order(
    db: Session, command: ConfirmOrderCommand
) -> OrderResponse:
    cart = get_shopping_cart_by_operator(db, command.operator_id)
    if cart is None or not cart.items:
        raise CartValidationError("Nie można zatwierdzić pustego koszyka.")

    total_price = _calculate_total_price(cart.items)
    
    order = OrderORM(
        operator_id=command.operator_id,
        assignment_number=str(uuid.uuid4()),
        status="CONFIRMED",
        products_count=len(cart.items),
        total_price=total_price,
    )
    db.add(order)
    db.flush()

    for item in cart.items:
        if item.product is not None:
            order_item = OrderItemORM(
                order_id=order.id,
                product_id=item.product_id,
                quantity=1,
                price=item.product.price,
            )
            db.add(order_item)

    db.delete(cart)
    db.commit()

    return OrderResponse(
        id=order.id,
        assignment_number=order.assignment_number,
        status=order.status,
        products_count=order.products_count,
        total_price=float(order.total_price),
        items=[
            OrderItemResponse(
                id=item.id,
                product_id=item.product_id,
                quantity=item.quantity,
                price=float(item.price),
                created_at=item.created_at,
            )
            for item in order.items
        ],
        created_at=order.created_at,
    )
