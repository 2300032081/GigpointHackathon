from datetime import datetime
from typing import Optional
from pydantic import BaseModel, Field


class TransactionCreate(BaseModel):
    product_id: str
    quantity: float = Field(gt=0)
    unit: Optional[str] = None
    price: Optional[float] = Field(default=None, ge=0)
    source: str = "MANUAL"
    language: Optional[str] = None
    raw_text: Optional[str] = None


class TransactionResponse(BaseModel):
    id: str
    product_id: str
    product_name: str
    transaction_type: str
    quantity: float
    unit: str
    price: Optional[float]
    source: str
    language: Optional[str]
    raw_text: Optional[str]
    created_at: datetime
