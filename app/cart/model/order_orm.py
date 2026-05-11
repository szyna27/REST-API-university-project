from datetime import datetime
from sqlalchemy import DateTime, ForeignKey, Integer, String, Numeric
from sqlalchemy.orm import Mapped, mapped_column, relationship
from app.REST.data.database import Base

class OrderORM(Base):
    __tablename__ = "orders"

    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    operator_id: Mapped[int] = mapped_column(
        Integer,
        ForeignKey("operators.id", ondelete="CASCADE"),
        nullable=False,
    )
    assignment_number: Mapped[str] = mapped_column(
        String,
        unique=True,
        nullable=False,
    )
    status: Mapped[str] = mapped_column(
        String,
        default="PENDING",
        nullable=False,
    )
    products_count: Mapped[int] = mapped_column(Integer, default=0, nullable=False)
    total_price: Mapped[float] = mapped_column(Numeric(10, 2), default=0.0, nullable=False)
    created_at: Mapped[datetime] = mapped_column(
        DateTime,
        nullable=False,
        default=datetime.now,
    )

    items = relationship(
        "OrderItemORM",
        cascade="all, delete-orphan",
        lazy="selectin",
    )
