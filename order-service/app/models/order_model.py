from typing import Optional
from sqlmodel import SQLModel, Field, Relationship
import enum
from sqlalchemy import Column, Enum
from datetime import datetime

class OrderStatus(enum.Enum):
    Pending = "Pending"
    Confirmed = "Confirmed"
    Shipped = "Shipped"
    Delivered = "Delivered"
    Canceled = "Canceled"


# Inventory Microservice Models
class Order(SQLModel, table=True):
    id: int | None = Field(default=None, primary_key=True)
    user_id: int 
    status: OrderStatus = Field(sa_column=Column(Enum(OrderStatus)))
    product_id: Optional[int] = Field(default=None, foreign_key="OrderItem.order_id")
    variant_id: int | None = None   
    quantity: int
    total_price: float 
    created_at: datetime = Field(default=datetime.now)


class OrderItem(SQLModel, table=True):
    order_id: int | None = Field(default=None, primary_key=True)
    name: str
    weight: float
    price: int
    color: str

class UpdateOrderitem(SQLModel):
    name: str | None = None
    weight: float | None = None
    price: int | None = None
    color: str | None = None


