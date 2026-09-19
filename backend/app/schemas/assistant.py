from typing import Optional
from pydantic import BaseModel, Field


class TextRequest(BaseModel):
    text: str = Field(min_length=1, max_length=500)
    language: Optional[str] = None


class ParseResponse(BaseModel):
    success: bool
    intent: str
    product: Optional[str] = None
    product_id: Optional[str] = None
    quantity: Optional[float] = None
    unit: Optional[str] = None
    price: Optional[float] = None
    transaction_type: Optional[str] = None
    language: str
    confidence: float
    response: Optional[str] = None
