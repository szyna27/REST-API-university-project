from sqlalchemy.orm import Mapped, mapped_column
from sqlalchemy import Integer, String, Text

from ..data.database import Base


class ForbiddenNameORM(Base):
    __tablename__ = "forbidden_names"

    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    name: Mapped[str] = mapped_column(String, unique=True, nullable=False)
    reason: Mapped[str | None] = mapped_column(Text, nullable=True)
