from datetime import datetime
from sqlalchemy import DateTime, ForeignKey, Integer, UniqueConstraint
from sqlalchemy.orm import Mapped, mapped_column, relationship
from app.REST.data.database import Base

class ShoppingCartItemORM(Base):
    __tablename__ = "shopping_cart_items"
    __table_args__ = (
        UniqueConstraint(
            "cart_id",
            "product_id",
            name="uq_shopping_cart_product",
        ),
    )

    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    cart_id: Mapped[int] = mapped_column(
        Integer,
        ForeignKey("shopping_carts.id", ondelete="CASCADE"),
        nullable=False,
    )
    product_id: Mapped[int] = mapped_column(
        Integer,
        ForeignKey("products.id", ondelete="CASCADE"),
        nullable=False,
    )
    created_at: Mapped[datetime] = mapped_column(
        DateTime,
        nullable=False,
        default=datetime.now,
    )

    product = relationship("ProductORM", lazy="joined")
