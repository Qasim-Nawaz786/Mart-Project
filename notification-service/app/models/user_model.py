from typing import Optional
from sqlmodel import SQLModel, Field, Relationship
import enum
from sqlalchemy import Column, Enum
from datetime import datetime




# Inventory Microservice Models
class UserLogin(SQLModel, table=True):
    User_id: int | None = Field(default=None, primary_key=True)
    message: str

class UserNotification(SQLModel, table=True):
    id: int | None = Field(default=None, primary_key=True)
    user_id: int 
    message: str = Field(nullable=False)
    status: str = Field(max_length=20, default="pending")
    created_at: datetime = Field(default=datetime.now)


