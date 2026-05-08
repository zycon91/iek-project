import uuid
from pydantic import BaseModel
from datetime import date


class SubscriptionBase(BaseModel):
    user_id: uuid.UUID
    plan: str
    start_date: date
    end_date: date
    is_active: bool


class SubscriptionCreate(SubscriptionBase):
    pass


class SubscriptionUpdate(BaseModel):
    plan: str | None = None
    start_date: date | None = None
    end_date: date | None = None


class SubscriptionResponse(SubscriptionBase):
    id: uuid.UUID

    class Config:
        from_attributes = True
