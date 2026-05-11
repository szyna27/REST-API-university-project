import uuid
from sqlalchemy.orm import Session
from app.cart.data.cart_repository import (
    add_order,
    add_order_item,
    clear_shopping_cart,
    get_or_create_shopping_cart
)
from app.cart.model.cart_schema import OrderResponse
from app.cart.model.order_item_orm import OrderItemORM
from app.cart.model.order_orm import OrderORM
from app.cart.model.shopping_cart_orm import ShoppingCartORM
from app.cart.service.cart_exceptions import CartValidationError
from app.cart.service.confirm_order_command import ConfirmOrderCommand


def _get_valid_cart(
    db: Session, 
    operator_id: int
) -> ShoppingCartORM:
    cart = get_or_create_shopping_cart(db, operator_id)
    
    if not cart.items:
        raise CartValidationError("Nie można potwierdzić zamówienia. Koszyk jest pusty.")
    
    return cart


def _calculate_total_cart_positions(shopping_cart: ShoppingCartORM) -> int:
    return len(shopping_cart.items)


def _calculate_total_price(shopping_cart: ShoppingCartORM) -> float:
    total = 0.0
    for item in shopping_cart.items:
        total += float(item.price) * item.quantity
    return total


def _create_order(
    db: Session,
    operator_id: int,
    products_count: int,
    total_price: float,
) -> OrderORM:
    order = OrderORM(
        operator_id=operator_id,
        order_number=str(uuid.uuid4()),
        status="CONFIRMED",
        products_count=products_count,
        total_price=total_price,
    )

    order = add_order(db, order)

    order.order_number = uuid.uuid4().hex[:8].upper()  # Generowanie krótkiego, unikalnego numeru zamówienia

    db.add(order)
    db.commit()
    db.refresh(order)

    return order


def _create_order_items(
    db: Session,
    order_id: int,
    shopping_cart: ShoppingCartORM,
) -> None:
    for cart_item in shopping_cart.items:
        order_item = OrderItemORM(
            order_id=order_id,
            product_id=cart_item.product_id,
            product_name=cart_item.product.name if cart_item.product else "Unknown Product",
            quantity=cart_item.quantity,
            price=cart_item.price,
        )

        add_order_item(db, order_item)


def _build_order_response(
    order: OrderORM
) -> OrderResponse:
    return OrderResponse(
        id=order.id,
        operator_id=order.operator_id,
        order_number=order.order_number,
        status=order.status,
        products_count=order.products_count,
        total_price=float(order.total_price),
        created_at=order.created_at,
        items=order.items,
    )


def handle_confirm_order(
    db: Session, command: ConfirmOrderCommand
) -> OrderResponse:
    cart = _get_valid_cart(db, command.operator_id)

    total_price = _calculate_total_price(cart)
    total_products = _calculate_total_cart_positions(cart)
    
    order = _create_order(
        db=db,
        operator_id=command.operator_id,
        products_count=total_products,
        total_price=total_price,
    )

    _create_order_items(db, order.id, cart)

    clear_shopping_cart(db, cart.id)

    return _build_order_response(order)