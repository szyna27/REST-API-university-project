from sqlalchemy.orm import Session, selectinload
from fastapi import HTTPException
from app.cart.model.shopping_cart_orm import ShoppingCartORM
from app.cart.model.shopping_cart_item_orm import ShoppingCartItemORM
from app.cart.model.order_orm import OrderORM

def get_shopping_cart_by_operator(db: Session, operator_id: int) -> ShoppingCartORM | None:
    return (
        db.query(ShoppingCartORM)
        .filter(ShoppingCartORM.operator_id == operator_id)
        .options(selectinload(ShoppingCartORM.items).selectinload(ShoppingCartItemORM.product))
        .first()
    )

def create_shopping_cart(db: Session, operator_id: int) -> ShoppingCartORM:
    cart = ShoppingCartORM(operator_id=operator_id)
    db.add(cart)
    db.flush()
    return cart

def get_cart_item_by_cart_and_product(db: Session, cart_id: int, product_id: int) -> ShoppingCartItemORM | None:
    return (
        db.query(ShoppingCartItemORM)
        .filter(
            ShoppingCartItemORM.cart_id == cart_id,
            ShoppingCartItemORM.product_id == product_id,
        )
        .first()
    )

def get_cart_item_by_id(db: Session, item_id: int) -> ShoppingCartItemORM | None:
    return (
        db.query(ShoppingCartItemORM)
        .filter(ShoppingCartItemORM.id == item_id)
        .options(selectinload(ShoppingCartItemORM.product))
        .first()
    )

def list_orders_by_operator(db: Session, operator_id: int) -> list[OrderORM]:
    return (
        db.query(OrderORM)
        .filter(OrderORM.operator_id == operator_id)
        .order_by(OrderORM.created_at.desc())
        .all()
    )

def get_order_by_id(db: Session, order_id: int) -> OrderORM | None:
    return (
        db.query(OrderORM)
        .filter(OrderORM.id == order_id)
        .options(selectinload(OrderORM.items))
        .first()
    )
