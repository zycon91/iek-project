import uuid
from pydantic import BaseModel
from datetime import date


class RentalBase(BaseModel):
    user_id: uuid.UUID
    movie_id: uuid.UUID
    start_date: date
    end_date: date


class RentalCreate(RentalBase):
    pass


class RentalUpdate(BaseModel):
    start_date: date | None = None
    end_date: date | None = None


class RentalResponse(RentalBase):
    id: uuid.UUID

    class Config:
        from_attributes = True
