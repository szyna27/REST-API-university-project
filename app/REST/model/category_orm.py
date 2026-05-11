from sqlalchemy.orm import Mapped, mapped_column
from sqlalchemy import Integer, Numeric, String, Text

from ..data.database import Base


class CategoryORM(Base):
    __tablename__ = "categories"

    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    name: Mapped[str] = mapped_column(String, unique=True, nullable=False)
    description: Mapped[str | None] = mapped_column(Text, nullable=True)
    min_price: Mapped[float | None] = mapped_column(Numeric(10, 2), nullable=True)
    max_price: Mapped[float | None] = mapped_column(Numeric(10, 2), nullable=True)
