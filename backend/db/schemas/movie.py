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

class MovieCreate(MovieBase):
    pass

class MovieUpdate(BaseModel):
    title: str | None = None
    duration: int | None = None
    description: str | None = None
    genre: str | None = None
    release_date: date | None = None
    rating: int | None = None

class MovieResponse(MovieBase):
    id: uuid.UUID
    
    class Config:
        from_attributes = True
