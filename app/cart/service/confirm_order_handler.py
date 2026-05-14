from datetime import datetime
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


def _generate_order_number(order_id: int) -> str:
    """
    Generuje numer w formacie "ZAM-YYYYMMDD-000001".
    """
    date_part = datetime.now().strftime("%Y%m%d")
    return f"ZAM-{date_part}-{order_id:06d}"



def _get_valid_cart(
    db: Session, 
    operator_id: int
) -> ShoppingCartORM:
    cart = get_or_create_shopping_cart(db, operator_id)
    
    if not cart.items:
        raise CartValidationError("Nie można potwierdzić zamówienia. Koszyk jest pusty.")

    for item in cart.items:
        if item.product and item.product.count < item.quantity:
            raise CartValidationError(
                f"Produkt '{item.product.name}' ma niewystarczającą ilość w magazynie "
                f"(dostępne: {item.product.count})."
            )
    
    return cart


def _calculate_total_cart_positions(shopping_cart: ShoppingCartORM) -> int:
    return len(shopping_cart.items)


def _calculate_total_price(shopping_cart: ShoppingCartORM) -> float:
    total = 0.0
    for item in shopping_cart.items:
        if item.product is not None:
            total += float(item.product.price) * item.quantity
    return total


def _create_order(
    db: Session,
    operator_id: int,
    products_count: int,
    total_price: float,
) -> OrderORM:
    order = OrderORM(
        operator_id=operator_id,
        order_number="TEMP",
        status="CONFIRMED",
        products_count=products_count,
        total_price=total_price,
    )

    order = add_order(db, order)

    order.order_number = _generate_order_number(order.id)

    db.add(order)
    db.commit()
    db.refresh(order)

    return order


def _create_order_items(
    db: Session,
    order_id: int,
    shopping_cart: ShoppingCartORM,
) -> None:
    for item in shopping_cart.items:
        order_item = OrderItemORM(
            order_id=order_id,
            product_id=item.product_id,
            product_name=item.product.name,
            quantity=item.quantity,
            price=item.product.price
        )
        
        if item.product:
            item.product.count -= item.quantity
            db.add(item.product)

        add_order_item(db, order_item)


def _build_order_response(
    order: OrderORM
) -> OrderResponse:
    return OrderResponse.model_validate(order)


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

    db.commit()
    db.refresh(order)

    return _build_order_response(order)