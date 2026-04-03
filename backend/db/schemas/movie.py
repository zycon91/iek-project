import uuid
from pydantic import BaseModel
from datetime import date

class MovieImport(BaseModel):
    tmdb_id: int

class MovieSearchResult(BaseModel):
    tmdb_id: int
    title: str
    release_date: str
    description: str
    rating: float

class MovieBase(BaseModel):
    title: str
    duration: int
    description: str
    genre: str
    release_date: date
    rating: int
    rental_price: int = 399
    purchase_price: int = 1499

class MovieCreate(MovieBase):
    pass

class MovieUpdate(BaseModel):
    title: str | None = None
    duration: int | None = None
    description: str | None = None
    genre: str | None = None
    release_date: date | None = None
    rating: int | None = None
    rental_price: int | None = None
    purchase_price: int | None = None

class MovieResponse(MovieBase):
    id: uuid.UUID
    
    class Config:
        from_attributes = True
