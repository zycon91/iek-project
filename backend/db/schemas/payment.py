import datetime
import uuid
from pydantic import BaseModel

class PaymentResponse(BaseModel):
    id: uuid.UUID
    user_id: uuid.UUID
    stripe_checkout_session_id: str
    stripe_payment_intent_id: str
    amount: int
    currency: str
    status: str
    payment_type: str
    referrence_id: uuid.UUID | None
    created_at: datetime

    class Config:
        from_attributes = True
