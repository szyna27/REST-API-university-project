from pydantic import BaseModel
from ..model.category_schema import Category


class ProductCreate(BaseModel):
    name : str
    price: float
    count: int
    description: str
    category_id: int


class ProductUpdate(BaseModel):
    name: str | None = None
    price: float | None = None
    count: int | None = None
    description: str | None = None
    category_id: int | None = None


class Product(BaseModel):
    id: int
    name: str
    price: float
    count: int
    description: str
    category: Category

    class Config:
        from_attributes = True