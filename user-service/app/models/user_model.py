from sqlmodel import SQLModel, Field, Relationship
from datetime import datetime

# user Microservice Models

class User(SQLModel, table = True):
    id: int | None = Field(primary_key=True)
    username: str = Field(max_length=50, unique=True, nullable=False)
    email: str = Field(unique=True, nullable=False, max_length=100)
    password: str = Field(nullable=False, max_length=255)
    created_at: datetime = Field(default=datetime.now)
    



