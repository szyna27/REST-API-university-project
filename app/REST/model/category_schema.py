from pydantic import BaseModel, ConfigDict


class Category(BaseModel):
    id: int
    name: str
    description: str
    min_price: float
    max_price: float

    model_config = ConfigDict(
        from_attributes=True,
    )
