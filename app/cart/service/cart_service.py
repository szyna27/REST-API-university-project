from datetime import datetime
from sqlalchemy.orm import Session
from app.REST.data.products_repository import get_product_by_id
from app.cart.data.cart_repository import (
    add_shopping_cart_item,
    delete_shopping_cart_item,
    get_cart_item_by_cart_and_product,
    get_cart_item_by_id,
    get_or_create_shopping_cart,
    get_order_by_id_and_operator_id,
    get_orders_by_operator_id,
)
from app.cart.model.shopping_cart_orm import ShoppingCartORM
from app.cart.model.cart_schema import (
    ShoppingCartItemCreate, 
    ShoppingCartResponse, 
    ShoppingCartItemResponse, 
    OrderListItemResponse, 
    OrderResponse,
)
from app.cart.service.cart_exceptions import (
    CartConflictError, 
    CartNotFoundError,
)

def _calculate_total_price(shopping_cart: ShoppingCartORM) -> float:
    total = 0.0

    for item in shopping_cart.items:
        if item.product is not None:
            total += float(item.product.price)

    return total

def _build_shopping_cart_response(shopping_cart: ShoppingCartORM) -> ShoppingCartResponse:
    return ShoppingCartResponse(
        id=shopping_cart.id,
        items=[
            ShoppingCartItemResponse.model_validate(item)
            for item in shopping_cart.items
        ],
        total_price=_calculate_total_price(shopping_cart),
        created_at=shopping_cart.created_at,
        updated_at=shopping_cart.updated_at,
    )

def get_current_shopping_cart(
    db: Session,
    operator_id: int,
) -> ShoppingCartResponse:
    shopping_cart = get_or_create_shopping_cart(db, operator_id)

    return _build_shopping_cart_response(shopping_cart)

def add_product_to_shopping_cart(
    db: Session,
    operator_id: int,
    payload: ShoppingCartItemCreate,
) -> ShoppingCartResponse:
    shopping_cart = get_or_create_shopping_cart(db, operator_id)

    product = get_product_by_id(db, payload.product_id)
    if product is None:
        raise CartNotFoundError("Produkt o podanym identyfikatorze nie istnieje.")

    existing_item = get_cart_item_by_cart_and_product(
        db=db,
        cart_id=shopping_cart.id,
        product_id=payload.product_id,
    )
    if existing_item is not None:
        raise CartConflictError("Ten produkt jest już dodany do koszyka.")

    add_shopping_cart_item(
        db=db,
        cart_id=shopping_cart.id,
        product_id=payload.product_id,
        quantity=payload.quantity,
    )

    shopping_cart.updated_at = datetime.now()
    db.add(shopping_cart)
    db.commit()
    db.refresh(shopping_cart)
    refreshed_shopping_cart = get_or_create_shopping_cart(db, operator_id)
    return _build_shopping_cart_response(refreshed_shopping_cart)

def remove_product_from_shopping_cart(
    db: Session,
    operator_id: int,
    item_id: int,
) -> bool:
    shopping_cart = get_or_create_shopping_cart(db, operator_id)

    item = get_cart_item_by_id(db, item_id)
    if item is None:
        raise CartNotFoundError("Pozycja w koszyku nie istnieje.")

    if item.cart_id != shopping_cart.id:
        raise CartNotFoundError("Pozycja nie należy do koszyka aktualnego operatora.")

    delete_shopping_cart_item(db, item)
    shopping_cart.updated_at = datetime.now()
    db.add(shopping_cart)
    db.commit()
    return True

def list_orders(
    db: Session,
    operator_id: int,
) -> list[OrderListItemResponse]:
    orders = get_orders_by_operator_id(
        db=db,
        operator_id=operator_id,
    )

    return [
        OrderListItemResponse.model_validate(order)
        for order in orders
    ]


def get_order_details(
    db: Session,
    operator_id: int,
    order_id: int,
) -> OrderResponse:
    order = get_order_by_id_and_operator_id(
        db=db,
        order_id=order_id,
        operator_id=operator_id,
    )

    if order is None:
        raise CartNotFoundError("Zamówienie nie istnieje.")

    return OrderResponse.model_validate(order)