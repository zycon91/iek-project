import uuid
from pydantic import BaseModel
from datetime import datetime


class SubscriptionBase(BaseModel):
    user_id: uuid.UUID
    plan: str
    start_date: datetime
    end_date: datetime
    is_active: bool


class SubscriptionCreate(SubscriptionBase):
    pass


class SubscriptionUpdate(BaseModel):
    plan: str | None = None
    start_date: datetime | None = None
    end_date: datetime | None = None


class SubscriptionResponse(SubscriptionBase):
    id: uuid.UUID

    class Config:
        from_attributes = True
