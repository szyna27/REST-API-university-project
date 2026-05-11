from sqlalchemy.orm import Session, joinedload
from sqlalchemy import select

from ..model.product_orm import ProductORM
from ..data.database import Base, engine


def create_tables():
    Base.metadata.create_all(engine)


def get_all_products(db: Session):
    query = (
        select(ProductORM)
        .options(
            joinedload(ProductORM.category)
        )
    )
    result = db.execute(query)
    return result.unique().scalars().all()

def get_product_by_id(db: Session, product_id: int):
    query = (
        select(ProductORM)
        .where(ProductORM.id == product_id)
        .options(
            joinedload(ProductORM.category)
        )
    )
    result = db.execute(query)
    return result.unique().scalar_one_or_none()

def get_product_by_name(db: Session, name: str):
    query = (
        select(ProductORM)
        .where(ProductORM.name == name)
        .options(
            joinedload(ProductORM.category)
        )
    )
    result = db.execute(query)
    return result.scalar_one_or_none()

def add_product(db: Session, product: ProductORM):
    db.add(product)
    db.commit()
    db.refresh(product)
    return product

def update_product(db: Session, product: ProductORM):
    db.add(product)
    db.commit()
    db.refresh(product)
    return product

def delete_product(db: Session, product: ProductORM):
    db.delete(product)
    db.commit()
    return True