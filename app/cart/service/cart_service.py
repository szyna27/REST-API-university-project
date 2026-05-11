from sqlalchemy.orm import Session
from app.cart.data.cart_repository import (
    create_shopping_cart,
    get_cart_item_by_cart_and_product,
    get_cart_item_by_id,
    get_order_by_id,
    get_shopping_cart_by_operator,
    list_orders_by_operator,
)
from app.cart.model.cart_schema import CartItemCreate, CartResponse, CartItemResponse, CartProductResponse, OrderListItemResponse, OrderResponse, OrderItemResponse
from app.cart.model.shopping_cart_item_orm import ShoppingCartItemORM
from app.cart.service.cart_exceptions import CartConflictError, CartNotFoundError, CartValidationError
from app.REST.data.products_repository import get_product_by_id

def _calculate_total_price(items: list[ShoppingCartItemORM]) -> float:
    total = 0.0
    for item in items:
        if item.product is not None:
            total += float(item.product.price)
    return total

def get_current_shopping_cart(db: Session, operator_id: int) -> CartResponse:
    cart = get_shopping_cart_by_operator(db, operator_id)
    if cart is None:
        cart = create_shopping_cart(db, operator_id)
        db.commit()

    return CartResponse(
        items=[
            CartItemResponse(
                id=item.id,
                product=CartProductResponse(
                    id=item.product.id,
                    name=item.product.name,
                    price=float(item.product.price),
                    description=item.product.description,
                ),
                created_at=item.created_at,
            )
            for item in cart.items
            if item.product is not None
        ],
        products_count=len(cart.items),
        total_price=_calculate_total_price(cart.items),
    )

def add_product_to_shopping_cart(
    db: Session, operator_id: int, payload: CartItemCreate
) -> CartResponse:
    product = get_product_by_id(db, payload.product_id)
    if product is None:
        raise CartNotFoundError("Produkt o podanym identyfikatorze nie istnieje.")

    cart = get_shopping_cart_by_operator(db, operator_id)
    if cart is None:
        cart = create_shopping_cart(db, operator_id)
    
    existing_item = get_cart_item_by_cart_and_product(
        db=db,
        cart_id=cart.id,
        product_id=payload.product_id,
    )
    if existing_item is not None:
        raise CartConflictError("Ten produkt jest już dodany do koszyka.")

    new_item = ShoppingCartItemORM(
        cart_id=cart.id,
        product_id=payload.product_id,
    )
    db.add(new_item)
    db.commit()

    return get_current_shopping_cart(db, operator_id)

def remove_product_from_shopping_cart(
    db: Session, operator_id: int, item_id: int
) -> None:
    cart = get_shopping_cart_by_operator(db, operator_id)
    if cart is None:
        raise CartNotFoundError("Koszyk nie istnieje.")

    item = get_cart_item_by_id(db, item_id)
    if item is None or item.cart_id != cart.id:
        raise CartNotFoundError("Element koszyka nie istnieje.")

    db.delete(item)
    db.commit()

def list_operator_orders(db: Session, operator_id: int) -> list[OrderListItemResponse]:
    orders = list_orders_by_operator(db, operator_id)
    return [
        OrderListItemResponse(
            id=o.id,
            assignment_number=o.assignment_number,
            status=o.status,
            products_count=o.products_count,
            total_price=float(o.total_price),
            created_at=o.created_at,
        )
        for o in orders
    ]

def get_order_details(db: Session, operator_id: int, order_id: int) -> OrderResponse:
    order = get_order_by_id(db, order_id)
    if order is None or order.operator_id != operator_id:
        raise CartNotFoundError("Zamówienie nie zostało znalezione.")

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
