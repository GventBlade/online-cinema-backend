from datetime import datetime
from decimal import Decimal
from typing import List, Optional
from pydantic import BaseModel, ConfigDict
from app.models import PaymentStatus


class PaymentItemResponse(BaseModel):
    id: int
    order_item_id: int
    price_at_payment: Decimal

    model_config = ConfigDict(from_attributes=True)


class PaymentResponse(BaseModel):
    id: int
    order_id: int
    amount: Decimal
    status: PaymentStatus
    external_payment_id: Optional[str]
    created_at: datetime
    items: List[PaymentItemResponse]

    model_config = ConfigDict(from_attributes=True)


class PaymentCreate(BaseModel):
    order_id: int