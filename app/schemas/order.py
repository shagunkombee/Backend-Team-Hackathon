"""
Order Schemas
"""
from pydantic import BaseModel
from datetime import datetime
from typing import List, Optional
from app.models.order import OrderStatus


class OrderItemCreate(BaseModel):
    """Order item creation schema"""
    product_id: int
    quantity: int
    price: float


class OrderItemResponse(BaseModel):
    """Order item response schema"""
    id: int
    product_id: int
    quantity: int
    price: float
    created_at: datetime
    
    class Config:
        from_attributes = True


class OrderCreate(BaseModel):
    """Order creation schema"""
    items: List[OrderItemCreate]
    shipping_address: Optional[str] = None


class OrderResponse(BaseModel):
    """Order response schema"""
    id: int
    user_id: int
    status: OrderStatus
    total_amount: float
    shipping_address: Optional[str]
    created_at: datetime
    updated_at: datetime
    items: List[OrderItemResponse]
    
    class Config:
        from_attributes = True


