import uuid
from pydantic import BaseModel
from datetime import datetime


class RentalBase(BaseModel):
    user_id: uuid.UUID
    movie_id: uuid.UUID
    start_date: datetime
    end_date: datetime


class RentalCreate(RentalBase):
    pass


class RentalUpdate(BaseModel):
    start_date: datetime | None = None
    end_date: datetime | None = None


class RentalResponse(RentalBase):
    id: uuid.UUID

    class Config:
        from_attributes = True
