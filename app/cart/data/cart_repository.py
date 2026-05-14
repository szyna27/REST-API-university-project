from sqlalchemy import select, delete
from sqlalchemy.orm import Session, selectinload

from app.cart.model.order_item_orm import OrderItemORM
from app.cart.model.shopping_cart_orm import ShoppingCartORM
from app.cart.model.shopping_cart_item_orm import ShoppingCartItemORM
from app.cart.model.order_orm import OrderORM


def get_shopping_cart_by_operator(
    db: Session, 
    operator_id: int
) -> ShoppingCartORM | None:
    query = (
        select(ShoppingCartORM)
        .where(ShoppingCartORM.operator_id == operator_id)
        .options(
            selectinload(ShoppingCartORM.items)
            .selectinload(ShoppingCartItemORM.product)
        )
    )
    result = db.execute(query).scalars().first()
    return result    


def create_shopping_cart(
    db: Session, 
    operator_id: int
) -> ShoppingCartORM:
    cart = ShoppingCartORM(operator_id=operator_id)

    db.add(cart)
    db.commit()
    db.refresh(cart)

    return cart


def get_or_create_shopping_cart(
    db: Session,
    operator_id: int
) -> ShoppingCartORM:
    cart = get_shopping_cart_by_operator(db, operator_id)
    
    if cart is not None:
        return cart
    
    return create_shopping_cart(db, operator_id)


def get_cart_item_by_cart_and_product(
    db: Session, 
    cart_id: int, 
    product_id: int
) -> ShoppingCartItemORM | None:
    query = (
        select(ShoppingCartItemORM)
        .where(
            ShoppingCartItemORM.cart_id == cart_id,
            ShoppingCartItemORM.product_id == product_id,
        )
        .options(selectinload(ShoppingCartItemORM.product))
    )
    result = db.execute(query).scalars().first()
    return result


def get_cart_item_by_id(
    db: Session, 
    item_id: int
) -> ShoppingCartItemORM | None:
    query = (
        select(ShoppingCartItemORM)
        .where(ShoppingCartItemORM.id == item_id)
        .options(selectinload(ShoppingCartItemORM.product))
    )
    result = db.execute(query).scalars().first()
    return result


def add_shopping_cart_item(
    db: Session, 
    cart_id: int, 
    product_id: int,
    quantity: int = 1
) -> ShoppingCartItemORM:
    item = ShoppingCartItemORM(cart_id=cart_id, product_id=product_id, quantity=quantity)
    db.add(item)
    db.commit()
    db.refresh(item)
    return item


def delete_shopping_cart_item(
    db: Session, 
    item_id: int
) -> None:
    query = delete(ShoppingCartItemORM).where(ShoppingCartItemORM.id == item_id)
    db.execute(query)
    db.commit()


def clear_shopping_cart(
    db: Session,
    cart_id: int
) -> None:
    query = delete(ShoppingCartItemORM).where(ShoppingCartItemORM.cart_id == cart_id)
    db.execute(query)
    db.commit()


def add_order(
    db: Session,
    order: OrderORM
) -> OrderORM:
    db.add(order)
    db.commit()
    db.refresh(order)
    
    return order


def save_order(
    db: Session,
    order: OrderORM
) -> None:
    db.add(order)
    db.commit()
    db.refresh(order)

    return order


def add_order_item(
    db: Session,
    order_item: OrderItemORM
) -> OrderItemORM:
    db.add(order_item)
    db.commit()
    db.refresh(order_item)

    return order_item


def get_orders_by_operator_id(
    db: Session,
    operator_id: int
) -> list[OrderORM]:
    query = (
        select(OrderORM)
        .where(OrderORM.operator_id == operator_id)
        .order_by(OrderORM.created_at.desc())
    )
    result = db.execute(query).scalars().all()
    return list(result)


def get_order_by_id_and_operator_id(
    db: Session,
    order_id: int,
    operator_id: int
) -> OrderORM | None:
    query = (
        select(OrderORM)
        .where(
            OrderORM.id == order_id,
            OrderORM.operator_id == operator_id,
        )
        .options(selectinload(OrderORM.items))
    )
    result = db.execute(query).scalars().first()
    return result
