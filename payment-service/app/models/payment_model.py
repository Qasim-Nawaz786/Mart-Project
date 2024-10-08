from sqlmodel import SQLModel, Field
from datetime import datetime

class PaymentToken(SQLModel, table=True):
    id: int | None = Field(default=None, primary_key=True)
    token: str = Field(nullable=False, unique=True)
    refresh_token: str | None = Field(default=None)
    expiry: int = Field(nullable=False)
    created_at: datetime = Field(default=datetime.now)

class Transaction(SQLModel, table=True):
    id: int | None = Field(default=None, primary_key=True)
    stripe_transaction_id: str = Field(nullable=False, unique=True)  # Changed to Stripe terminology
    basket_id: str = Field(nullable=False)
    amount: float = Field(nullable=False)
    customer_email: str = Field(nullable=False)
    customer_mobile: str = Field(nullable=False)
    status: str | None = Field(default=None)  # Refactored status code/message to a general status
    created_at: datetime = Field(default_factory=datetime.utcnow)
