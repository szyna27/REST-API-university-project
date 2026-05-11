from sqlalchemy.orm import Session
from sqlalchemy import select, desc

from ..model.product_history_orm import ProductHistoryORM


def get_product_history_by_product_id(db: Session, product_id: int):
    query = (
        select(ProductHistoryORM)
        .where(ProductHistoryORM.product_id == product_id)
        .order_by(
            desc(ProductHistoryORM.changed_at), 
            desc(ProductHistoryORM.id)
        ) 
    )
    #sortujemy względem czasu zmiany, w przypadku gdyby dwa wpisy otrzymały bardzo zbliżony znacznik czasu,
    #id rekordu pozwoli zachować odpowiednią kolejność wyników
    result = db.execute(query)
    return result.scalars().all()

def add_product_history(db: Session, history_entry: ProductHistoryORM):
    db.add(history_entry)
    db.commit()
    db.refresh(history_entry)
    return history_entry