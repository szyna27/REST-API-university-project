from pydantic import BaseModel, ConfigDict
from datetime import datetime

class ShoppingCartItemCreate(BaseModel):
    product_id: int
    quantity: int = 1

class ShoppingCartItemUpdate(BaseModel):
    quantity: int

class ShoppingCartProductResponse(BaseModel):
    id: int
    name: str
    price: float
    description: str

    model_config = ConfigDict(
        from_attributes=True,
    )

class ShoppingCartItemResponse(BaseModel):
    id: int
    quantity: int
    product: ShoppingCartProductResponse
    created_at: datetime

    model_config = ConfigDict(
        from_attributes=True,
    )
    
class ShoppingCartResponse(BaseModel):
    id: int
    operator_id: int
    items: list[ShoppingCartItemResponse]
    products_count: int
    total_price: float
    created_at: datetime
    updated_at: datetime
    
    model_config = ConfigDict(
        from_attributes=True,
    )

class OrderItemResponse(BaseModel):
    id: int
    product_id: int
    product_name: str
    quantity: int
    price: float
    
    model_config = ConfigDict(
        from_attributes=True,
    )

class OrderResponse(BaseModel):
    id: int
    operator_id: int
    order_number: str
    status: str
    products_count: int
    total_price: float
    created_at: datetime
    items: list[OrderItemResponse]
    
    model_config = ConfigDict(
        from_attributes=True,
    )

class OrderListItemResponse(BaseModel):
    id: int
    order_number: str
    status: str
    products_count: int
    total_price: float
    created_at: datetime
    
    model_config = ConfigDict(
        from_attributes=True,
    )
