from pydantic import BaseModel


class Category(BaseModel):
    id: int
    name: str
    description: str
    min_price: float
    max_price: float

    class Config:
        from_attributes = True
