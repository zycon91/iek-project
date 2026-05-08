import uuid
from pydantic import BaseModel
from datetime import datetime


class PurchaseCreate(BaseModel):
    movie_id: uuid.UUID


class PurchaseResponse(BaseModel):
    id: uuid.UUID
    user_id: uuid.UUID
    movie_id: uuid.UUID
    amount_paid: int
    purchased_at: datetime

    class Config:
        from_attributes = True
