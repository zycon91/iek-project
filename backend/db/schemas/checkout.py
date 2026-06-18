import uuid
from typing import Literal

from pydantic import BaseModel


class CheckoutCreate(BaseModel):
    movie_id: uuid.UUID
    kind: Literal["rental", "purchase"]


class CheckoutResponse(BaseModel):
    checkout_url: str
