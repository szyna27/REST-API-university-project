from sqlalchemy.orm import Mapped, mapped_column
from sqlalchemy import Integer, String, DateTime, JSON, func
from datetime import datetime

from ..data.database import Base


class ProductHistoryORM(Base):
    __tablename__ = "products_history"

    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    product_id: Mapped[int] = mapped_column(
        Integer,
        nullable=False,
        index=True  
    )
    action: Mapped[str] = mapped_column(String, nullable=False)
    previous_state: Mapped[dict] = mapped_column(JSON, nullable=False)
    current_state: Mapped[dict] = mapped_column(JSON, nullable=False)
    changed_at: Mapped[datetime] = mapped_column(
        DateTime,
        nullable=False,
        server_default=func.now()
    )