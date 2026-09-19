from datetime import datetime
from typing import Optional
from pydantic import BaseModel, ConfigDict, Field


class ProductBase(BaseModel):
    name: str = Field(min_length=1, max_length=120)
    category: str = Field(default="General", max_length=80)
    unit: str
    quantity: float = Field(default=0, ge=0)
    price: Optional[float] = Field(default=None, ge=0)
    low_stock_threshold: float = Field(default=10, ge=0)
    target_stock: float = Field(default=20, ge=0)


class ProductCreate(ProductBase):
    pass


class ProductUpdate(ProductBase):
    pass


class ProductResponse(ProductBase):
    id: str
    created_at: datetime
    updated_at: datetime
    status: str
    reorder_quantity: float

    model_config = ConfigDict(from_attributes=True)
