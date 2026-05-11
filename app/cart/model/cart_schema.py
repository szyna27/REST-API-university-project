from pydantic import BaseModel
from datetime import datetime

class CartItemCreate(BaseModel):
    product_id: int

class CartProductResponse(BaseModel):
    id: int
    name: str
    price: float
    description: str

class CartItemResponse(BaseModel):
    id: int
    product: CartProductResponse
    created_at: datetime
    
class CartResponse(BaseModel):
    items: list[CartItemResponse]
    products_count: int
    total_price: float

class OrderItemResponse(BaseModel):
    id: int
    product_id: int
    quantity: int
    price: float
    created_at: datetime

class OrderResponse(BaseModel):
    id: int
    assignment_number: str
    status: str
    products_count: int
    total_price: float
    items: list[OrderItemResponse]
    created_at: datetime

class OrderListItemResponse(BaseModel):
    id: int
    assignment_number: str
    status: str
    products_count: int
    total_price: float
    created_at: datetime
