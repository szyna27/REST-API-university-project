from sqlalchemy.orm import Session
from sqlalchemy import select

from ..model.forbidden_name_orm import ForbiddenNameORM


def get_forbidden_name_by_id(forbidden_name_id: int, db: Session):
    query = select(ForbiddenNameORM).where(ForbiddenNameORM.id == forbidden_name_id)
    result = db.execute(query)
    return result.scalar_one_or_none()

def get_all_forbidden_names(db: Session):
    query = select(ForbiddenNameORM)
    result = db.execute(query)
    return result.scalars().all()
