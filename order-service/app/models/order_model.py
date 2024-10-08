from typing import Optional
from sqlmodel import SQLModel, Field, Relationship
import enum
from sqlalchemy import Column, Enum
from datetime import datetime



# class OrderItem(SQLModel, table=True):
#     order_id: int | None = Field(default=None, primary_key=True)
#     name: str
#     weight: float
#     price: int
#     color: str

class Order(SQLModel, table=True):
    id: Optional[int]  = Field(default=None, primary_key=True)
    user_id: int 
    product_id: int
    variant_id: int | None = None   
    quantity: int
    total_price: float 
    created_at: datetime = Field(default_factory=lambda: datetime.now())

class UpdateOrderitem(SQLModel):
    name: str | None = None
    weight: float | None = None
    price: int | None = None
    color: str | None = None
